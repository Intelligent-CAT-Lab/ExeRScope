import ast
import os
import json

def load_dataset():
    dataset_list = ['humaneval', 'cruxeval', 'classeval', 'Avatar']
    return dataset_list

class NestedLoopDetector(ast.NodeVisitor):
    def __init__(self):
        self.nested_loop_found = False

    def visit_For(self, node):
        # Check for nested loops inside this 'For' loop
        if any(isinstance(child, (ast.For, ast.While)) for child in ast.iter_child_nodes(node)):
            self.nested_loop_found = True
        self.generic_visit(node)  # Continue visiting child nodes

    def visit_While(self, node):
        # Check for nested loops inside this 'While' loop
        if any(isinstance(child, (ast.For, ast.While)) for child in ast.iter_child_nodes(node)):
            self.nested_loop_found = True
        self.generic_visit(node)

def has_nested_loops(code):
    tree = ast.parse(code)
    detector = NestedLoopDetector()
    detector.visit(tree)
    return detector.nested_loop_found

class NestedIfDetector(ast.NodeVisitor):
    def __init__(self):
        self.nested_if_found = False

    def visit_If(self, node):
        # Check if there's a nested 'if' statement within this 'if' statement's body
        if any(isinstance(child, ast.If) for child in ast.iter_child_nodes(node)):
            self.nested_if_found = True
        self.generic_visit(node)  # Continue visiting child nodes

def has_nested_if(code):
    tree = ast.parse(code)
    detector = NestedIfDetector()
    detector.visit(tree)
    return detector.nested_if_found

class UnnestedIfDetector(ast.NodeVisitor):
    def __init__(self):
        self.unnested_if_found = False

    def visit_If(self, node):
        # Check if this 'if' statement has no nested 'if' in its body
        if not any(isinstance(child, ast.If) for child in ast.iter_child_nodes(node)):
            self.unnested_if_found = True
        self.generic_visit(node)  # Continue visiting child nodes

def has_unnested_if(code):
    tree = ast.parse(code)
    detector = UnnestedIfDetector()
    detector.visit(tree)
    return detector.unnested_if_found

class ForLoopDetector(ast.NodeVisitor):
    def __init__(self):
        self.for_loop_found = False

    def visit_For(self, node):
        # If a 'for' loop is found, set the flag to True
        self.for_loop_found = True
        # No need to go further since we found a for loop
        return  # Exit early after finding the first 'for' loop

def has_for_loop(code):
    tree = ast.parse(code)
    detector = ForLoopDetector()
    detector.visit(tree)
    return detector.for_loop_found

class WhileLoopDetector(ast.NodeVisitor):
    def __init__(self):
        self.while_loop_found = False

    def visit_While(self, node):
        # If a 'while' loop is found, set the flag to True
        self.while_loop_found = True
        # No need to go further since we found a while loop
        return  # Exit early after finding the first 'while' loop

def has_while_loop(code):
    tree = ast.parse(code)
    detector = WhileLoopDetector()
    detector.visit(tree)
    return detector.while_loop_found



class TryExceptDetector(ast.NodeVisitor):
    def __init__(self):
        self.try_except_found = False

    def visit_Try(self, node):
        # If a 'try' block is found, set the flag to True
        self.try_except_found = True
        # No need to go further since we found a try-except block
        return  # Exit early after finding the first try-except block

def has_try_except(code):
    tree = ast.parse(code)
    detector = TryExceptDetector()
    detector.visit(tree)
    return detector.try_except_found

def extract_constructs(dataset, transform=False):
    overall_results = {}
    root = f"../dataset/{dataset}"
    for d in os.listdir(root):
        if not transform:
            file_path = os.path.join(root, d, 'main.py')
            code = open(file_path, 'r').read()
        else:
            file_path = os.path.join(root, d, "main.py")
            if not os.path.exists(file_path):
                continue
            code = open(file_path, 'r').read()
        results = {
            "nested": 0,
            "if": 0,
            "for": 0,
            "while": 0,
            "try": 0,
            "switch": 0,
            "basic": 1,
            "nested_if": 0
        }
        if has_nested_loops(code):
            results["nested"] = 1
            results["basic"] = 0
        if has_unnested_if(code):
            results["if"] = 1
            results["basic"] = 0
        if has_for_loop(code):
            results["for"] = 1
            results["basic"] = 0
        if has_while_loop(code):
            results["while"] = 1
            results["basic"] = 0
        if has_try_except(code):
            results["try"] = 1
            results["basic"] = 0
        if has_nested_if(code):
            results["nested_if"] = 1
            results["basic"] = 0
        overall_results[d] = results
    path = f"../Experiment_Results/result_stat/Constructs/{dataset}.json"
    with open(path, 'w') as wr:
        json.dump(overall_results, wr, indent=4)

def main():
    dataset_list = load_dataset()
    for d in dataset_list:
        ## check if data has been collected or not
        construct_path = f"../Experiment_Results/result_stat/Constructs/{d}.json"
        if os.path.exists(construct_path):
            pass
        else:
            extract_constructs(d)

if __name__ == "__main__":
    main()