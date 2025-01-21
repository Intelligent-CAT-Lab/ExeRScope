#!/usr/bin/env python3
# Code modified and features added by: Yang Chen <yangc9@illinois.edu>
# Original code author: Rahul Gopinath <rahul.gopinath@cispa.saarland>
# License: GPLv3
"""
PyCFG for Python MCI
Use http://viz-js.com/ to view digraph output
"""

import ast
import re
import astunparse
import pygraphviz

class CFGNode(dict):
    registry = 0
    cache = {}
    stack = []
    def __init__(self, parents=[], ast=None, defs=None, uses=None):
        # print(parents)
        # assert type(parents) is list
        self.parents = parents
        self.calls = []
        self.children = []
        self.ast_node = ast
        self.rid  = CFGNode.registry
        self.defs = defs if defs != None else {}
        self.uses = uses if uses != None else {}
        CFGNode.cache[self.rid] = self
        CFGNode.registry += 1

    def end_lineno(self):
        return self.ast_node.end_lineno if hasattr(self.ast_node, 'end_lineno') else 0

    def lineno(self):
        return self.ast_node.lineno if hasattr(self.ast_node, 'lineno') else 0

    def __str__(self):
        return "id:%d line[%d] parents: %s : %s" % (self.rid, self.lineno(), str([p.rid for p in self.parents]), self.source())

    def __repr__(self):
        return str(self)
    
    def get_defs(self):
        return self.defs
    
    def get_uses(self):
        return self.uses

    def add_child(self, c):
        if c not in self.children:
            self.children.append(c)

    def __eq__(self, other):
        return self.rid == other.rid

    def __neq__(self, other):
        return self.rid != other.rid

    def set_parents(self, p):
        self.parents = p

    def add_parent(self, p):
        if p not in self.parents:
            self.parents.append(p)

    def add_parents(self, ps):
        for p in ps:
            self.add_parent(p)

    def add_calls(self, func):
        self.calls.append(func)

    def source(self):
        return astunparse.unparse(self.ast_node).strip()

    def to_json(self):
        return {'id':self.rid, 'parents': [p.rid for p in self.parents], 'children': [c.rid for c in self.children], 'calls': self.calls, 'at':self.lineno() ,'ast':self.source()}

    @classmethod
    def to_graph(cls, arcs=[]):
        def unhack(v):
            for i in ['if', 'while', 'for', 'elif']:
                v = re.sub(r'^_%s:' % i, '%s:' % i, v)
            return v
        G = pygraphviz.AGraph(directed=True)
        cov_lines = set(i for i,j in arcs)
        for nid, cnode in CFGNode.cache.items():
            G.add_node(cnode.rid)
            n = G.get_node(cnode.rid)
            lineno = cnode.lineno()
            end_lineno = cnode.end_lineno()
            node_defs = cnode.get_defs()
            node_uses = cnode.get_uses()
            stat_defs, stat_uses = [], []
            for line in node_defs:
                if line >= lineno and line <= end_lineno:
                    stat_defs.extend(node_defs[line])
            for line in node_uses:
                if line >= lineno and line <= end_lineno:
                    stat_uses.extend(node_uses[line])
            n.attr['stat_defs'] = stat_defs
            n.attr['stat_uses'] = stat_uses
            n.attr['label'] = "%d-%d: %s\n\nDef: %s Use: %s\n\nNode ID: %s" % (lineno,end_lineno, unhack(cnode.source()), stat_defs, stat_uses, nid)
            n.attr['lineno'] = "%d" % (lineno)
            n.attr['end_lineno'] = "%d" % (end_lineno)
            n.attr['source_code'] = "%s" % (unhack(cnode.source()))

            for pn in cnode.parents:
                plineno = pn.lineno()
                # print(pn)
                if hasattr(pn, 'calllink') and pn.calllink > 0 and not hasattr(cnode, 'calleelink'):
                    # print("DOT")
                    # print(pn.rid, cnode.rid)
                    # exit(0)
                    # G.add_edge(pn.rid, cnode.rid, style='dotted', weight=100)
                    continue

                if arcs:
                    if  (plineno, lineno) in arcs:
                        G.add_edge(pn.rid, cnode.rid, color='blue')
                    elif plineno == lineno and lineno in cov_lines:
                        G.add_edge(pn.rid, cnode.rid, color='blue')
                    elif hasattr(cnode, 'fn_exit_node') and plineno in cov_lines:  # child is exit and parent is covered
                        G.add_edge(pn.rid, cnode.rid, color='blue')
                    elif hasattr(pn, 'fn_exit_node') and len(set(n.lineno() for n in pn.parents) | cov_lines) > 0: # parent is exit and one of its parents is covered.
                        G.add_edge(pn.rid, cnode.rid, color='blue')
                    elif plineno in cov_lines and hasattr(cnode, 'calleelink'): # child is a callee (has calleelink) and one of the parents is covered.
                        G.add_edge(pn.rid, cnode.rid, color='blue')
                    else:
                        G.add_edge(pn.rid, cnode.rid, color='red')
                else:
                    G.add_edge(pn.rid, cnode.rid)
                    # print(pn.rid, cnode.rid)
        # print(G.nodes(), len(G.nodes()))
        # print(G.edges(), len(G.edges()))
        return G
    
class VariableUseFinder(ast.NodeVisitor):
    def __init__(self):
        self.used_vars = {}

    def visit_Name(self, node):
        if node.lineno not in self.used_vars:
            self.used_vars[node.lineno] = []
        if isinstance(node.ctx, ast.Load):
            self.used_vars[node.lineno].append(node.id)
        self.generic_visit(node)

    def uses(self):
        return self.used_vars

class VariableDefFinder(ast.NodeVisitor):
    def __init__(self):
        self.def_vars = {}

    def visit_Name(self, node):
        if node.lineno not in self.def_vars:
            self.def_vars[node.lineno] = []
            
        if isinstance(node.ctx, ast.Store):
           self.def_vars[node.lineno].append(node.id)
        self.generic_visit(node)

    def defs(self):
        return self.def_vars
    
def get_def_use(node):
    defs, uses = {}, {}
    defs = get_all_defs(node)
    uses = get_all_uses(node)
    return defs, uses
    
def get_all_uses(node):
    finder = VariableUseFinder()
    finder.visit(node)
    return finder.uses()
    
def get_all_defs(node):
    finder = VariableDefFinder()
    finder.visit(node)
    return finder.defs()

class PyCFG:
    """
    The python CFG
    """
    def __init__(self):
        self.founder = CFGNode(parents=[], ast=ast.parse('start').body[0]) # sentinel
        self.founder.ast_node.lineno = 0
        self.functions = {}
        self.functions_node = {}
        
    def parse(self, src):
        return ast.parse(src)

    def walk(self, node, myparents):
        if node is None: 
            return
        
        fname = "on_%s" % node.__class__.__name__.lower()
        if hasattr(self, fname):
            fn = getattr(self, fname)
            v = fn(node, myparents)
            return v
        else:
            # new_parents = []
            # for child in ast.iter_child_nodes(node):
            #     child_parents = self.walk(child, myparents)
            #     if child_parents:
            #         new_parents.extend(child_parents)
            return myparents
    
    def on_module(self, node, myparents):
        """
        Module(stmt* body)
        """
        # each time a statement is executed unconditionally, make a link from
        # the result to next statement
        p = myparents
        for n in node.body:
            p = self.walk(n, p)
        return p
        
    def on_try(self, node, myparents):
        # Entry node for the try block
        try_entry_node = CFGNode(parents=myparents, ast=node)
        last_nodes = [try_entry_node]

        # Process each statement in the try block
        for stmt in node.body:
            current_nodes = []
            for last_node in last_nodes:
                new_nodes = self.walk(stmt, [last_node])
                if not new_nodes:  # Safety check to prevent empty returns
                    new_nodes = [last_node]  # Default to last node if nothing new
                current_nodes.extend(new_nodes)
            last_nodes = current_nodes  # Update last nodes to the most recently created nodes

        # Nodes for the connection to except and finally blocks
        except_nodes = []

        # Handle each except block
        for handler in node.handlers:
            handler_entry_node = CFGNode(parents=[try_entry_node], ast=handler)
            handler_last_nodes = [handler_entry_node]
            for stmt in handler.body:
                current_nodes = []
                for handler_last_node in handler_last_nodes:
                    new_nodes = self.walk(stmt, [handler_last_node])
                    if not new_nodes:  # Same safety check as above
                        new_nodes = [handler_last_node]
                    current_nodes.extend(new_nodes)
                handler_last_nodes = current_nodes
            except_nodes.extend(handler_last_nodes)

        # Finally block handling
        if node.finalbody:
            finally_entry_node = CFGNode(parents=[try_entry_node] + except_nodes, ast=node.finalbody[0])
            last_finally_nodes = [finally_entry_node]
            for stmt in node.finalbody:
                current_finally_nodes = []
                for last_finally_node in last_finally_nodes:
                    new_nodes = self.walk(stmt, [last_finally_node])
                    if not new_nodes:
                        new_nodes = [last_finally_node]
                    current_finally_nodes.extend(new_nodes)
                last_finally_nodes = current_finally_nodes

            return_nodes = last_nodes + except_nodes + last_finally_nodes
        else:
            return_nodes = last_nodes + except_nodes

        return return_nodes

    def on_assign(self, node, myparents):
        """
        Assign(expr* targets, expr value)
        TODO: AugAssign(expr target, operator op, expr value)
        -- 'simple' indicates that we annotate simple name without parens
        TODO: AnnAssign(expr target, expr annotation, expr? value, int simple)
        """
        # if len(node.targets) > 1: 
        #     print(ast.unparse(node))
        #     raise NotImplemented('Parallel assignments')
        
        defs, uses = get_def_use(node)
        
        # print(ast.unparse(node), ":", defs, uses)        

        p = [CFGNode(parents=myparents, ast=node, defs=defs, uses=uses)]
        p = self.walk(node.value, p)
        return p
    
    def on_augassign(self, node, myparents):
        defs, uses = get_def_use(node)
        p = [CFGNode(parents=myparents, ast=node, defs=defs, uses=uses)]
        p = self.walk(node.value, p)

        return p
    
    def on_annassign(self, node, myparents):
        defs, uses = get_def_use(node)
        p = [CFGNode(parents=myparents, ast=node, defs=defs, uses=uses)]
        p = self.walk(node.value, p)

        return p

    def on_pass(self, node, myparents):
        return [CFGNode(parents=myparents, ast=node)]

    def on_break(self, node, myparents):
        parent = myparents[0]
        while not hasattr(parent, 'exit_nodes'):
            # we have ordered parents
            parent = parent.parents[0]

        assert hasattr(parent, 'exit_nodes')
        p = CFGNode(parents=myparents, ast=node)

        # make the break one of the parents of label node.
        parent.exit_nodes.append(p)

        # break doesnt have immediate children
        return []

    def on_continue(self, node, myparents):
        parent = myparents[0]
        while not hasattr(parent, 'exit_nodes'):
            # we have ordered parents
            parent = parent.parents[0]
        assert hasattr(parent, 'exit_nodes')
        p = CFGNode(parents=myparents, ast=node)

        # make continue one of the parents of the original test node.
        parent.add_parent(p)

        # return the parent because a continue is not the parent
        # for the just next node
        return []

    def on_for(self, node, myparents):
        #node.target in node.iter: node.body

        test_ast = ast.parse('_for: True if %s else False' % astunparse.unparse(node.iter).strip()).body[0]
        defs, uses = get_def_use(node.iter)
        _test_node = CFGNode(parents=myparents, ast=test_ast, defs=defs, uses=uses)
        ast.copy_location(_test_node.ast_node, node)

        # we attach the label node here so that break can find it.
        _test_node.exit_nodes = []
        test_node = self.walk(node.iter, [_test_node])

        extract_ast = ast.parse('%s = %s.shift()' % (astunparse.unparse(node.target).strip(), astunparse.unparse(node.iter).strip())).body[0]
        defs, uses = get_def_use(ast.Assign(targets=node.target, value=node.iter))
        extract_node = CFGNode(parents=[_test_node], ast=extract_ast, defs=defs, uses=uses)
        ast.copy_location(extract_node.ast_node, _test_node.ast_node)

        # now we evaluate the body, one at a time.
        p1 = [extract_node]
        for n in node.body:
            p1 = self.walk(n, p1)

        # the test node is looped back at the end of processing.
        _test_node.add_parents(p1)
        
        else_nodes = []
        if node.orelse:
            else_parent_nodes = [_test_node]
            for n in node.orelse:
                new_else_nodes = self.walk(n, else_parent_nodes)
                else_nodes.extend(new_else_nodes)

        return _test_node.exit_nodes + else_nodes if node.orelse else _test_node.exit_nodes + test_node + else_nodes

    def on_while(self, node, myparents):
        # For a while, the earliest parent is the node.test
        defs, uses = get_def_use(node.test)
        _test_node = CFGNode(parents=myparents, ast=ast.parse('_while: %s' % astunparse.unparse(node.test).strip()).body[0], defs=defs, uses=uses)
        ast.copy_location(_test_node.ast_node, node.test)
        _test_node.exit_nodes = []
        test_node = self.walk(node.test, [_test_node])

        # we attach the label node here so that break can find it.

        # now we evaluate the body, one at a time.
        p1 = test_node
        for n in node.body:
            p1 = self.walk(n, p1)

        # the test node is looped back at the end of processing.
        _test_node.add_parents(p1)
        
        else_nodes = []
        if node.orelse:
            else_parent_nodes = [_test_node]
            for n in node.orelse:
                new_else_nodes = self.walk(n, else_parent_nodes)
                else_nodes.extend(new_else_nodes)

        # link label node back to the condition.
        return _test_node.exit_nodes + else_nodes if node.orelse else _test_node.exit_nodes + test_node  + else_nodes

    def on_if(self, node, myparents):
        defs, uses = get_def_use(node)
        _test_node = CFGNode(parents=myparents, ast=ast.parse('_if: %s' % astunparse.unparse(node.test).strip()).body[0], defs=defs, uses=uses)
        ast.copy_location(_test_node.ast_node, node.test)
        test_node = self.walk(node.test, [_test_node])
        g1 = test_node
        for n in node.body:
            g1 = self.walk(n, g1)
        g2 = test_node
        for n in node.orelse:
            g2 = self.walk(n, g2)

        return g1 + g2

    def on_binop(self, node, myparents):
        left = self.walk(node.left, myparents)
        right = self.walk(node.right, left)
        return right

    def on_compare(self, node, myparents):
        left = self.walk(node.left, myparents)
        right = self.walk(node.comparators[0], left)
        return right

    def on_unaryop(self, node, myparents):
        return self.walk(node.operand, myparents)

    def on_call(self, node, myparents):
        def get_func(node):
            if type(node.func) is ast.Name:
                mid = node.func.id
            elif type(node.func) is ast.Attribute:
                mid = node.func.attr
            elif type(node.func) is ast.Call:
                mid = get_func(node.func)
            else:
                raise Exception(str(type(node.func)))
            return mid
                #mid = node.func.value.id

        p = myparents
        for a in node.args:
            p = self.walk(a, p)
        mid = get_func(node)
        myparents[0].add_calls(mid)

        # these need to be unlinked later if our module actually defines these
        # functions. Otherwsise we may leave them around.
        # during a call, the direct child is not the next
        # statement in text.
        for c in p:
            c.calllink = 0
        return p

    def on_expr(self, node, myparents):
        defs, uses = get_def_use(node)
        p = [CFGNode(parents=myparents, ast=node, defs=defs, uses=uses)]
        return self.walk(node.value, p)

    def on_return(self, node, myparents):
        parent = myparents[0]

        if node.value:
            val_node = self.walk(node.value, myparents)
        else:
            # Create a placeholder node for the implicit 'return None'
            val_node = [CFGNode(parents=myparents, ast=ast.parse('return None').body[0], defs={}, uses={})]

        # on return look back to the function definition.
        while not hasattr(parent, 'return_nodes'):
            parent = parent.parents[0]
        assert hasattr(parent, 'return_nodes')
        
        defs, uses = get_def_use(node)
        p = CFGNode(parents=val_node, ast=node, defs=defs, uses=uses)

        # make the break one of the parents of label node.
        parent.return_nodes.append(p)

        # return doesnt have immediate children
        return []

    def on_functiondef(self, node, myparents):
        # a function definition does not actually continue the thread of
        # control flow
        # name, args, body, decorator_list, returns
        fname = node.name
        args = node.args
        returns = node.returns
        # defs, uses = get_def_use(node)

        enter_node = CFGNode(parents=[], ast=ast.parse('enter: %s(%s)' % (node.name, ', '.join([a.arg for a in node.args.args])) ).body[0]) # sentinel #defs=defs, uses=uses
        enter_node.calleelink = True
        ast.copy_location(enter_node.ast_node, node)
        exit_node = CFGNode(parents=[], ast=ast.parse('exit: %s(%s)' % (node.name, ', '.join([a.arg for a in node.args.args])) ).body[0]) # sentinel #defs=defs, uses=uses
        exit_node.fn_exit_node = True
        ast.copy_location(exit_node.ast_node, node)
        enter_node.return_nodes = [] # sentinel

        p = [enter_node]
        for n in node.body:
            p = self.walk(n, p)

        for n in p:
            if n not in enter_node.return_nodes:
                enter_node.return_nodes.append(n)

        for n in enter_node.return_nodes:
            exit_node.add_parent(n)

        self.functions[fname] = [enter_node, exit_node]
        self.functions_node[enter_node.lineno()] = fname

        return myparents
    
    def on_classdef(self, node, myparents):
        # A class definition does not directly continue the thread of control flow
        class_name = node.name

        # Create entry and exit nodes for the class scope
        enter_node = CFGNode(parents=[], ast=ast.parse('enter: %s' % class_name).body[0])  # Sentinel
        enter_node.calleelink = True  # Treat it like a call
        ast.copy_location(enter_node.ast_node, node)

        exit_node = CFGNode(parents=[], ast=ast.parse('exit: %s' % class_name).body[0])  # Sentinel
        exit_node.fn_exit_node = True  # Mark as exit node
        ast.copy_location(exit_node.ast_node, node)

        # Initialize the container for nodes that are returns from methods
        enter_node.return_nodes = []

        # Walk through class body (methods, attributes, etc.)
        p = [enter_node]
        for n in node.body:
            if isinstance(n, ast.FunctionDef) or isinstance(n, ast.AsyncFunctionDef):
                p = self.walk(n, p)
            else:
                # Handle class variables and other possible statements
                p = self.walk(n, p)

        # Any node not explicitly returning connects to the exit node
        for n in p:
            if n not in enter_node.return_nodes:
                enter_node.return_nodes.append(n)

        # All method return nodes should connect to the class exit node
        for n in enter_node.return_nodes:
            exit_node.add_parent(n)

        # Register the class similarly to how functions are registered (if needed)
        self.functions[class_name] = [enter_node, exit_node]
        self.functions_node[enter_node.lineno()] = class_name

        # Continue with the original flow outside the class definition
        return myparents


    def get_defining_function(self, node):
        if node.lineno() in self.functions_node: return self.functions_node[node.lineno()]
        if not node.parents:
            self.functions_node[node.lineno()] = ''
            return ''
        val = self.get_defining_function(node.parents[0])
        self.functions_node[node.lineno()] = val
        return val

    def link_functions(self):
        for nid,node in CFGNode.cache.items():
            if node.calls:
                for calls in node.calls:
                    if calls in self.functions:
                        enter, exit = self.functions[calls]
                        enter.add_parent(node)
                        if node.children:
                            # # until we link the functions up, the node
                            # # should only have succeeding node in text as
                            # # children.
                            # assert(len(node.children) == 1)
                            # passn = node.children[0]
                            # # We require a single pass statement after every
                            # # call (which means no complex expressions)
                            # assert(type(passn.ast_node) == ast.Pass)

                            # # unlink the call statement
                            assert node.calllink > -1
                            node.calllink += 1
                            for i in node.children:
                                i.add_parent(exit)
                            # passn.set_parents([exit])
                            # ast.copy_location(exit.ast_node, passn.ast_node)


                            # #for c in passn.children: c.add_parent(exit)
                            # #passn.ast_node = exit.ast_node

    def update_functions(self):
        for nid,node in CFGNode.cache.items():
            _n = self.get_defining_function(node)

    def update_children(self):
        for nid,node in CFGNode.cache.items():
            for p in node.parents:
                p.add_child(node)

    def gen_cfg(self, src):
        """
        >>> i = PyCFG()
        >>> i.walk("100")
        5
        """
        node = self.parse(src)
        nodes = self.walk(node, [self.founder])
        self.last_node = CFGNode(parents=nodes, ast=ast.parse('stop').body[0])
        ast.copy_location(self.last_node.ast_node, self.founder.ast_node)
        self.update_children()
        self.update_functions()
        self.link_functions()

def compute_dominator(cfg, start = 0, key='parents'):
    dominator = {}
    dominator[start] = {start}
    all_nodes = set(cfg.keys())
    rem_nodes = all_nodes - {start}
    for n in rem_nodes:
        dominator[n] = all_nodes

    c = True
    while c:
        c = False
        for n in rem_nodes:
            pred_n = cfg[n][key]
            doms = [dominator[p] for p in pred_n]
            i = set.intersection(*doms) if doms else set()
            v = {n} | i
            if dominator[n] != v:
                c = True
            dominator[n] = v
    return dominator

def slurp(f):
    with open(f, 'r') as f: return f.read()


def get_cfg(pythonfile):
    cfg = PyCFG()
    cfg.gen_cfg(slurp(pythonfile).strip())
    cache = CFGNode.cache
    g = {}
    for k,v in cache.items():
        j = v.to_json()
        at = j['at']
        parents_at = [cache[p].to_json()['at'] for p in j['parents']]
        children_at = [cache[c].to_json()['at'] for c in j['children']]
        if at not in g:
            g[at] = {'parents':set(), 'children':set()}
        # remove dummy nodes
        ps = set([p for p in parents_at if p != at])
        cs = set([c for c in children_at if c != at])
        g[at]['parents'] |= ps
        g[at]['children'] |= cs
        if v.calls:
            g[at]['calls'] = v.calls
        g[at]['function'] = cfg.functions_node[v.lineno()]
    return (g, cfg.founder.ast_node.lineno, cfg.last_node.ast_node.lineno)

def compute_flow(pythonfile):
    cfg,first,last = get_cfg(pythonfile)
    return cfg, compute_dominator(cfg, start=first), compute_dominator(cfg, start=last, key='children')

if __name__ == '__main__':
    import json
    import sys
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('pythonfile', help='The python file to be analyzed')
    parser.add_argument('-d','--dots', action='store_true', help='generate a dot file')
    parser.add_argument('-c','--cfg', action='store_true', help='print cfg')
    parser.add_argument('-x','--coverage', action='store', dest='coverage', type=str, help='branch coverage file')
    parser.add_argument('-y','--ccoverage', action='store', dest='ccoverage', type=str, help='custom coverage file')
    args = parser.parse_args()
    if args.dots:
        arcs = None
        if args.coverage:
            cdata = coverage.CoverageData()
            cdata.read_file(filename=args.coverage)
            arcs = [(abs(i),abs(j)) for i,j in cdata.arcs(cdata.measured_files()[0])]
        elif args.ccoverage:
            arcs = [(i,j) for i,j in json.loads(open(args.ccoverage).read())]
        else:
            arcs = []
        cfg = PyCFG()
        cfg.gen_cfg(slurp(args.pythonfile).strip())
        g = CFGNode.to_graph(arcs)
        g.draw(args.pythonfile + '.png', prog='dot')
        # print(g.string(), file=sys.stderr)
        # node index; label is lineno
        
    elif args.cfg:
        cfg,first,last = get_cfg(args.pythonfile)
        for i in sorted(cfg.keys()):
            print(i,'parents:', cfg[i]['parents'], 'children:', cfg[i]['children'])
        print(cfg)