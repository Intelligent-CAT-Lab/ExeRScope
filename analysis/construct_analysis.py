import json
from star_plot import star_plot
def load_dataset():
    dataset_list = ['humaneval', 'cruxeval', 'classeval', 'Avatar']
    return dataset_list

def ier_constructs(data_path, label_path):
    result = {}
    correct_ids = []
    total_count = {
        'nested': 0, 'if': 0, 'for': 0, 'while': 0, 'try': 0, 'switch': 0, 'basic': 0, "nested_if": 0
    }
    correct_count = {
        'nested': 0, 'if': 0, 'for': 0, 'while': 0, 'try': 0, 'switch': 0, 'basic': 0, "nested_if": 0
    }
    ## loading data
    with open(data_path, 'r') as reader:
        data_constructs = json.load(reader)
    with open(label_path, 'r') as reader1:
        data_labels = json.load(reader1)
    
    for k in data_constructs.keys():
        for j in data_constructs[k].keys():
            total_count[j] += data_constructs[k][j]
        if k not in data_labels: continue
        if data_labels[k] == 1:
            for j in data_constructs[k].keys():
                correct_count[j] += data_constructs[k][j]
    for k in total_count.keys():
        if total_count[k]>1:
            result[k] = correct_count[k] / total_count[k]
    return result


def plot_constructs_ier(dataset):
    # dataset = 'humaneval'
    data_path= f"../Experiment_Results/result_stat/Constructs/{dataset}.json"
    label_path_gpt4 = f"../Experiment_Results/result_stat/ER/gpt-4-turbo_{dataset}.json"
    label_path_gemini = f"../Experiment_Results/result_stat/ER/gemini-1.5-pro_{dataset}.json"
    label_path_deepseek = f"../Experiment_Results/result_stat/ER/deepseek-coder-33b-instruct_{dataset}.json"
    label_path_semcoder = f"../Experiment_Results/result_stat/ER/semcoder_s_{dataset}.json"
    label_path_starcoder = f"../Experiment_Results/result_stat/ER/starcoder2-15b_{dataset}.json"
    gpt4 = ier_constructs(data_path, label_path_gpt4)
    gemini = ier_constructs(data_path, label_path_gemini)
    semcoder = ier_constructs(data_path, label_path_semcoder)
    starcoder = ier_constructs(data_path, label_path_starcoder)
    deepseek = ier_constructs(data_path, label_path_deepseek)
    
    label = [k for k in gpt4.keys()]
    label_new = []
    for l in label:
        if l == 'nested':
            label_new.append("NL")
        if l == 'if':
            label_new.append("I")
        if l == 'for':
            label_new.append("F")
        if l == "while":
            label_new.append("W")
        if l == 'try':
            label_new.append("T")
        if l == 'basic':
            label_new.append("B")
        if l == "switch":
            label_new.append("S")
        if l == 'nested_if':
            label_new.append("NI")
    gpt4_sr = [gpt4[l] for l in label]
    gemini_sr = [gemini[l] for l in label]
    semcoder_sr = [semcoder[l] for l in label]
    starcoder_sr = [starcoder[l] for l in label]
    deepseek_sr = [deepseek[l] for l in label]
    
  
    data = [
        label_new,
        (
            dataset, [
                gpt4_sr,
                gemini_sr,
                deepseek_sr,
                semcoder_sr,
                starcoder_sr,
            ]
        )
    ]
    labels = ('GPT-4-Turbo','Gemini-1.5-Pro', 'DeepSeek-Coder-Inst-33b', 'SemCoder-S', 'StarCoder2-15b')
    title = f"{dataset}_ER"
    star_plot(data, len(label), labels, title)

if __name__ == "__main__":
    for d in load_dataset():
        plot_constructs_ier(d)