import ast
import utils
import sys
from my_radon.radon.visitors import ComplexityVisitor as ComplexityVisitor
#modification: by default, cyclomatic complexity = 0

def get_cc(file):
    code = utils.read_file(file)
    return get_cc_for_code(code)

def get_cc_for_code(code):
    visitor = ComplexityVisitor(off=False).from_code(code)
    return visitor.total_complexity

if __name__ == "__main__":
    file = sys.argv[1]
    print(get_cc(file))