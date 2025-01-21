import ast
import scipy
from scipy import stats
import os
import json
import time
def categorize_value(value):

    try:
        parsed_value = ast.literal_eval(value)
        if isinstance(parsed_value, bool):
            return "binary"
        elif isinstance(parsed_value, int):
            return "int"
        elif isinstance(parsed_value, float):
            return "float"
        elif isinstance(parsed_value, str):
            return "string"
        elif isinstance(parsed_value, list):
            return "list"
        elif isinstance(parsed_value, tuple):
            return "tuple"
        elif isinstance(parsed_value, dict):
            return "dictionary"
        else:
            return "string"
    except:
        # If parsing fails, it's likely a plain string
        return "string"

def collect_types(dataset):
    types = {}
    folder = f"../dataset/{dataset}"
    for d in os.listdir(folder):
        output_path = os.path.join(folder, d, 'output.txt')
        if not os.path.exists(output_path):
            continue
        output_text = open(output_path, 'r').read().strip('\n')
        variable_type = categorize_value(output_text)
        types[d] = variable_type
    return types

def collect_output_types(dataset, model):
    results = {}
    folder = f"../Experiment_Results/ER/{model}/{dataset}"
    for d in os.listdir(folder):
        output_path = os.path.join(folder, d, 'predict.txt')
        output_text = open(output_path, 'r').read().strip('\n')
        variable_type = categorize_value(output_text)
        results[d] = variable_type
    return results
        
def load_models():
    model_list = ['gpt-4-turbo', 'gemini-1.5-pro', 'deepseek-coder-33b-instruct', 'semcoder_s', 'starcoder2-15b']
    return model_list      

def load_datasets():
    dataset_list = ['Avatar', 'classeval', 'humaneval', 'cruxeval']
    return dataset_list

def analyze_types(dataset):
    results_all = {}
    results_models_all = {}
    model_list = load_models()
    types_dataset = collect_types(dataset)
    
    for m in model_list:
        results = {}
        results_models = {}
        label_path = f"../Experiment_Results/result_stat/ER/{m}_{dataset}.json"
        label_result = json.load(open(label_path))
        types_pred = collect_output_types(dataset, m)
        for i in label_result:
            if types_dataset[i] not in results_models:
                results_models[types_dataset[i]] = {
                    'tm':0,
                    'vm':0,
                    'total':0
                }
            results_models[types_dataset[i]]['total'] += 1
            results[i] = {}
            results[i]['vm'] = label_result[i]
            if label_result[i] == 1:
                results_models[types_dataset[i]]['vm'] += 1
            if types_pred[i] == types_dataset[i]:
                results[i]['tm'] = 1
                results_models[types_dataset[i]]['tm'] += 1
            else:
                results[i]['tm'] = 0
            results[i]['types'] = types_dataset[i]
        
        results_all[m] = results
        results_models_all[m] = results_models
    return results_all, results_models_all

def main():
    summary = {}
    summary_models = {}
    datasets = load_datasets()
    for d in datasets:
        report, report_model = analyze_types(d)
        summary[d] = report
        summary_models[d] = report_model
    report_path = f"../Experiment_Results/figures/variable_types/variable_types.json"
    report_model_path = f"../Experiment_Results/figures/variable_types/variable_types_models.json"
    with open(report_path, 'w') as wr:
        json.dump(summary, wr, indent=4)
    with open(report_model_path, 'w') as wf:
        json.dump(summary_models, wf, indent=4)

if __name__ == "__main__":
    # analyze_types('humaneval')
    main()
        