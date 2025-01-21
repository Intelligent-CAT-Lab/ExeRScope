# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
import logging
import sys

from tree_sitter import Language, Parser

from .parser import (
    DFG_csharp,
    DFG_go,
    DFG_java,
    DFG_javascript,
    DFG_php,
    DFG_python,
    DFG_ruby,
    DFG_rust,
    index_to_code_token,
    remove_comments_and_docstrings,
    tree_to_token_index,
)
from .utils import get_tree_sitter_language

dfg_function = {
    "python": DFG_python,
    "java": DFG_java,
    "ruby": DFG_ruby,
    "go": DFG_go,
    "php": DFG_php,
    "javascript": DFG_javascript,
    "c_sharp": DFG_csharp,
    "c": DFG_csharp,  # XLCoST uses C# parser for C
    "cpp": DFG_csharp,  # XLCoST uses C# parser for C++
    "rust": DFG_rust,
}


def calc_dataflow_match(references, candidate, lang, langso_so_file):
    return corpus_dataflow_match([references], [candidate], lang, langso_so_file)

def track_operators(code):
    tree_sitter_language = Language("/home/yang/.local/lib/python3.10/site-packages/tree_sitter_languages/languages.so", "python")
    lang = "python"    
    #get_tree_sitter_language(lang)

    parser = Parser()
    parser.set_language(tree_sitter_language)
    # parser.language = tree_sitter_language
    parser = [parser, dfg_function[lang]]
    ast = parser[0].parse(bytes(code, "utf8")).root_node
    depths = []
    def get_all_sub_trees(root_node):
        node_stack = []
        sub_tree_sexp_list = []
        depth = 1
        node_stack.append([root_node, depth])
        while len(node_stack) != 0:
            cur_node, cur_depth = node_stack.pop()
            depths.append(cur_depth)
            sub_tree_sexp_list.append([cur_node, cur_depth])
            # print(code[cur_node.start_byte:cur_node.end_byte])
            # print(cur_node)
            for child_node in cur_node.children:
                if len(child_node.children) != 0:
                    depth = cur_depth + 1
                    node_stack.append([child_node, int(depth)])
        return sub_tree_sexp_list, max(depths)
    
    cand_sexps, max_depth = get_all_sub_trees(ast)
    operators = [] #type=unary_operator, type=binary_operator, type=boolean_operator
    for x in cand_sexps:
        node_type = x[0].type
        node_depth = x[1]
        # print(node_type)
        # print([node_type, node_depth])
        # print(code[x[0].start_byte:x[0].end_byte])
        if node_type in ["unary_operator", "binary_operator", "boolean_operator", "not_operator", "comparison_operator", "augmented_assignment" \
                        #  "for_statement", "if_statement", "while_statement", "assert_statement", \
                         ]:
            # print(x)
            # exit(0)
            operators.append([node_type, node_depth]) # operator type; depth in ast tree
            # print([node_type, node_depth])
            # print(code[x[0].start_byte:x[0].end_byte])
    # exit(0)
    return operators, max_depth


def get_dataflow_for_file(string):
    tree_sitter_language = Language("/home/yang/.local/lib/python3.10/site-packages/tree_sitter_languages/languages.so", "python")
    lang = "python"    
    #get_tree_sitter_language(lang)

    parser = Parser()
    parser.set_language(tree_sitter_language)
    # parser.language = tree_sitter_language
    parser = [parser, dfg_function[lang]]
    try:
        candidate = remove_comments_and_docstrings(string, lang)
    except Exception:
        raise Exception("Error when remove_comments_and_docstrings")

    cand_dfg = get_data_flow(candidate, parser)
    normalized_cand_dfg = normalize_dataflow(cand_dfg)
    # for d in cand_dfg:
    #     print(d)
    # print("done")
    # print(cand_dfg)
    # print(0)
    # print(normalized_cand_dfg)
    return normalized_cand_dfg, cand_dfg

def corpus_dataflow_match(references, candidates, lang, tree_sitter_language=None):
    if not tree_sitter_language:
        tree_sitter_language = Language("/home/yang/.local/lib/python3.10/site-packages/tree_sitter_languages/languages.so", "python")
        #get_tree_sitter_language(lang)

    parser = Parser()
    parser.set_language(tree_sitter_language)
    # parser.language = tree_sitter_language
    parser = [parser, dfg_function[lang]]
    match_count = 0
    total_count = 0

    for i in range(len(candidates)):
        references_sample = references[i]
        candidate = candidates[i]
        for reference in references_sample:
            try:
                candidate = remove_comments_and_docstrings(candidate, lang)
            except Exception:
                pass
            try:
                reference = remove_comments_and_docstrings(reference, lang)
            except Exception:
                pass

            cand_dfg = get_data_flow(candidate, parser)
            ref_dfg = get_data_flow(reference, parser)

            normalized_cand_dfg = normalize_dataflow(cand_dfg)
            normalized_ref_dfg = normalize_dataflow(ref_dfg)

            if len(normalized_ref_dfg) > 0:
                total_count += len(normalized_ref_dfg)
                for dataflow in normalized_ref_dfg:
                    if dataflow in normalized_cand_dfg:
                        match_count += 1
                        normalized_cand_dfg.remove(dataflow)
    if total_count == 0:
        logging.warning(
            "WARNING: There is no reference data-flows extracted from the whole corpus, "
            "and the data-flow match score degenerates to 0. Please consider ignoring this score."
        )
        return 0
    score = match_count / total_count
    return score


def get_data_flow(code, parser):
    try:
        tree = parser[0].parse(bytes(code, "utf8"))
        root_node = tree.root_node
        
        tokens_index = tree_to_token_index(root_node)
        code = code.split("\n")
        code_tokens = [index_to_code_token(x, code) for x in tokens_index]
        index_to_code = {}
        for idx, (index, code) in enumerate(zip(tokens_index, code_tokens)):
            index_to_code[index] = (idx, code)
        try:
            DFG, _ = parser[1](root_node, index_to_code, {})
        except Exception:
            DFG = []
        DFG = sorted(DFG, key=lambda x: x[1])
        indexs = set()
        for d in DFG:
            if len(d[-1]) != 0:
                indexs.add(d[1])
            for x in d[-1]:
                indexs.add(x)
        new_DFG = []
        for d in DFG:
            if d[1] in indexs:
                new_DFG.append(d)
        dfg = new_DFG
    except Exception:
        code.split()
        dfg = []
    # merge nodes
    dic = {}
    for d in dfg:
        if d[1] not in dic:
            dic[d[1]] = d
        else:
            dic[d[1]] = (
                d[0],
                d[1],
                d[2],
                list(set(dic[d[1]][3] + d[3])),
                list(set(dic[d[1]][4] + d[4])),
            )
    DFG = []
    for d in dic:
        DFG.append(dic[d])
    dfg = DFG
    return dfg


def normalize_dataflow_item(dataflow_item):
    var_name = dataflow_item[0]
    dataflow_item[1]
    relationship = dataflow_item[2]
    par_vars_name_list = dataflow_item[3]
    dataflow_item[4]

    var_names = list(set(par_vars_name_list + [var_name]))
    norm_names = {}
    for i in range(len(var_names)):
        norm_names[var_names[i]] = "var_" + str(i)

    norm_var_name = norm_names[var_name]
    relationship = dataflow_item[2]
    norm_par_vars_name_list = [norm_names[x] for x in par_vars_name_list]

    return (norm_var_name, relationship, norm_par_vars_name_list)


def normalize_dataflow(dataflow):
    var_dict = {}
    i = 0
    normalized_dataflow = []
    for item in dataflow:
        var_name = item[0]
        relationship = item[2]
        par_vars_name_list = item[3]
        for name in par_vars_name_list:
            if name not in var_dict:
                var_dict[name] = "var_" + str(i)
                i += 1
        if var_name not in var_dict:
            var_dict[var_name] = "var_" + str(i)
            i += 1
        normalized_dataflow.append(
            (
                var_dict[var_name],
                relationship,
                [var_dict[x] for x in par_vars_name_list],
            )
        )
    return normalized_dataflow

def read_file(file_path):
    file = open(file_path, 'r')
    content = file.read()
    return content

def clear_string(old_string):
    lines = old_string.splitlines()
    stripped_lines = [line.rstrip() for line in lines]
    cleaned_string = "\n".join(stripped_lines)
    return cleaned_string

if __name__ == "__main__":
    file1 = sys.argv[1] 
    content = clear_string(read_file(file1))
    # score = corpus_dataflow_match(references, predictions, lang="python")
    get_dataflow_for_file(content)
    track_operators(content)
