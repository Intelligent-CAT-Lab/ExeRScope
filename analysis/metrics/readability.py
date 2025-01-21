import ast
import builtins
import os
import sys
import utils
import re
import keyword
import math
from collections import Counter
import nltk
import tokenize
from io import BytesIO
from nltk import word_tokenize
from nltk.corpus import wordnet as wn
from nltk.corpus import words
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import jaccard_score
import numpy as np

try:
    # Try to access the words corpus (it will fail if the corpus hasn't been downloaded yet)
    words.words()
    
except LookupError:
    # If the corpus hasn't been downloaded, download it
    nltk.download('words')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('omw-1.4')
    nltk.download('punkt')

def remove_imports(source_code):
    tree = ast.parse(source_code)
    class ImportRemover(ast.NodeTransformer):
        def visit_Import(self, node):
            return None 

        def visit_ImportFrom(self, node):
            return None 
    transformer = ImportRemover()
    tree = transformer.visit(tree)
    new_source_code = ast.unparse(tree)
    return new_source_code

class LoopCounter(ast.NodeVisitor):
    def __init__(self):
        self.loop_count = 0
        self.loops = []

    def visit_While(self, node):
        self.loop_count += 1
        self.loops.append(ast.unparse(node))
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.loop_count += 1
        self.loops.append(ast.unparse(node))
        self.generic_visit(node)
    
    def visit_ListComp(self, node):
        self.loop_count += len(node.generators)
        self.loops.append(ast.unparse(node.generators))
        self.generic_visit(node)

    def visit_DictComp(self, node):
        self.loop_count += len(node.generators)
        self.loops.append(ast.unparse(node.generators))
        self.generic_visit(node)
    
    def visit_SetComp(self, node):
        self.loop_count += len(node.generators)
        self.loops.append(ast.unparse(node.generators))
        self.generic_visit(node)

    def visit_GeneratorExp(self, node):
        self.loop_count += len(node.generators)
        self.loops.append(ast.unparse(node.generators))
        self.generic_visit(node)

class ConditionCounter(ast.NodeVisitor):
    def __init__(self):
        self.condition_count = 0
        self.conditions = []

    def visit_If(self, node):
        self.condition_count += 1
        self.conditions.append(ast.unparse(node))
        self.generic_visit(node)
    
    def visit_IfExp(self, node):
        self.condition_count += 1
        self.conditions.append(ast.unparse(node))
        self.generic_visit(node)
        
    def visit_comprehension(self, node):
        self.condition_count += len(node.ifs)
        if len(node.ifs):
            self.conditions.append(ast.unparse(node))
        self.generic_visit(node)

class AssignmentCounter(ast.NodeVisitor):
    def __init__(self):
        self.assignment_count = 0
        self.assignments = []

    def visit_Assign(self, node):
        self.assignment_count += 1
        self.assignments.append(ast.unparse(node))
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        self.assignment_count += 1
        self.assignments.append(ast.unparse(node))
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        self.assignment_count += 1
        self.assignments.append(ast.unparse(node))
        self.generic_visit(node)

class LoopNestingCounter(ast.NodeVisitor):
    def __init__(self):
        self.max_nesting_depth = 0
        self.current_depth = 0

    def visit_For(self, node):
        self.current_depth += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_While(self, node):
        self.current_depth += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1
        
class MaxConditionCounter(ast.NodeVisitor):
    def __init__(self):
        self.max_conditions = 0

    def visit_If(self, node):
        conditions_count = self.count_conditions(node.test)
        self.max_conditions = max(self.max_conditions, conditions_count)
        self.generic_visit(node)

    def count_conditions(self, test):
        if isinstance(test, (ast.BoolOp)):
            return sum(self.count_conditions(value) for value in test.values)
        elif isinstance(test, (ast.Compare, ast.Name, ast.Call, ast.Constant)):
            return 1
        elif isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
            return self.count_conditions(test.operand)
        else:
            return 0
        
class IfNestingCounter(ast.NodeVisitor):
    def __init__(self):
        self.max_nesting_depth = 0
        self.current_depth = 0

    def visit_If(self, node):
        self.current_depth += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1
        
class CodeLineCounter(ast.NodeVisitor):
    def __init__(self):
        self.code_lines = set()

    def visit(self, node):
        if hasattr(node, 'lineno'):
            self.code_lines.add(node.lineno)
        self.generic_visit(node)
        
class VariableCounter(ast.NodeVisitor):
    def __init__(self):
        self.variables = set()

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store, ast.AugStore, ast.AnnAssign)):
            self.variables.add(node.id)
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables.add(target.id)
            elif isinstance(target, (ast.Tuple, ast.List)):
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        self.variables.add(elt.id)
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        if isinstance(node.target, ast.Name):
            self.variables.add(node.target.id)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if isinstance(node.target, ast.Name):
            self.variables.add(node.target.id)
        self.generic_visit(node)

class ArrayCounter(ast.NodeVisitor):
    def __init__(self):
        self.array_count = 0
        self.arrays = []

    def visit_List(self, node):
        self.array_count += 1
        self.arrays.append(ast.unparse(node))
        self.generic_visit(node)
        
    def visit_ListComp(self, node):
        self.array_count += 1
        self.arrays.append(ast.unparse(node))
        self.generic_visit(node)

class OperatorCounter(ast.NodeVisitor):
    def __init__(self):
        self.operator_count = 0

    def visit_BinOp(self, node):
        self.operator_count += 1
        self.generic_visit(node)

    def visit_UnaryOp(self, node):
        self.operator_count += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.operator_count += 1
        self.generic_visit(node)

    def visit_Compare(self, node):
        self.operator_count += len(node.ops)
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        self.operator_count += 1
        self.generic_visit(node)
        
class MissingConditionCounter(ast.NodeVisitor):
    def __init__(self):
        self.missing_conditions_count = 0

    def visit_While(self, node):
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            self.missing_conditions_count += 1
        self.generic_visit(node)
        
    def visit_If(self, node):
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            self.missing_conditions_count += 1
        self.generic_visit(node)

# class NestedCastingCounter(ast.NodeVisitor):
#     def __init__(self):
#         self.max_nested_casting = 0
#         self.current_depth = 0

#     def visit_Call(self, node):
#         if isinstance(node.func, ast.Name) and node.func.id in {'int', 'float', 'str', 'bool', 'complex', 'bytes', 'list', 'tuple', 'set', 'dict'}:
#             self.current_depth += 1
#             self.max_nested_casting = max(self.max_nested_casting, self.current_depth)
#             self.generic_visit(node)
#             self.current_depth -= 1
#         else:
#             self.generic_visit(node)

class NestedCastingCounter(ast.NodeVisitor):
    def __init__(self):
        self.nested_casting_count = 0
        self.nested = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in {'int', 'float', 'str', 'bool', 'complex', 'bytes', 'list', 'tuple', 'set', 'dict'}:
            if any(isinstance(arg, ast.Call) for arg in node.args):
                self.nested_casting_count += 1
                self.nested.append(ast.unparse(node))
        self.generic_visit(node)
            
def get_nested_casting(code):
    tree = ast.parse(code)
    counter = NestedCastingCounter()
    counter.visit(tree)
    return counter.nested_casting_count

def get_num_of_missing_conditions(python_code: str) -> int:
    tree = ast.parse(python_code)
    counter = MissingConditionCounter()
    counter.visit(tree)
    return counter.missing_conditions_count
        
def get_num_of_operators(code):
    tree = ast.parse(code)
    counter = OperatorCounter()
    counter.visit(tree)
    return counter.operator_count

def get_num_of_arrays(code):
    tree = ast.parse(code)
    counter = ArrayCounter()
    counter.visit(tree)
    return counter.array_count, counter.arrays

def get_num_of_variables(code):
    tree = ast.parse(code)
    counter = VariableCounter()
    counter.visit(tree)
    return len(counter.variables), counter.variables
        
def get_max_conditions(code):
    tree = ast.parse(code)
    counter = MaxConditionCounter()
    counter.visit(tree)
    return counter.max_conditions

def get_max_nested_loops(code):
    tree = ast.parse(code)
    counter = LoopNestingCounter()
    counter.visit(tree)
    return counter.max_nesting_depth

def get_max_nested_ifs(code):
    tree = ast.parse(code)
    counter = IfNestingCounter()
    counter.visit(tree)
    return counter.max_nesting_depth

def get_max_line_token_length(code):
    lines = code.split('\n')
    max_length = max(tokenize_code(line) for line in lines)
    return max_length

def get_lines_of_code(code):
    tree = ast.parse(code)
    counter = CodeLineCounter()
    counter.visit(tree)
    return len(counter.code_lines)

def tokenize_code(code):
    tokens = word_tokenize(code)
    return len(tokens)

def get_num_of_tokens(code):
    num_tokens = tokenize_code(code)
    return num_tokens

def get_num_of_conditions(code):
    tree = ast.parse(code)
    counter = ConditionCounter()
    counter.visit(tree)
    return counter.condition_count, counter.conditions

def get_num_of_loops(code):
    tree = ast.parse(code)
    counter = LoopCounter()
    counter.visit(tree)
    return counter.loop_count, counter.loops

def get_num_of_assignments(code):
    tree = ast.parse(code)
    counter = AssignmentCounter()
    counter.visit(tree)
    return counter.assignment_count, counter.assignments

def main(python_file):
    code = utils.read_file(python_file)
    metrics_r2i(code)
    metrics_textual(code)
    
def metrics_r2i(code):
    num_tokens = get_num_of_tokens(code)
    num_conditions, conditions = get_num_of_conditions(code)
    num_loops, loops = get_num_of_loops(code)
    num_assignments, assignments = get_num_of_assignments(code)
    num_max_nested_loop = get_max_nested_loops(code)
    num_max_nested_if = get_max_nested_ifs(code)
    num_max_conditions_in_if = get_max_conditions(code)
    max_line_tokens = get_max_line_token_length(code)
    lines_of_code = get_lines_of_code(code)
    num_of_variables, variables = get_num_of_variables(code)
    num_of_arrays, arrays = get_num_of_arrays(code)
    num_of_operators = get_num_of_operators(code)
    num_of_missing_conditions = get_num_of_missing_conditions(code)
    num_of_nested_casting = get_nested_casting(code)
    print("""num_tokens: {}, num_conditions: {}, num_loops: {}, num_assignments: {},
num_max_nested_loop: {}, num_max_nested_if: {}, num_max_conditions_in_if: {}, max_line_tokens: {},
lines_of_code: {}, num_of_variables: {}, num_of_arrays: {}, num_of_operators: {}, 
num_of_missing_conditions: {}, num_of_nested_casting: {}""".format(
        num_tokens, num_conditions, num_loops, num_assignments, num_max_nested_loop,
        num_max_nested_if, num_max_conditions_in_if, max_line_tokens,
        lines_of_code, num_of_variables, num_of_arrays, num_of_operators,
        num_of_missing_conditions, num_of_nested_casting))

def preprocessing(code):
    no_imports_code = remove_imports(code) # remove import nodes
    tokens = remove_non_textual_tokens_from_code(no_imports_code) # Textual tokens
    splited_tokens = split_tokens(tokens) # Split tokens
    filtered_tokens = remove_stop_words(splited_tokens) # Filtered tokens
    stemmed_tokens = apply_porter_stemming(filtered_tokens) # Stemmed tokens
    return stemmed_tokens

def preprocessing_line(code):
    tokens = remove_non_textual_tokens_from_code(code) # Textual tokens
    splited_tokens = split_tokens(tokens) # Split tokens
    filtered_tokens = remove_stop_words(splited_tokens) # Filtered tokens
    stemmed_tokens = apply_porter_stemming(filtered_tokens) # Stemmed tokens
    return stemmed_tokens

def remove_non_textual_tokens_from_code(code):
    # Remove non-textual tokens from the corpora, e.g., operators, special symbols, and programming language keywords;
    tokens = []
    token_stream = tokenize.tokenize(BytesIO(code.encode('utf-8')).readline)
    python_keywords = keyword.kwlist
    for token in token_stream:
        if token.type == tokenize.NAME:
            if token.string not in python_keywords and re.findall(r'\b\w+\b', token.string):
                tokens.append(token.string)
    return tokens

def split_tokens(tokens):
    # Split the remaining tokens into separate words by using the under score or camel case separators; e.g., getText is split into get and text;
    split_tokens = []
    for token in tokens:
        parts = token.split('_')
        for part in parts:
            camel_case_parts = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', part)
            split_tokens.extend(camel_case_parts)
    return split_tokens

def remove_stop_words(tokens):
    # Remove words belonging to a stop-word list (e.g., articles, adverbs) 
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token.lower() not in stop_words]
    return filtered_tokens

def apply_porter_stemming(tokens):
    # Extract stems from words by using the Porter algorithm 
    porter = PorterStemmer()
    stemmed_tokens = [porter.stem(token) for token in tokens]
    return stemmed_tokens

def get_itid(tokens):
    # Identifier Terms in Dictionary (ITID)
    english_words = words.words()
    overlap = [token for token in tokens if token in english_words]
    rate = len(overlap)/len(tokens)
    return rate

def get_nm(tokens):
    # Number of Meanings (NM)
    nm_values = [number_of_meanings(token) for token in tokens]
    if nm_values:
        return max(nm_values), sum(nm_values) / len(nm_values)
    else:
        return 0, 0
    
def number_of_meanings(term):
    synsets = wn.synsets(term)
    return len(synsets)

def extract_identifiers(node):
    identifiers = []
    for child in ast.walk(node):
        if isinstance(child, ast.Name):
            identifiers.append(child.id)
    return identifiers

def extract_blocks(source_code):
    tree = ast.parse(source_code)
    blocks = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.For, ast.While, ast.If, ast.With, ast.Try)):
            block_identifiers = extract_identifiers(node)
            blocks.append(set(block_identifiers))
    return blocks

def vocabulary_overlap(block1, block2):
    return len(block1 & block2) / float(len(block1 | block2))

def get_TC(code):
    # Textual Coherence (TC). the vocabulary overlap between all the possible pairs of distinct syntactic blocks.
    blocks = extract_blocks(code)
    overlaps = []
    num_blocks = len(blocks)
    for i in range(num_blocks):
        for j in range(i + 1, num_blocks):
            overlap = vocabulary_overlap(blocks[i], blocks[j])
            overlaps.append(overlap)
    return {
        'max_overlap': max(overlaps) if overlaps else 0,
        'min_overlap': min(overlaps) if overlaps else 0,
        'average_overlap': sum(overlaps) / len(overlaps) if overlaps else 0
    }
    
def preprocess_line(line):
    tokens = nltk.word_tokenize(line)
    return [token.lower() for token in tokens if token.isalpha()]

def jaccard_similarity(list1, list2):
    set1, set2 = set(list1), set(list2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

def prepare_documents(code_snippet):
    lines = code_snippet.strip().split('\n')
    documents = [preprocess_line(line) for line in lines if line.strip() != '']
    return documents

def compute_jaccard_matrix(documents):
    n = len(documents)
    jaccard_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            jaccard_matrix[i, j] = 1 - jaccard_similarity(documents[i], documents[j])
    return jaccard_matrix
    
def get_noc(code):
    # Number Of Concepts (NOC)
    documents = prepare_documents(code)
    jaccard_matrix = compute_jaccard_matrix(documents)

    # Perform DBSCAN clustering
    dbscan = DBSCAN(metric='precomputed', eps=0.5, min_samples=1)
    clusters = dbscan.fit_predict(jaccard_matrix)

    # Calculate NOC and NOC_norm
    num_clusters = len(set(clusters))
    num_documents = len(documents)
    noc = num_clusters # Number of Concepts (NOC)
    noc_norm = num_clusters / num_documents # Normalized NOC (NOC_norm)

    return noc, noc_norm

def find_particularity(term):
    synsets = wn.synsets(term)
    if not synsets:
        return 0
    # Get the first synset (most common sense)
    synset = synsets[0]
    # Calculate the number of hops to the root hypernym
    hypernym_paths = synset.hypernym_paths()
    if not hypernym_paths:
        return 0
    # Use the shortest path to the root
    shortest_path = min(len(path) for path in hypernym_paths)
    return shortest_path

def get_nmi_line_tokens(line):
    tokens = preprocessing_line(line)
    # Narrow Meaning Identifiers (NMI), summing the "particularity" of each term in a line of code. The "particularity" of a term is defined as the number of hops from the term to the root of its hypernym tree in WordNet.
    particularities = [find_particularity(token) for token in tokens if token.isalpha()]
    return sum(particularities)

def get_nmi_snippet(snippet):
    lines = snippet.strip().split('\n')
    line_nmis = [get_nmi_line_tokens(line) for line in lines]
    total_nmi = sum(line_nmis)
    average_nmi = total_nmi / len(line_nmis) if line_nmis else 0
    return average_nmi

def get_entropy(code):
    tokens = word_tokenize(code)
    # token frequencies
    token_counts = Counter(tokens)
    total_tokens = sum(token_counts.values())
    
    # entropy
    entropy = 0
    for count in token_counts.values():
        probability = count / total_tokens
        entropy -= probability * math.log2(probability)
    
    return entropy

def metrics_textual(code):
    stemmed_tokens = preprocessing(code)
    itid_rate = get_itid(stemmed_tokens)
    max_nm, avg_nm = get_nm(stemmed_tokens)
    tc_res = get_TC(code)
    average_tc = tc_res["average_overlap"]
    noc, noc_norm = get_noc(code)
    nmi = get_nmi_snippet(code)
    entropy = get_entropy(code)
    
    print("""itid_rate: {}, average NM: {}, average_tc: {}, noc_norm: {}, nmi: {}, entropy: {}"""\
        .format(itid_rate, avg_nm, average_tc, noc_norm, nmi, entropy))

if __name__ == "__main__":
    args = sys.argv[1:]
    python_file = args[0]
    main(python_file)
    