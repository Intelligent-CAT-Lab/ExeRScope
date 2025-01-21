import ast
import networkx as nx
import pygraphviz as pgv
import sys
from pycfg import CFGNode as CFGNode
from pycfg import PyCFG as PyCFG
from pycfg import slurp as slurp
from pycfg import get_cfg as get_cfg

"""
Steps:
1. Build CFG
2. Base = E - N + 2*P
3. DFS CFG to add weights for nested code structures (0.5), operators (0.1), comprehension (1).

helpful link: https://pygraphviz.github.io/documentation/stable/reference/agraph.html
"""

class NestingLevelVisitor(ast.NodeVisitor):
    def __init__(self):
        self.nesting_levels = {'if': [], 'for': [], 'while': []}
        self.current_depth = 0

    def generic_visit(self, node):
        if isinstance(node, (ast.If, ast.For, ast.While)):
            # Increase depth for nested 'if', 'for', 'while'
            self.current_depth += 1
            # print(ast.unparse(node))
            self.nesting_levels[node.__class__.__name__.lower()].append(self.current_depth)
            # Visit child nodes
            super().generic_visit(node)
            # Decrease depth after visiting children
            self.current_depth -= 1
        else:
            # Visit child nodes
            super().generic_visit(node)

    def get_nesting_levels(self):
        return self.nesting_levels

class OperatorCounter(ast.NodeVisitor):
    def __init__(self):
        self.binop_count = []
        self.unaryop_count = []
        self.boolop_count = []
        self.compareop_count = []
        self.listcomp_count = []
        self.dictcomp_count = []
        self.setcomp_count = []
        self.gen_count = []
        self.lambda_count = []

    def visit_BinOp(self, node):
        self.binop_count.append(node)
        self.generic_visit(node)
        
    def visit_UnaryOp(self, node):
        self.unaryop_count.append(node)
        self.generic_visit(node)
    
    def visit_BoolOp(self, node):
        self.boolop_count.append(node)
        self.generic_visit(node)

    def visit_Compare(self, node):
        self.compareop_count.append(node)
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
def count_nested_weight(code, nested_weight = 0.5):
    root = ast.parse(code)
    visitor = NestingLevelVisitor()
    visitor.visit(root)
    
    nesting_code_structures = visitor.get_nesting_levels()
    nested_lengths = 0
    for code_structure in nesting_code_structures:
        # print(nesting_code_structures[code_structure])
        nested_lengths += sum(nesting_code_structures[code_structure]) - len(nesting_code_structures[code_structure])
    
    return nested_lengths * nested_weight
        
def count_operators_weight(code, op_weight = 0.1, complex_structures_weight = 0.3, comprehension_weight = 1):
    root = ast.parse(code)
    counter = OperatorCounter()
    counter.visit(root)

    ops = {
        "BinOp": counter.binop_count,
        "UnaryOp": counter.unaryop_count,
        "BoolOp": counter.boolop_count,
        "CompareOp": counter.compareop_count,
        }

    complex_structures = {
        "Lambda": counter.lambda_count,
    }

    comprehension = {
        "ListComp": counter.listcomp_count,
        "DictComp": counter.dictcomp_count,
        "SetComp": counter.setcomp_count,
        "Generator": counter.gen_count
    }

    ops_length = sum(len(op) for op in ops.values())
    ops_weight = op_weight * ops_length

    complex_structures_length =  sum(len(op) for op in complex_structures.values())
    complex_structures_weight = complex_structures_weight * complex_structures_length
    
    comprehension_nums = sum(len(comp) for comp in comprehension.values())
    comprehension_weight = comprehension_weight * comprehension_nums

    weight = ops_weight + complex_structures_weight + comprehension_weight
    return weight
    
def get_CFG(python_file):
    arcs = []
    cfg = PyCFG()
    cfg.gen_cfg(slurp(python_file).strip()) 
    g = CFGNode.to_graph(arcs)
    g.draw(python_file + '.png', prog='dot')
    return g

def read_file(file_path):
    file = open(file_path, 'r')
    content = file.read()
    return content
    
def dfs(graph, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    print("Visiting:", start.attr["label"])  # process the node
    # check_nested_levels(start)
    # print("Neighbors:", [neighbor.attr["label"] for neighbor in graph.neighbors(start) if neighbor not in visited], "\n")
    for next_node in graph[start]:
        if next_node not in visited:
            dfs(graph, next_node, visited)
          
# trailing effects by showing all paths?  
def extract_all_paths(CFG):
    cfg = nx.nx_agraph.from_agraph(CFG)
    start_nodes = [node for node in cfg if cfg.in_degree(node) == 0]
    end_nodes = [node for node in cfg if cfg.out_degree(node) == 0]

    # Extract all paths from start node to each end node
    all_paths = []
    for end_node in end_nodes:
        for start_node in start_nodes:
            paths = list(nx.all_simple_paths(cfg, source=start_node, target=end_node))
            all_paths.extend(paths)

    return all_paths

def main(python_file):
    cfg = get_CFG(python_file)
    cfg_nodes = cfg.nodes()
    cfg_edges = [ edge for edge in cfg.edges() if edge.attr["style"] != "dotted"]

    """get all paths, may use later 
    all_paths = extract_all_paths(cfg)
    for path in all_paths:
            for nodeid in path:
            node = cfg.get_node(nodeid)
            code = node.attr["source_code"]
            print(code)
    """

    # # weights for operators/complex data structures
    # code = read_file(python_file)
    # operators_weight = count_operators_weight(code)
    
    # base complexity for paths
    connected_components = list(nx.strongly_connected_components(cfg))
    base_complexity = len(cfg_edges) - len(cfg_nodes) + 2 * len(connected_components)
    
    # weights for nested levels
    # nested_weight = count_nested_weight(code)  
    
    return base_complexity 
    #+ operators_weight + nested_weight
        
if __name__ == "__main__":
    args = sys.argv[1:]
    python_file = args[0]
    final_value = main(python_file)
    print(final_value)
