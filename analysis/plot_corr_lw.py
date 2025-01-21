import matplotlib.pyplot as plt
import json
import collections
import numpy as np
from scipy import stats
import scipy
import os
class plot_bar_only:
    def __init__(self, result, data, title, path, xaxis):
        self.result = result
        self.data = data
        self.K = 10
        self.width = 0.6
        self.title = title
        self.path = path
        self.Xa = xaxis
    
    def data_convert(self):
        converted_data = {}
        for k in self.result.keys():
            if k in self.data.keys():
                key = round(self.data[k])
                if key not in converted_data.keys():
                    converted_data[key] = {'f':0, 'p':0}
                label = self.result[k]
                if label:
                    converted_data[key]['p'] += 1
                else:
                    converted_data[key]['f'] += 1
        od = collections.OrderedDict(sorted(converted_data.items()))
        return od
    
    def plot(self, corr=True, first=True):
        
        
        data = self.data_convert()
        label_x = list(data.keys())
        
        data_f = np.array([data[i]['f'] for i in data.keys()])
        data_p = np.array([data[i]['p'] for i in data.keys()])
        
        ratio = data_p/ (data_f + data_p)
        # print(ratio)
       
        
        bar_data = {
            'Correct': data_p[: self.K],
            'Incorrect': data_f[: self.K]
        }
        # plt.rcParams["figure.figsize"] = [7.50, 3.50]
        # plt.rcParams["figure.autolayout"] = True
        fig, ax = plt.subplots(figsize=(3.5, 3.5))
        
        bottom = np.zeros(len(label_x[:self.K]))
        for s, s_count in bar_data.items():
            if s=='Correct':
                bar_color = 'green'
            if s=='Incorrect':
                bar_color = 'red'
            
            p = ax.bar(label_x[: self.K], s_count, self.width, label=s, bottom=bottom, color=bar_color)
          
            bottom += s_count
        # ax.tick_params(axis='x')
        ## add line plots
        if first:
            plt.ylabel('#Correct / Incorrect',  fontsize=22)
            plt.xlabel(f'#{self.Xa}',  fontsize=25)

        ratio_line = ratio[:self.K]
        x_line = label_x[:self.K]
        ax2 = plt.twinx()
        ax2.scatter(x_line, ratio_line, color='blue', label='CERR' , s=30, marker='o')
        ax2.set_ylim(0,1)
        # ax2.set_ylabel('CRR', fontsize=25)
        # if not first:
        for label in ax.get_yticklabels():
            label.set_fontsize(25)
        for label in ax2.get_yticklabels():
            label.set_fontsize(25)
        for label in ax.get_xticklabels():
            label.set_fontsize(25)
        
        if not first:
            ax.xaxis.set_tick_params(labelbottom=False)
            ax.yaxis.set_tick_params(labelleft=False)
            ax.yaxis.set_tick_params(left=False)

        if corr:
            corr, pvalue = scipy.stats.spearmanr(label_x[:self.K], ratio[:self.K])
            title = self.title + '\n' + 'Spearman RoC:' + str(corr)
        else:
            title = self.title
        ax.set_title(title)
      
        plt.savefig(self.path, bbox_inches='tight', dpi=500, pad_inches=1)
        corr, pvalue = stats.spearmanr(label_x[:self.K], ratio[:self.K])

def load_models():
    model_list = ["semcoder_s", "gpt-4-turbo", "gemini-1.5-pro", "starcoder2-15b", "deepseek-coder-33b-instruct"]
    return model_list       
    
def load_data(task, model):
    if task == "IER":
        path_avatar = f"../Experiment_Results/result_stat/ER/{model}_Avatar.json"
        path_heval =  f"../Experiment_Results/result_stat/ER/{model}_humaneval.json"
        path_ceval = f"../Experiment_Results/result_stat/ER/{model}_classeval.json"
        path_crux = f"../Experiment_Results/result_stat/ER/{model}_cruxeval.json"
        result_heval = json.load(open(path_heval, 'r'))
        result_ceval = json.load(open(path_ceval, 'r'))
        result_crux = json.load(open(path_crux, 'r'))
        overall_results = {}
        for res in [result_heval, result_crux, result_ceval]:
            for key in res.keys():
                overall_results[key] = res[key]
    if task == "SR":
        path_heval =  f"../Experiment_Results/result_stat/SR/{model}_humaneval.txt"
        path_ceval = f"../Experiment_Results/result_stat/SR/{model}_classeval.txt"
        data_dir_heval = "../dataset/Intermediate/Synthesis/humaneval"
        data_dir_ceval = "../dataset/Intermediate/Synthesis/classeval"
        
        corrrect_id_list_hevel, corrrect_id_list_cevel = [], []
        with open(path_heval, 'r') as f1:
            for line in f1.readlines():
                corrrect_id_list_hevel.append(line.strip("\n"))
        with open(path_ceval, 'r') as f2:
            for line in f2.readlines():
                corrrect_id_list_cevel.append(line.strip("\n"))
        overall_results = {}
        for i in os.listdir(data_dir_heval):
            if i in corrrect_id_list_hevel:
                overall_results[i] = 1
            else:
                overall_results[i] = 0
        for i in os.listdir(data_dir_ceval):
            if i in corrrect_id_list_cevel:
                overall_results[i] = 1
            else:
                overall_results[i] = 0
    if task == "CR":
        path_heval =  f"../Experiment_Results/result_stat/CR/{model}_humaneval.txt"
        path_ceval = f"../Experiment_Results/result_stat/CR/{model}_classeval.txt"
        path_crux =  f"../Experiment_Results/result_stat/CR/{model}_cruxeval.txt"
        # path_avatar = f"../Experiment_Results/result_stat/CR/{model}_Avatar.txt"
        data_dir_heval = "../dataset/Intermediate/Synthesis/humaneval"
        data_dir_ceval = "../dataset/Intermediate/Synthesis/classeval"
        data_dir_crux = "../dataset/cruxeval"
        # data_dir_avatar = "../dataset/Avatar/Avatar-Python"
        
        corrrect_id_list_hevel, corrrect_id_list_cevel, corrrect_id_list_crux, corrrect_id_list_avatar = [], [], [], []
        with open(path_heval, 'r') as f1:
            for line in f1.readlines():
                corrrect_id_list_hevel.append(line.strip("\n"))
        with open(path_ceval, 'r') as f2:
            for line in f2.readlines():
                corrrect_id_list_cevel.append(line.strip("\n"))
        with open(path_crux, 'r') as f3:
            for line in f3.readlines():
                corrrect_id_list_crux.append(line.strip("\n"))
        # with open(path_avatar, 'r') as f4:
        #     for line in f4.readlines():
        #         corrrect_id_list_avatar.append(line.strip("\n"))            
        overall_results = {}
        for i in os.listdir(data_dir_heval):
            if i in corrrect_id_list_hevel:
                overall_results[i] = 1
            else:
                overall_results[i] = 0
        for i in os.listdir(data_dir_ceval):
            if i in corrrect_id_list_cevel:
                overall_results[i] = 1
            else:
                overall_results[i] = 0
        for i in os.listdir(data_dir_crux):
            if i in corrrect_id_list_crux:
                overall_results[i] = 1
            else:
                overall_results[i] = 0
    overall_cc = {}
    if task == "CR":
        path_cc = "../Experiment_Results/result_stat/LW/lw_trans.json"
    else:
        path_cc = "../Experiment_Results/result_stat/LW/lw.json"
    cc_data = json.load(open(path_cc, 'r'))
    for key in cc_data:
        for k in cc_data[key]:
            overall_cc[k] = cc_data[key][k]
    return overall_results, overall_cc

def plot_corr(model, task = 'IER'):
    overall_results, overall_cc = load_data(task, model)
    path = f"../Experiment_Results/figures/dynamic_property/ER_{model}.jpg"
    plotter = plot_bar_only(overall_results, overall_cc, model, path, "Loop Length")
    plotter.plot()


if __name__ == "__main__":
    for m in load_models():
        plot_corr(m)