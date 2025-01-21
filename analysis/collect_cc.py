import os
import csv
import json
import matplotlib.pyplot as plt
import numpy as np
import statistics
import subprocess
from tqdm import tqdm

def load_dataset():
    dataset_list = ['humaneval', 'cruxeval', 'classeval', 'avatar']
    return dataset_list

def load_cc(dataset):
    result = {}
    if dataset == 'avatar':
        data_dir = "../dataset/Avatar"
    else:
        data_dir = f"../dataset/{dataset}"
    ids = os.listdir(data_dir)
    csv_path = f"../Experiment_Results/result_stat/CC/{dataset}_complexity.csv"
    with open(csv_path, 'r') as file:
        csvFile = csv.reader(file)
        for lines in csvFile:
            if dataset in ['Avatar', "humaneval", "cruxeval", 'classeval']:
                task_id = lines[0].split("//")[-1].split(".")[0] 
            else:
                if len(lines[0].split("/")) == 1: continue
                task_id = lines[0].split("/")[-2]
            if task_id in ids:
                result[task_id] = int(lines[1])
    # print(result)
    return result



def collect_cc():
    results = {}
    data_avatar = load_cc_transformed("Avatar")
    data_humaneval = load_cc_transformed("humaneval")
    data_cruxeval = load_cc_transformed("cruxeval")
    data_classeval = load_cc_transformed("classeval")
    # print(data_avatar)
    results = {
        "avatar": data_avatar,
        "classeval": data_classeval,
        "cruxeval": data_cruxeval,
        "humaneval": data_humaneval,
    }
    wr_path = "../Experiment_Results/result_stat/CC/cc_transformed.json"
    with open(wr_path, 'w') as wr:
        json.dump(results, wr, indent=4)

def run_cc(dataset):
    csv_path = f"../Experiment_Results/result_stat/CC/{dataset}.csv"
    data_root = f"../dataset/{dataset}"
    for d in tqdm(os.listdir(data_root)):
        py_path = f"{data_root}/{d}/main.py"
        subprocess.run(["python", "./metrics/my_metric.py", py_path, "./tmp", csv_path])

def main():
    json_path = "../Experiment_Results/result_stat/CC/cc.json"
    if os.path.exists(json_path):
        data = json.load(open(json_path, 'r'))
    else:
        data = {}
    dataset_list = load_dataset()
    for d in dataset_list:
        ## check if data has been collected. If so continue
        if d in data.keys():
            continue
        result = load_cc(d)
        data[d] = result

if __name__ == "__main__":
    main()
        

