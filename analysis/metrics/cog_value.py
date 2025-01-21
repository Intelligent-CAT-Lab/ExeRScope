import ast
import sys
import utils
from my_cognitive_complexity.cognitive_complexity.api import get_cognitive_complexity
from my_cognitive_complexity.cognitive_complexity.api import get_cognitive_complexity_for_node
#modification: add comprehension

def get_cog(file): 
    code = utils.read_file(file)
    root = ast.parse(code)
    total_cog = 0
    for node in ast.iter_child_nodes(root):
        current_cog = 0
        if isinstance(node, ast.FunctionDef):
            current_cog = get_cognitive_complexity(node)
        else:
            current_cog = get_cognitive_complexity_for_node(node)
        total_cog += current_cog
        if current_cog:
            print(ast.unparse(node))
            print(current_cog)
            
        # print(ast.dump(node))
        # print(current_cog)
    return total_cog

def get_cog_for_code(code):
    root = ast.parse(code)
    total_cog = 0
    for node in ast.iter_child_nodes(root):
        current_cog = 0
        if isinstance(node, ast.FunctionDef):
            current_cog = get_cognitive_complexity(node)
        else:
            current_cog = get_cognitive_complexity_for_node(node)
        total_cog += current_cog
        # print(current_cog)
        # print(ast.unparse(node))
    return total_cog

if __name__ == "__main__":
    file = sys.argv[1]
    print(get_cog(file))