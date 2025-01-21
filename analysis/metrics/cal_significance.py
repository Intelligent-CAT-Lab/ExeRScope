import csv
import os
import sys
import numpy as np
import scipy.stats as stats
from explore import statistical_analysis_t as statistical_analysis_t
from explore import statistical_analysis_u as statistical_analysis_u

def cal_summary(csv_file):
    with open(csv_file, mode ='r')as file:
      csvFile = csv.reader(file)
      before, after = {}, {}
      for line in csvFile:
          if "Operator" in line:
              continue
          op = line[0]
          before[op] = {
              "DS": int(line[1]) + int(line[2]) + int(line[3]),
              "DU": int(line[4]) + int(line[5]) + int(line[6]),
              "N": int(line[7]) + int(line[8]) + int(line[9]),
              "Total": sum([int(item) for item in line[1:]])
              }
          after[op] = {
	      "DS": int(line[1]) + int(line[5]) + int(line[7]),
              "DU": int(line[2]) + int(line[4]) + int(line[8]),
              "N": int(line[3]) + int(line[6]) + int(line[9]),
              "Total": sum([int(item) for item in line[1:]])
	      }
          # seperate operator/ one round

    before_rate, after_rate = {}, {}
    for op in before:
        for key in before[op]:
            if key == "Total":
                continue
            if key not in before_rate:
                before_rate[key] = []
            before_rate[key].append(round(before[op][key]/before[op]["Total"], 2))
    for op in after:
        for key in after[op]:
            if key == "Total":
                  continue
            if key not in after_rate:
                after_rate[key] = []
            after_rate[key].append(round(after[op][key]/after[op]["Total"], 2))
    for op in before_rate:
        mean_before, std_before, mean_after, std_after, t_stat, p_value = \
            statistical_analysis_t(before_rate[op], after_rate[op])
        print("Type: {}, mean_before: {}, std_before: {}, mean_after: {}, std_after: {}, t_stat: {}, p_value: {}" \
              .format(op, mean_before, std_before, mean_after, std_after, t_stat, p_value))

def parse_single_operator_D(results_dir):
    for dirpath, _, files in os.walk(results_dir):
        for file in files:
            if file.startswith("transformation"):
                file_path = os.path.join(dirpath, file)
                print(file_path)
                exit(0)
        
def parse_single_operator_total(results_dir):
    for dirpath, _, files in os.walk(results_dir):
        for file in files:
            if file.startswith("transformation"):
                file_path = os.path.join(dirpath, file)
                results = parse_results_per_file(file_path)
                for key in ["success", "unsuccess"]:
                    # print(results["Before"][key], results["After"][key])
                    mean_before, std_before, mean_after, std_after, t_stat, p_value = \
                        statistical_analysis_t(results["Before"][key], results["After"][key])
                    mean_before, std_before, mean_after, std_after, u_stat, p_value_u = \
                        statistical_analysis_u(results["Before"][key], results["After"][key])
                    print("Operator: {}, Result: {}, mean_before: {}, std_before: {}, mean_after: {}, std_after: {}, t_stat: {}, ttest_p_value: {}, u_stat: {}, utest_p_value: {}" \
                          .format(results["Operator"], key, mean_before, std_before, mean_after, std_after, t_stat, p_value, u_stat, p_value_u))

def parse_single_operator_seperate(results_dir):
    for dirpath, _, files in os.walk(results_dir):
        for file in files:
            if file.startswith("transformation"):
                file_path = os.path.join(dirpath, file)
                results = parse_results_per_file_seperate(file_path)

                #for key in ["Before_DS", "Before_DU", "Before_N"]:
                    # mean_before, std_before, mean_after, std_after, t_stat, p_value_t = \
                    #     statistical_analysis_t(results[key], results[key + "_transformation"])
                mean_before, std_before, mean_after, std_after, u_stat, p_value_u = \
                    statistical_analysis_u(results["All_Before"], results["All_After"])
                print("Op:{}, mean_success_before:{}, std_before:{}, mean_success_after:{}, std_after:{}, u_stat:{}, utest_p:{}, Total:{}, {}" \
                      .format(results["Operator"], mean_before, std_before, mean_after, std_after, u_stat, p_value_u, results["Total"], "significant" if p_value_u < 0.05 else "unsignificant"))
                # print(results["All_Before"], "\n", results["All_After"])
                    # print("Data:\nBefore: {}\nAfter: {}".format(results[key],results[key + "_transformation"]))
                    
def string_to_list(string):
    return string.replace("]", "").replace("[", "").replace("\'", "").replace(" ", "").split(",")

def parse_results_per_file(csv_file):
    op = csv_file.split("transformation_")[1].split(".csv")[0]
    results = {
        "Operator": op,
        "Before": {"success": [0, 0, 0], "unsuccess": [0, 0, 0]},
        "After": {"success": [0, 0, 0], "unsuccess": [0, 0, 0] },
        "Total" : 0
    }
    programs = []
    with open(csv_file, mode ='r')as file:
      csvFile = csv.reader(file)
      for line in csvFile:
          if "Operator" in line:
              continue
          program_id = line[1]
          if program_id not in programs:
               programs.append(program_id)
          before_results = string_to_list(line[2])
          after_results = string_to_list(line[3])
          for i in range(3):
              if before_results[i] == "unsuccess":
                  results["Before"]["unsuccess"][i] += 1
              elif before_results[i] == "success":
                  results["Before"]["success"][i] += 1
              else:
                  raise Exception("Parse Error")

              if after_results[i] == "unsuccess":
                  results["After"]["unsuccess"][i] += 1
              elif after_results[i] == "success":
                  results["After"]["success"][i] += 1
              else:
                  raise Exception("Parse Error")
    results["Total"] = len(programs)
    # print(results)
    for i in range(3):
        for key1 in ["Before", "After"]:
            for key2 in ["success", "unsuccess"]:
                results[key1][key2][i] = round(results[key1][key2][i]/results["Total"], 2)
    return results

def parse_results_per_file_seperate_all(csv_file):
    op = csv_file.split("transformation_")[1].split(".csv")[0]
    results = {
        "Operator": op,
        "Before": [],
        "After": [],
        "Total" : 0
    }
    programs = []
    with open(csv_file, mode ='r')as file:
      csvFile = csv.reader(file)
      for line in csvFile:
          if "Operator" in line:
              continue
          program_id = line[1]
          if program_id not in programs:
               programs.append(program_id)
          before_results = string_to_list(line[2])
          after_results = string_to_list(line[3])
          before_num_success = len([item for item in before_results if item == "success"])
          after_num_success = len([item for item in after_results if item == "success"])
          s_before = round(before_num_success/len(before_results), 2)
          s_after = round(after_num_success/len(after_results), 2)
          results["Before"].append(s_before)
          results["After"].append(s_after)
    results["Total"] = len(programs)
    return results

def parse_results_per_file_seperate(csv_file):
    op = csv_file.split("transformation_")[1].split(".csv")[0]
    results = {
        "Operator": op,
        "Before_DS": [],
        "Before_DS_transformation": [],
        "Before_DU": [],
        "Before_DU_transformation": [],
        "Before_N": [],
        "Before_N_transformation": [],
        "All_Before" : [],
        "All_After": [],
        "Total" : 0
    }
    programs = []
    with open(csv_file, mode ='r')as file:
      csvFile = csv.reader(file)
      for line in csvFile:
          if "Operator" in line:
              continue
          program_id = line[1]
          if program_id not in programs:
               programs.append(program_id)
          before_results = string_to_list(line[2])
          after_results = string_to_list(line[3])
          before_num_success = len([item for item in before_results if item == "success"])
          after_num_success = len([item for item in after_results if item == "success"])
          s_before = round(before_num_success/len(before_results), 2)
          s_after = round(after_num_success/len(after_results), 2)
          if before_num_success == 3:
              results["Before_DS"].append(before_num_success)
              results["Before_DS_transformation"].append(after_num_success)
          elif before_num_success == 0:
              results["Before_DU"].append(before_num_success)
              results["Before_DU_transformation"].append(after_num_success)
          else:
              results["Before_N"].append(before_num_success)
              results["Before_N_transformation"].append(after_num_success)
          results["All_Before"].append(before_num_success)
          results["All_After"].append(after_num_success)
    results["Total"] = len(programs)
    return results

if __name__ == "__main__":
    args = sys.argv[1:]
    csv_file = args[0]
    res_dir = args[1] #/home/yang/PLTranslationEmpirical/s
    # cal_summary(csv_file)
    # parse_single_operator_total(res_dir)
    parse_single_operator_seperate(res_dir)
    exit(0)

    # before = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,2,1,1,2,2,1,1,2,1,2,2,1,1,2,2,1,1,2,2,2,1,2,1,2,2,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3]
    # after = [0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,1,0,1,0,2,0,0,0,0,0,2,0,0,0,0,2,1,0,0,0,1,0,0,1,0,0,3,0,0,0,1,1,0,2,3,0,0,2,0,0,3,0,0,2,0,0,3,3,2,3,0,3,2,0,0,0,1,3,0,2,0,3,3,1,1,0,3,0,0,0,3,0,3,1,3,3,0,3,0,3,3,0,1,3,1,3,3,3,0,3,3,3,0,0,0,1,0,0,0,3,3,2,2,0,0,0]
    before = [0, 0, 0, 1, 0, 1, 1, 3, 3, 3, 3, 3, 3]
    after = [0, 0, 0, 0, 0, 0, 0, 3, 1, 0, 3, 2, 3]
    mean_before, std_before, mean_after, std_after, u_stat, p_value_u = \
        statistical_analysis_u(before, after)
    print("mean_before: {}, std_before: {}, mean_after: {}, std_after: {}, u_stat: {}, utest_p_value: {}" \
          .format(mean_before, std_before, mean_after, std_after, u_stat, p_value_u))
    print(before, "\n", after)

    before = [0, 0, 0, 1, 0, 1, 1, 3, 3, 3, 3, 3, 3, 0, 0, 0, 1, 0, 1, 1, 3, 3, 3, 3, 3, 3]
    after = [0, 0, 0, 0, 0, 0, 0, 3, 1, 0, 3, 2, 3, 0, 0, 0, 0, 0, 0, 0, 3, 1, 0, 3, 2, 3]
    mean_before, std_before, mean_after, std_after, u_stat, p_value_u = \
        statistical_analysis_u(before, after)
    print("mean_before: {}, std_before: {}, mean_after: {}, std_after: {}, u_stat: {}, utest_p_value: {}" \
          .format(mean_before, std_before, mean_after, std_after, u_stat, p_value_u))
    print(before, "\n", after)
    # mean_before, std_before, mean_after, std_after, t_stat, p_value_t = \
    #     statistical_analysis_t(before, after)
    # print("mean_before: {}, std_before: {}, mean_after: {}, std_after: {}, t_stat: {}, ttest_p_value: {}" \
    #       .format(mean_before, std_before, mean_after, std_after, t_stat, p_value_t))
    

