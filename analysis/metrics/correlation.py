import csv
import os
import sys
import pandas as pd
from scipy.stats import spearmanr


def correlation(complexity_file, similarity_file):
    instance_result = {}
    all_complxity = []
    all_LD = []
    with open(complexity_file, mode ='r')as file:
        csvFile = csv.reader(file)
        for line in csvFile:
            if "rule" in line:
                continue
            rule = line[0]
            instance_id = line[1]
            complexity_diff = line[-1]
            if instance_id not in instance_result:
                instance_result[instance_id] = {
                    "instance_id": instance_id,
                    "complexity_diff": complexity_diff,
                }
    with open(similarity_file, mode ='r')as file:
        csvFile = csv.reader(file)
        for line in csvFile:
            if "File1" in line:
                continue
            instance_id = line[0].split("/")[-1]
            LD_distance = line[-2]
            token_LD_distance = line[-1]
            if instance_id not in instance_result:
                continue
            instance_result[instance_id].update({
                    "LD_distance": LD_distance,
                    "token_LD_distance": token_LD_distance
                })
            all_complxity.append(instance_result[instance_id]["complexity_diff"])
            all_LD.append(instance_result[instance_id]["LD_distance"])
    
    # print(len(instance_result), len(all_complxity), len(all_LD))
    df_dict = pd.DataFrame.from_dict(instance_result, orient='index')

    df_dict['complexity_diff'] = df_dict['complexity_diff'].astype(float)
    df_dict['LD_distance'] = df_dict['LD_distance'].astype(float)
    df_dict['token_LD_distance'] = df_dict['token_LD_distance'].astype(float)
    
    print(df_dict['LD_distance'])
    print(df_dict['token_LD_distance'])
    spearman_corr_dict1, p_value_dict1 = spearmanr(df_dict['complexity_diff'], df_dict['LD_distance'])
    spearman_corr_dict2, p_value_dict2 = spearmanr(df_dict['complexity_diff'], df_dict['token_LD_distance'])
    print("rule: {}, spearman_corr_LD: {}, p_value_LD: {}, spearman_corr_token_LD: {}, p_value_token_LD: {},".format(rule, spearman_corr_dict1, p_value_dict1, spearman_corr_dict2, p_value_dict2))


if __name__ == "__main__":
    args = sys.argv[1:]
    complexity_file = args[0]
    similarity_file = args[1]
    correlation(complexity_file, similarity_file)
    
    """
    python3 correlation.py /home/yang/Benchmark/v0_metric_avatar_transformation/a0ea016b1a22bd22bbe60ab2e02a198239b976a1/summary/add_nested_for_in.csv /home/yang/Benchmark/v0_metric_avatar_transformation/a0ea016b1a22bd22bbe60ab2e02a198239b976a1/CSV/add_nested_for_in_similarity.csv 

    """