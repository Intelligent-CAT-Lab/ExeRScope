import my_codebleu.codebleu.dataflow_match as dfm
import sys
import utils

def get_dataflow(content):
    normalized_cand_dfg, cand_dfg = dfm.get_dataflow_for_file(content)
    return cand_dfg #normalized_cand_dfg, 

def get_dataflow_file(file):
    content = utils.clear_string(utils.read_file(file))
    return get_dataflow(content)

if __name__ == "__main__":
    file1 = sys.argv[1]
    content = utils.clear_string(utils.read_file(file1))
    for edge in get_dataflow(content):
        print(edge)