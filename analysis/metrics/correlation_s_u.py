import csv
import os
import sys
import utils
from explore import statistical_analysis_u as statistical_analysis_u

def get_files(s):
    result = []
    with open(s, mode ='r')as file:
        csvFile = csv.reader(file)
        for line in csvFile:
            if "file_id" in line:
                continue
            instance = line[0]
            if instance:
                file_path = os.path.join("/home/yang/Benchmark/dataset/python_avatar", instance + ".py") if "atcoder" in instance or "codeforces_" in instance \
                    else os.path.join("/home/yang/Benchmark/dataset/python_codenet", instance + ".py")
                result.append(file_path)
    return result

def correlation(s, u, save_dir, save_to_csv):
    success_files = get_files(s)
    unsuccess_files = get_files(u)
    success_complexity = []
    unsuccess_complexity = []
    
    for file in success_files:
        complexity = utils.run_cmds_nopipe(["python3", "/home/yang/Benchmark/tool/metrics/my_metric.py", file, save_dir, save_to_csv])
        # complexity = my_metric.main(file, save_dir, save_to_csv)
        success_complexity.append(complexity)
    for file in unsuccess_files:
        complexity = utils.run_cmds_nopipe(["python3", "/home/yang/Benchmark/tool/metrics/my_metric.py", file, save_dir, save_to_csv])
        unsuccess_complexity.append(complexity)
        
    print(success_complexity)
    print(unsuccess_complexity)
    mean_success, std_success, mean_unsuccess, std_unsuccess, u_stat, p_value_u = \
    statistical_analysis_u(success_complexity, unsuccess_complexity)
    print("mean_success: {}, std_success: {}, mean_unsuccess: {}, std_unsuccess: {}, u_stat: {}, utest_p_value: {}" \
        .format(mean_success, std_success, mean_unsuccess, std_unsuccess, u_stat, p_value_u))
    




if __name__ == "__main__":
    args = sys.argv[1:]
    s = args[0]
    u = args[1]
    save_dir = args[2]
    save_to_csv = args[3]
    correlation(s, u, save_dir, save_to_csv)
