import os
import json
import pprint

def get_datasets_models():
    model_list = ['gpt-4-turbo', 'gemini-1.5-pro', 'deepseek-coder-33b-instruct', 'semcoder_s', 'starcoder2-15b']
    dataset_list = ['Avatar', 'classeval', 'cruxeval', 'humaneval']
    return model_list, dataset_list

def parse_results(dataset, model):
    results  = {}
    correct, total = 0,0
    raw_folder = f"../Experiment_Results/ER/{model}/{dataset}"
    dataset_folder = f"../dataset/{dataset}"
    for d in os.listdir(raw_folder):
        pred_path = os.path.join(raw_folder, d, 'predict.txt')
        gt_path = os.path.join(dataset_folder, d, 'output.txt')
        
        pred_text = open(pred_path, 'r').read().strip("\n").strip().replace(' ','').replace('"','\'')
        gt_text = open(gt_path, 'r').read().strip("\n").strip().replace(' ','').replace('"','\'')
        if pred_text == gt_text:
            results[d] = 1
            correct += 1
        else:
            results[d] = 0
        total += 1
    path_json = f"../Experiment_Results/result_stat/ER/{model}_{dataset}.json"
    with open(path_json, 'w') as f:
        json.dump(results, f, indent=4)
    suc_rate = correct / total
    return "%.4f"%suc_rate


def main():
    report = {}
    model_list, dataset_list = get_datasets_models()
    for m in model_list:
        for d in dataset_list:
            score = parse_results(d, m)
            if d not in report:
                report[d] = {}
            report[d][m] = score
    report_path = "../Experiment_Results/result_stat/ER/overall_results.json"
    with open(report_path, 'w') as wr:
        json.dump(report, wr, indent=4)
    pprint.pprint(report, compact=True)
    
if __name__ == "__main__":
    main()