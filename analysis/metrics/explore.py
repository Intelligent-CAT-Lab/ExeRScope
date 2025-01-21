import csv
import os
import sys
import cog_value
import cc_value
import dataflow
import operators
import count_ops
import utils
import def_use
import numpy as np
import scipy.stats as stats

"""python3 explore.py ../../dataset/python_codenet ../../dataset/python_codenet \
    success.csv(../../94.csv) unsuccess.csv(../../61.csv) save_to_dir (statistics/codenet)
"""

def read_file(file_path):
    file = open(file_path, 'r')
    content = file.read()
    return content

def clear_string(old_string):
    lines = old_string.splitlines()
    stripped_lines = [line.rstrip() for line in lines]
    cleaned_string = "\n".join(stripped_lines)
    return cleaned_string

def get_program(file_dir, file_list):
    file_list = [item for item in read_file(file_list).split("\n") if item]
    program_list = []
    for dirpath, _, files in os.walk(file_dir):
        for file in files:
            file_id = file.split(".")[0]
            if file_id in file_list and file.endswith(".py"):
                file_path = os.path.join(dirpath, file)
                program_list.append([file_path, file_id])
    return program_list

def generate_data(program_list):
    results = {}
    for item in program_list:
        file = item[0]
        file_id = item[1]
        program = clear_string(read_file(file))
        cog = cog_value.get_cog_for_code(program)
        cc = cc_value.get_cc_for_code(program)
        df = len(dataflow.get_dataflow(program))
        
        def_use_chain = def_use.get_def_use(program)
        total_defs = len(def_use_chain.keys())
        total_uses = sum(def_use_chain.values())
        max_use = max(def_use_chain.values()) if len(def_use_chain.values()) else 0
        avg_use =  0 if total_defs ==0 else total_uses/total_defs
        zero_use = len([use for use in def_use_chain.values() if use == 0])
        # print(zero_use, avg_use, max_use )
        # print(def_use_chain, total_defs, total_uses, avg_def_use_chains)
        # print(program)
        # for i in dataflow.get_dataflow(program): 
        #     print(i)
        op_levels, max_ast_length = operators.get_operators_dict(program)
        depths = operators.get_operators_depths(program)
        all_operators, all_operands = count_ops.count_detailed_operators_and_operands(program)
        
        total_operators_num = sum(op_levels.values())
        operators_types = len(op_levels)
        total_operands_num = sum(all_operands.values())
        unique_operands_num = len(all_operands)
        
        if file_id not in results:
            results[file_id] = {
                "file_id": file_id,
                "cognitive complexity": cog,
                "cyclomatic complexity": cc,
                "dataflow edges": df,
                "total_operators_num": total_operators_num,
                "operator types": operators_types,
                "different operators levels": len(op_levels),
                "total_operands_num": total_operands_num,
                "unique_operands_num": unique_operands_num,
                # "operator depths": depths,
                "different levels of operator depths": len(list(set(depths))),
                "max_ast_length": max_ast_length,
                "total_defs": total_defs,
                "total_uses": total_uses,
                "max_use": max_use,
                "avg_use": round(avg_use, 2),
                "zero_use": zero_use
            }
    return results

def save_to_csv(csv_path, result_dict):
    for program in result_dict:
        fields = [key for key in result_dict[program].keys()]
        break
    utils.write_header_csv(csv_path, fields)
    for item in result_dict:
        utils.write_dict_csv(csv_path,fields,result_dict[item])
        
def statistical_analysis(list1, list2):
    mean1 = np.mean(list1)
    std1 = np.std(list1, ddof=1)
    mean2 = np.mean(list2)
    std2 = np.std(list2, ddof=1)

    # Perform a t-test to compare the means of the two lists
    t_stat, p_value = stats.ttest_ind(list1, list2)

    return round(mean1,2), round(std1,2), round(mean2,2), round(std2,2), round(t_stat,2), round(p_value,4)
        
def do_analysis(success_results, fail_results):
    metrics = {}
    for program in success_results:
        for key in ([key for key in success_results[program].keys()]):
            if key not in metrics:
                metrics[key] = {"success": [], "unsuccess":[]}
            metrics[key]["success"].append(success_results[program][key])
    for program in fail_results:
        for key in ([key for key in fail_results[program].keys()]):
            if key not in metrics:
                metrics[key] = {"success": [], "unsuccess":[]}
            metrics[key]["unsuccess"].append(fail_results[program][key])
    
    print("metric, mean1, mean2, t_stat, p_value")
    for key in metrics:
        if key == "file_id":
            continue
        mean1, std1, mean2, std2, t_stat, p_value = statistical_analysis(metrics[key]["success"], metrics[key]["unsuccess"])
        print("{},{},{},{},{},{}"
              .format(key, mean1, mean2, t_stat, p_value, "significant" if p_value < 0.05 else "unsignificant")
              )

if __name__ == "__main__":
    args = sys.argv[1:]
    success_dir = args[0]
    fail_dir = args[1]
    success_list = args[2]
    fail_list =args[3]
    save_to_dir = args[4]
    os.makedirs(save_to_dir, exist_ok = True)
    success_programs = get_program(success_dir, success_list)
    success_results = generate_data(success_programs)
    save_to_csv(os.path.join(save_to_dir, "s.csv"), success_results)
    
    fail_programs = get_program(fail_dir, fail_list)
    fail_results = generate_data(fail_programs)
    do_analysis(success_results, fail_results)

    save_to_csv(os.path.join(save_to_dir, "u.csv"), fail_results)
    