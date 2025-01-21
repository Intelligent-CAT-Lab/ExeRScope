import os
import subprocess
import re
import json
from collections import Counter
from tqdm import tqdm
import re

template_cruxeval = """import sys
import trace
from main import f


tracer = trace.Trace(
    ignoredirs=[sys.prefix, sys.exec_prefix],
    trace=1,
    count=0)
tracer.run("$INPUT$")
"""

template_cruxeval_trans = """
import sys
import trace
from transformation import f


tracer = trace.Trace(
    ignoredirs=[sys.prefix, sys.exec_prefix],
    trace=1,
    count=0)
tracer.run("$INPUT$")
"""

template_humaneval_trans = """
import sys
import trace
from transformation import $SIGNATURE$


tracer = trace.Trace(
    ignoredirs=[sys.prefix, sys.exec_prefix],
    trace=1,
    count=0)
tracer.run("$INPUT$")
"""

template_classeval="""
import sys
import trace
$CODE$

tracer = trace.Trace(
    ignoredirs=[sys.prefix, sys.exec_prefix],
    trace=1,
    count=0)
tracer.run('t.test()')
"""

def load_dataset():
    dataset_list = ['humaneval', 'cruxeval', 'classeval', 'avatar']
    return dataset_list

def extract_imports(path):
    code_snippet = open(path, 'r').read()
    pattern = r'^import\s.*$|from\s.*\simport.*$'
    imports = re.findall(pattern, code_snippet, re.MULTILINE)
    return imports

def create_file_cruxeval(transfer=False):
    data_root = "../dataset/cruxeval"
    for d in os.listdir(data_root):
        input_path = os.path.join(data_root, d, 'input.txt')
        input_text = open(input_path, 'r').read().strip("\n")
        code_input = input_text.replace('"', "'")
        if transfer:
            code2write = template_cruxeval_trans.replace("$INPUT$", code_input)
            write_path = os.path.join(data_root, d, 'execution_path_trans.py')            
        else:
            code2write = template_cruxeval.replace("$INPUT$", code_input)
            write_path = os.path.join(data_root, d, 'execution_path.py')
        with open(write_path, 'w') as wr:
            wr.write(code2write)

def create_file_humaneval(transfer=False):
    data_root = "../dataset/humaneval"
    for d in os.listdir(data_root):
        input_path = os.path.join(data_root, d, 'input.txt')
        input_text = open(input_path, 'r').read().strip("\n")
        code_input = input_text.replace('"', "'")
        signature = code_input.split("(")[0].lstrip().rstrip()
        
        if transfer:
            code2write = template_humaneval_trans.replace("$INPUT$", code_input).replace("$SIGNATURE$", signature)
            write_path = os.path.join(data_root, d, 'execution_path_trans.py')          
        else:
            pass
        with open(write_path, 'w') as wr:
            wr.write(code2write)



def create_file_classeval(transfer=False):
    data_root = "../dataset/classeval"
    for d in os.listdir(data_root):
        if transfer:
            write_path = os.path.join(data_root, d, 'execution_path_trans.py')
            code_path = os.path.join(data_root, d, 'transformation.py')
            test_path = os.path.join(data_root, d, "method_test.py")
            code_test = open(test_path, 'r').read()
            if not os.path.exists(code_path):
                continue
            code_text = open(code_path, 'r').read()
            classname = d.split("@")[1].split(".")[0]
            test_case_path = f"/home/changshu/ClassEval/data/benchmark_test_code/{classname}.py"
            imports = "\n".join(extract_imports(test_case_path))
            appended_code = "class Test(unittest.TestCase):\n" + "    " + code_test + "\n" + "t=Test()"
            
            code_text = imports + "\n" + code_text + "\n" + appended_code + "\n"
            
        else:
            write_path = os.path.join(data_root, d, 'execution_path.py')
            code_path = os.path.join(data_root, d, 'run.py')
            code_text = open(code_path, 'r').read()
        code2write = template_classeval.replace("$CODE$", code_text)
        with open(write_path, 'w') as wr:
            wr.write(code2write)

def collect_ll(dataset):
    if dataset == "humaneval":
        create_file_humaneval()
    elif dataset == "cruxeval":
        create_file_cruxeval()
    elif dataset == "classeval":
        create_file_classeval()
    dataroot = f"../dataset/{dataset}"
    execute_tracer(dataroot)
    results = get_loop_length(dataset)
    return results

def execute_tracer(root, transfer=False):
    for d in tqdm(os.listdir(root)):
        if "HumanEval" in d and "__" in d: continue
        if transfer:
            path_tracer = os.path.join(root, d, "execution_path_trans.py")
            path_wr = os.path.join(root, d, 'execution_path_trans.txt')
        else:
            path_tracer = os.path.join(root, d, "execution_path.py")
            path_wr = os.path.join(root, d, 'execution_path.txt')
        if not os.path.exists(path_tracer):
            continue
        try:
            result = subprocess.check_output(f"python {path_tracer} >> {path_wr}", stderr=subprocess.STDOUT, shell=True)
            # with open(path_wr, 'w') as wr:
            #     wr.write(result.decode())
        except:
            print(path_tracer)

def get_loop_length(dataset, transfer=False):
    root = f"../dataset/{dataset}"
    results = {}
    if transfer:
        if dataset in ["humaneval", "cruxeval"]:
            pattern = r"transformation.py\((\d+)\):"
        else:
            pattern = r"execution_path_trans.py\((\d+)\):"
    else:
        if dataset in ['humaneval', 'cruxeval']:
            pattern = r'main.py\((\d+)\):'
        else:
            pattern = r"execution_path.py\((\d+)\):"
    for d in os.listdir(root):
        if "HumanEval" in d and "__" in d: continue
        if transfer:
            exe_path = os.path.join(root, d, 'execution_path_trans.txt')
        else:
            exe_path = os.path.join(root, d, 'execution_path.txt')
        if not os.path.exists(exe_path):
            pass
        else:
            try:
                exe_log = open(exe_path, 'r').read()
                matches = re.findall(pattern, exe_log)
            except:
                print(exe_path)
                continue
        if len(matches) == 0:
            matches.append("1")
        counter = Counter(matches)
        _, frequency = counter.most_common(1)[0]
        results[d] = frequency
    return results



def main():
    dataset_list = load_dataset()
    json_path = f"../Experiment_Results/result_stat/LW/lw.json"
    if os.path.exists(json_path):
        data = json.load(open(json_path, 'r'))
    else:
        data = {}
    
    for d in dataset_list:
        if d in data.keys():
            pass
        else:
            data[d] = collect_ll(d)
    
    with open(json_path, 'w') as wr:
        json.dump(data, wr, indent=4)

if __name__ == "__main__":
    main()

    