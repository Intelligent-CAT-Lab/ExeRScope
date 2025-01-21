import ast
import os
import sys
import shutil
import networkx as nx
import pkg_resources
import pygraphviz as pgv
from def_use import get_def_use as get_def_use
# from get_nested import get_nested as get_nested
from pycfg import CFGNode
from pycfg import PyCFG
from pycfg import slurp as slurp
# from pycfg import get_cfg as get_cfg
from stdlib_list import stdlib_list
from utils import write_file
from utils import write_dict_csv
import astunparse

import graphviz
from py2cfgPlus.py2cfgPlus.builder import CFGBuilder

"""
Reproduction:
1. Reproduce APR tasks with new models.
"""

"""
TODO: 
1. correlation analysis for different/my metrics and translation failures; in papers;
2. read the paper
3. different weights for operators/comprehension/nested code structures/... 
   (sensitivity analysis for different values)
4. [bad transformation] on good/bad translations seperately 
 
Steps:
1. Build CFG, AST
2. Base = E - N + 2*P 
3. Search AST to add weights for nested code structures (0.5), operators (0.1), comprehension (1); 
We should not DFS CFG for this step, because the nested structures are not distinguished with sequential statements in CFG.
for: 1 + (nesting level - 1) * 0.5 (?)
4. Add dataflow (uses of variables).

helpful link: https://pygraphviz.github.io/documentation/stable/reference/agraph.html
"""

class PredicateOperatorChecker(ast.NodeVisitor):
    def __init__(self):
        self.predicates_with_operators = []

    def check_operators_in_predicate(self, predicate):
        # Helper function to detect operator nodes in predicates
        if isinstance(predicate, list):
            for pred in predicate:
                self.check_operators_in_predicate(pred)  # Recursive call for each condition
        else:
            for node in ast.walk(predicate):
                if isinstance(node, (ast.BoolOp, ast.Compare, ast.BinOp, ast.UnaryOp)):
                    self.predicates_with_operators.append(astunparse.unparse(predicate))
                    break

    def visit_If(self, node):
        self.check_operators_in_predicate(node.test)
        self.generic_visit(node)

    def visit_While(self, node):
        self.check_operators_in_predicate(node.test)
        self.generic_visit(node)

    def visit_ListComp(self, node):
        for generator in node.generators:
            self.check_operators_in_predicate(generator.ifs)
        self.generic_visit(node)

    def visit_DictComp(self, node):
        for generator in node.generators:
            self.check_operators_in_predicate(generator.ifs)
        self.generic_visit(node)
    
    def visit_SetComp(self, node):
        for generator in node.generators:
            self.check_operators_in_predicate(generator.ifs)
        self.generic_visit(node)
    
    def visit_GeneratorExp(self, node):
        for generator in node.generators:
            self.check_operators_in_predicate(generator.ifs)
        self.generic_visit(node)
    
    def visit_Lambda(self, node):
        if isinstance(node.body, ast.Compare) or isinstance(node.body, ast.BoolOp):
            self.check_operators_in_predicate(node.body)
        self.generic_visit(node)
    
    def visit_Call(self, node):
        # `any()`, `all()`, `filter()`
        if isinstance(node.func, ast.Name):
            if node.func.id in ['any', 'all', 'range']:
                for arg in node.args:
                    self.check_operators_in_predicate(arg)
        # no need to consider `filter()`, because the condition in `filter()` 
        # will either be considered in lambda, or in normal functions
        # elif isinstance(node.func, ast.Name) and node.func.id == 'filter':
        #     if len(node.args) > 1 and not isinstance(node.args[0], ast.Lambda):
        #         self.predicates.append(ast.unparse(node.args[0]))
        self.generic_visit(node)

class NestingLevelVisitor(ast.NodeVisitor):
    def __init__(self):
        self.nesting_info = {'If': [], 'For': [], 'While': []}
        self.nested_code = {'If': [], 'For': [], 'While': []}
        self.current_depth = 0
        self.parent = None
    
    def add_parents(self, node, parent=None):
        for child in ast.iter_child_nodes(node):
            child.parent = node
            self.add_parents(child, node)

    def generic_visit(self, node):
        self.add_parents(node)
        if isinstance(node, (ast.If, ast.For, ast.While)) and not self.is_elif(node):
            self.current_depth += 1
            self.nesting_info[type(node).__name__].append(self.current_depth)
            if self.current_depth > 1:
                self.nested_code[type(node).__name__].append(astunparse.unparse(node))
        super().generic_visit(node)
        if isinstance(node, (ast.If, ast.For, ast.While)) and not self.is_elif(node):
            self.current_depth -= 1

    def is_elif(self, node):
        return (isinstance(node, ast.If) and isinstance(node.parent, ast.If) and 
                isinstance(getattr(node.parent, 'orelse', []), list) and len(node.parent.orelse) and
                node == node.parent.orelse[0])

    def get_nesting_info(self):
        return self.nesting_info
    
    def get_nesting_code(self):
        return self.nested_code
    
class ImportCollector(ast.NodeVisitor):
    def __init__(self):
        self.imports = []
        self.fromimport_module_map = {}
        self.custom_defined_funcs = []

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name not in self.imports:
                self.imports.append(alias.name)
            if alias.asname and alias.asname not in self.imports:
                self.imports.append(alias.asname)
                self.fromimport_module_map[alias.asname] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module_name = node.module
        for alias in node.names:
            if alias.name not in self.imports:
                self.imports.append(alias.name)
                self.fromimport_module_map[alias.name] = module_name.split(".")[0]
            if alias.asname and alias.asname not in self.imports:
                self.imports.append(alias.asname)
                self.fromimport_module_map[alias.asname] = module_name.split(".")[0]
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        self.custom_defined_funcs.append(node.name)
        self.generic_visit(node)

class APICallExtractor(ast.NodeVisitor):
    def __init__(self, imports, fromimport_module_map, custom_defined_funcs):
        self.imports = imports
        self.fromimport_module_map = fromimport_module_map
        self.custom_defined_funcs = custom_defined_funcs
        self.standard_api_calls = []
        self.third_party_calls = []
        self.inter_dependencies = []
        self.intra_dependencies = []
        self.enumerate_count = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            module_name = self.resolve_module_name(node.func.value)
            if module_name == "self":
                module_name = node.func.attr
            if module_name and module_name in self.imports:
                if self.is_third_party(module_name) or self.is_standard_library(module_name)\
                    or self.is_third_party(self.get_module_fromimport(module_name)) or \
                        self.is_standard_library(self.get_module_fromimport(module_name)):
                    self.third_party_calls.append(astunparse.unparse(node))
                else:
                    self.inter_dependencies.append(astunparse.unparse(node))
            elif module_name and module_name in self.custom_defined_funcs:
                self.intra_dependencies.append(astunparse.unparse(node))
        elif isinstance(node.func, ast.Name) and node.func.id == 'enumerate':
            self.enumerate_count.append(node)
        elif isinstance(node.func, ast.Name):
            if node.func.id in self.imports:
                if self.is_third_party(node.func.id) or self.is_standard_library(node.func.id):
                    self.third_party_calls.append(astunparse.unparse(node))
                else:
                    module_name = self.get_module_fromimport(node.func.id)
                    if module_name:
                        if self.is_third_party(module_name) or self.is_standard_library(module_name):
                            self.third_party_calls.append(astunparse.unparse(node))
                        else:
                            self.inter_dependencies.append(astunparse.unparse(node))
                    else:
                        self.inter_dependencies.append(astunparse.unparse(node))
            elif node.func.id in self.custom_defined_funcs:
                self.intra_dependencies.append(astunparse.unparse(node))
        self.generic_visit(node)

    def resolve_module_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self.resolve_module_name(node.value)
        
    def get_module_fromimport(self, node_func_id):
        if node_func_id in self.fromimport_module_map:
            return self.fromimport_module_map[node_func_id]
        
    def is_standard_library(self, module_name):
        libraries = stdlib_list()
        return module_name in libraries
    
    def is_third_party(self, module_name):
        templates = {"PIL": "pillow", "dateutil": "python-dateutil", "sklearn": "scikit-learn"}
        installed_packages = {pkg.key for pkg in pkg_resources.working_set}
        if module_name in installed_packages and not self.is_standard_library(module_name):
            return True
        elif module_name.lower() in installed_packages and not self.is_standard_library(module_name):
            return True
        elif module_name.upper() in installed_packages and not self.is_standard_library(module_name):
            return True
        if module_name in templates:
            return self.is_third_party(templates[module_name])
        else:
            return False
        
            
def extract_third_party_api_calls(code):
    tree = ast.parse(code)
    
    import_collector = ImportCollector()
    import_collector.visit(tree)
    
    extractor = APICallExtractor(import_collector.imports, import_collector.fromimport_module_map, import_collector.custom_defined_funcs)
    extractor.visit(tree)
    return extractor.third_party_calls, extractor.inter_dependencies, extractor.intra_dependencies

class ComplexCodeStructureCounter(ast.NodeVisitor):
    def __init__(self):
        self.current_function = None
        self.listcomp_count = []
        self.dictcomp_count = []
        self.setcomp_count = []
        self.gen_count = []
        self.lambda_count = []
        self.lists = []
        self.thread = []
        self.recursive_functions = []
        self.decorator = []
        
    def visit_ClassDef(self, node):
        if len(node.decorator_list) > 0:
            self.decorator.extend(node.decorator_list)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        self.current_function = node.name
        if len(node.decorator_list) > 0:
            self.decorator.extend(node.decorator_list)
        self.generic_visit(node)
        self.current_function = None

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'Thread':
                self.thread.append(node)
        elif isinstance(node.func, ast.Name):
            if node.func.id == self.current_function:
                if self.current_function not in self.recursive_functions:
                    self.recursive_functions.append(self.current_function)
            
        # if node.decorator_list:
        #     self.decorator.append(node)
        self.generic_visit(node)
        
    def visit_List(self, node):
        self.lists.append(node)
        self.generic_visit(node)

    def visit_ListComp(self, node):
        self.listcomp_count.append(node)
        self.generic_visit(node)

    def visit_DictComp(self, node):
        self.dictcomp_count.append(node)
        self.generic_visit(node)

    def visit_SetComp(self, node):
        self.setcomp_count.append(node)
        self.generic_visit(node)
        
    def visit_GeneratorExp(self, node):
        self.gen_count.append(node)
        self.generic_visit(node)

    def visit_Lambda(self, node):
        self.lambda_count.append(node)
        self.generic_visit(node)
        
# nested. how about consectuative code structures in control flow?
def count_nested_weight(code, nested_weight = 1):
    root = ast.parse(code)
    visitor = NestingLevelVisitor()
    visitor.visit(root)
    
    nested_code_structures = visitor.get_nesting_info()
    nested_code_stats = visitor.get_nesting_code()
    nested_lengths = 0
    for code_structure in nested_code_structures:
        nested_lengths += sum(nested_code_structures[code_structure]) - len(nested_code_structures[code_structure])
    
    return nested_lengths * nested_weight, nested_code_structures, nested_code_stats

def check_predicates_for_operators(code):
    tree = ast.parse(code)
    checker = PredicateOperatorChecker()
    checker.visit(tree)
    return checker.predicates_with_operators
        
def complex_constructs_weight(code, complex_structures_weight = 2, comprehension_weight = 1):
    root = ast.parse(code)
    counter = ComplexCodeStructureCounter()
    counter.visit(root)

    # To add "str(cookies[1]) if takahashi > 0 else str(max(0, cookies[1] - abs(leftOver)))"
    complex_structures = {
        "Lambda": counter.lambda_count,
        "thread" : counter.thread,
        "recursive_functions": counter.recursive_functions,
        "decorator": counter.decorator,
        # "enumerate": counter.enumerate_count
    }

    comprehension = {
        "ListComp": counter.listcomp_count,
        "DictComp": counter.dictcomp_count,
        "SetComp": counter.setcomp_count,
        "Generator": counter.gen_count,
        "list": counter.lists,
    }

    complex_structures_length =  sum(len(op) for op in complex_structures.values())
    complex_structures_weight = complex_structures_weight * complex_structures_length
    
    comprehension_nums = sum(len(comp) for comp in comprehension.values())
    comprehension_weight = comprehension_weight * comprehension_nums

    code_structure_weight = complex_structures_weight + comprehension_weight
    return code_structure_weight, complex_structures, comprehension

def move_and_rename_file(src_file, dest_dir, new_file_name):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    if os.path.exists(src_file):
        dest_file = os.path.join(dest_dir, new_file_name)
        shutil.move(src_file, dest_file)
    
def get_CFG(python_file, dest_dir):
    png_path = 'CFG'+python_file.split("/")[-1]+".png"
    try:
        arcs = []
        py_cfg = PyCFG()
        py_cfg.gen_cfg(slurp(python_file).strip()) 
        cfg = CFGNode.to_graph(arcs)
        cfg.draw(png_path, prog='dot')
        cfg_nodes = cfg.nodes()
        cfg_edges = [edge for edge in cfg.edges() if edge.attr["style"] != "dotted"]
         # base complexity for paths
        connected_components = list(nx.strongly_connected_components(cfg))
        filtered_connected_components = connected_components
        for component in connected_components:
            tag = []
            start = None
            stop = None
            if len(component) == 2:
                g = list(component)
                tag.append(g[0].attr["source_code"])
                tag.append(g[1].attr["source_code"])
            if "stop" in tag and "start" in tag:
                if g[0].attr["source_code"] == "start":
                    start = g[0]
                    stop = g[1]
                elif g[1].attr["source_code"] == "start":
                    start = g[1]
                    stop = g[0]
                filtered_connected_components.remove(component)
                G = nx.nx_agraph.from_agraph(cfg)
                cfg_nodes.remove(g[0])
                cfg_nodes.remove(g[1])
                edge = tuple(nx.shortest_path(G, start, stop))
                cfg_edges.remove(edge)
        move_and_rename_file(png_path, dest_dir, python_file.split('/')[-1] + ".png")
        move_and_rename_file(png_path + ".dot", dest_dir, python_file.split('/')[-1] + ".dot")
        move_and_rename_file(png_path + ".png", dest_dir, python_file.split('/')[-1] + ".png")
        return len(cfg_nodes), len(cfg_edges), len(filtered_connected_components)
    except:
        cfg_builder = CFGBuilder()
        cfg = cfg_builder.build_from_file(png_path, python_file)
        cfg.build_visual(png_path, 'dot')
        cfg.build_visual(png_path, 'png')
        G = pgv.AGraph(f"{png_path}.dot")
        nx_graph = nx.nx_agraph.from_agraph(G)
        nodes = list(nx_graph.nodes())
        edges = list(nx_graph.edges())
        connected_components = list(nx.weakly_connected_components(nx_graph))
        # print(len(nodes), len(edges), len(connected_components))
        move_and_rename_file(png_path, dest_dir, python_file.split('/')[-1] + ".png")
        move_and_rename_file(png_path + ".dot", dest_dir, python_file.split('/')[-1] + ".dot")
        move_and_rename_file(png_path + ".png", dest_dir, python_file.split('/')[-1] + ".png")
        return len(nodes), len(edges), len(connected_components)


def read_file(file_path):
    file = open(file_path, 'r')
    content = file.read()
    return content
    
def dfs(graph, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    for next_node in graph[start]:
        if next_node not in visited:
            dfs(graph, next_node, visited)

def dfs_all_paths(graph, start, end, path=None):
    if path is None:
        path = [start]

    if start == end:
        return [path]

    if start not in graph:
        return []

    paths = []
    for node in graph[start]:
        if node not in path or node == end:  # Allow revisiting 'End'
            new_paths = dfs_all_paths(graph, node, end, path + [node])
            for new_path in new_paths:
                paths.append(new_path)

    return paths
          
def extend_paths_through_cycle(paths, cycle_nodes, G, end):
    # Extend each path through the cycle exactly once
    extended_paths = []
    for path in paths:
        last_node = path[-1]
        # Find all simple paths through the cycle starting from the last node
        for cycle_start in cycle_nodes:
            if G.has_edge(last_node, cycle_start):
                for path_through_cycle in nx.all_simple_paths(G, cycle_start, cycle_start):
                    # Now extend to the end node from the cycle start
                    for continuation_path in nx.all_simple_paths(G, cycle_start, end):
                        new_path = path[:-1] + path_through_cycle + continuation_path[1:]
                        extended_paths.append(new_path)
    return extended_paths

def remove_duplicates(lst):
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result

# trailing effects by showing all paths?  
def extract_all_paths(CFG):
    cfg = nx.nx_agraph.from_agraph(CFG)
    start_nodes = [node for node in cfg if cfg.in_degree(node) == 0]
    end_nodes = [node for node in cfg if cfg.out_degree(node) == 0]

    # first get all cycles
    cycles = sorted(nx.simple_cycles(cfg))
    
    all_paths = []
    
    # paths with cycles, to build the all paths, assuming only execute all loops for once
    for unsorted_cycle in cycles:
        cycle = sorted(unsorted_cycle, key=int)
        cycle_start = cycle[0]
        cycle_end = cycle[-1]
        start_to_cycle_paths = []
        cycle_to_end_paths = []
        for start_node in start_nodes:
            start_to_cycle_paths.extend(nx.all_simple_paths(cfg, start_node, cycle_start))
        for end_node in end_nodes:
            cycle_to_end_paths.extend(nx.all_simple_paths(cfg, cycle_start, end_node))
            
        for start_to_cycle_path in start_to_cycle_paths:
            for cycle_to_end_path in cycle_to_end_paths:
                unsorted_path = start_to_cycle_path + cycle + cycle_to_end_path
                path = remove_duplicates(unsorted_path)
                # path = [sorted(list(set(unsorted_path)), key=int)]
                if path not in all_paths:
                    all_paths.append(path)
                
    # paths without loops(cycles)
    for end_node in end_nodes:
        for start_node in start_nodes:
            paths = list(nx.all_simple_paths(cfg, start_node, end_node))
            if paths:
                for path in paths:
                    if path not in all_paths:
                        all_paths.append(path)
    return all_paths

def count_def_use(code):
    total_uses = []
    chains = get_def_use(code)
    for var in chains:
        total_uses.extend(chains[var])
    uses = sum(total_uses)
    return uses

def get_def_live_lengths(all_paths, cfg):
    def_live_lengths = {}
    path_id = 0
    for path in all_paths:
        if path_id not in def_live_lengths:
            def_live_lengths[path_id] = {}
        for nodeid in path:
            node = cfg.get_node(nodeid)
            code = node.attr["source_code"]
            defs = ast.literal_eval(node.attr["stat_defs"])
            uses = ast.literal_eval(node.attr["stat_uses"])
            
            for def_id in defs: # TODO: distinguish defs with function name
                if def_id == "_":
                    continue
                if def_id not in def_live_lengths[path_id]:
                    def_live_lengths[path_id][def_id] = []
                if node not in def_live_lengths[path_id][def_id]:
                    def_live_lengths[path_id][def_id].append(node)
            for use_id in uses:
                if use_id not in def_live_lengths[path_id]:
                    continue
                if node not in def_live_lengths[path_id][use_id]:
                    def_live_lengths[path_id][use_id].append(node)
                
        path_id += 1
    var_live_pairs = {}
    
    for path_id in def_live_lengths:
        for var in def_live_lengths[path_id]:
            if var not in var_live_pairs:
                var_live_pairs[var] = {}
            if path_id not in var_live_pairs[var]:
                var_live_pairs[var][path_id] = []
            all_nodes = def_live_lengths[path_id][var]
            pairs = [(start, end) for start, end in zip(all_nodes, all_nodes[1:])]
            for (start, end) in pairs:
                if (start, end) not in var_live_pairs[var][path_id]:
                    var_live_pairs[var][path_id].append((start, end))
    max_var_distance = {}
    
    # get the max length of paths between two def-use/use-use for each variable
    cfg_nx = nx.nx_agraph.from_agraph(cfg)
    for var in var_live_pairs:
        if var not in max_var_distance:
            max_var_distance[var] = []
        for path_id in var_live_pairs[var]:
            for (start, end) in var_live_pairs[var][path_id]:
                # paths = list(nx.all_simple_paths(cfg_nx, start, end))
                path = all_paths[path_id][all_paths[path_id].index(start):all_paths[path_id].index(end)+1]
                if len(path) > len(max_var_distance[var]):
                    max_var_distance[var] = path
    
    return def_live_lengths, max_var_distance

def main(python_file, save_dir, save_to_csv, piB=1, piOp=1, piN=1, piD=1, piC = 1, piT = 1):
    
    code = read_file(python_file)
    if code == "":
        raise Exception("Python file {} is empty.".format(python_file))
    
    NumNodes, NumEdges, NumIslands = get_CFG(python_file, save_dir)
        
    # base complexity
    base_complexity = NumEdges - NumNodes + 2 * NumIslands
    
    code_structure_weight, complex_structures, comprehension = complex_constructs_weight(code)
    third_party_calls, inter_dependencies, intra_dependencies = extract_third_party_api_calls(code)
    
    third_party_calls_weight = len(third_party_calls)
    inter_dependencies_weight = len(inter_dependencies)
    intra_dependencies_weight = len(intra_dependencies)
    
    predicates_with_operators = check_predicates_for_operators(code)
    predicates_with_operators_weight = len(predicates_with_operators)

    # weights for nested levels
    nested_weight, nested_code_structures, nested_code_stats = count_nested_weight(code)  
    
    
    log_path = os.path.join(save_dir, python_file.replace("/", "_") + ".log")
    
    
    log_content = \
        """
        Edges: {}, Nodes: {},  Islands: {},
        Predicates with operators: {}
        Nesting levels of code structures (N>1): {}\n{}
        Complex code structures: {}, comprehension: {},
        Third-party calls: {}, Inter_dependencies: {}, Intra_dependencies: {}, 
        Base complexity: {}, Predicates with operators: {}, Nested levels: {}, Complex code structures: {}, Third-Party calls: {}, Inter_dependencies: {}, Intra_dependencies: {}
        """.format(NumEdges, NumNodes, NumIslands,
            predicates_with_operators,
            nested_code_structures, nested_code_stats,
            # max_var_distance,
            complex_structures,comprehension,
            third_party_calls, inter_dependencies, intra_dependencies,
            base_complexity, predicates_with_operators_weight, nested_weight, 
            # def_uses, def_uses_avg, 
            code_structure_weight, third_party_calls_weight, inter_dependencies_weight, intra_dependencies_weight, 
            # final_value
            )
    write_file(log_path, log_content)
    results = {
        "File": python_file, 
        "Base complexity": base_complexity, 
        "Predicates with operators": predicates_with_operators_weight, 
        "Nested levels": nested_weight, 
        # "Variable max distance (sum)": def_uses, 
        # "Variable max distance (average)": def_uses_avg,
        "Complex code structures": code_structure_weight, 
        "Third-Party calls": third_party_calls_weight, 
        "Inter_dependencies": inter_dependencies_weight, 
        "Intra_dependencies": intra_dependencies_weight,  
        # "Final value": final_value, 
        "Log": log_path 
    }
    headers = list(results.keys())
    write_dict_csv(save_to_csv, headers, results)
    # print(results)
    return results

if __name__ == "__main__":
    args = sys.argv[1:]
    python_file = args[0]
    save_dir = args[1]
    save_to_csv = args[2]
    final_value = main(python_file, save_dir, save_to_csv, piB=1, piN=1, piOp=1, piD=1, piC=1, piT=1)
