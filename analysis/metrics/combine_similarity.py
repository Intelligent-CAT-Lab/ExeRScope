import csv
import os
import sys
import utils

def combine_files(dir, save_dir):
    final_summary = {}
    save_to = os.path.join(save_dir, "similarity_summary.csv")
    for dirpath, _, files in os.walk(dir):
        for file in files:
            if file.endswith("csv") and "_similarity" in file:
                rule = file.split("_similarity")[0]
                similarity_file_path = os.path.join(dirpath, file)
                final_dict = {}
                summary = {}
                with open(similarity_file_path, mode ='r')as file:
                    csvFile = csv.reader(file)
                    for line in csvFile:
                        if "BLEU" in str(line):
                            continue
                        instance_id = line[0].split("/")[-1].strip()
                        # BLEU, CodeBLEU, Jaccard, LD
                        BLEU = line[2].split(":")[-1].strip()
                        CodeBLEU = line[3].split(":")[-1].strip()
                        Jaccard = line[4].split(":")[-1].strip()
                        LD = line[5].split(":")[-1].strip()
                        token_LD = line[6].split(":")[-1].strip()
                        
                        if instance_id not in final_dict:
                            final_dict[instance_id] = {
                                "BLEU":BLEU,
                                "CodeBLEU": CodeBLEU,
                                "Jaccard": Jaccard, 
                                "LD":LD,
                                "token_LD": token_LD
                            }
                header = ["rule", "BLEU", "CodeBLEU", "Jaccard", "LD", "token_LD"]
                
                for head in header:
                    if head == "id" or head == "rule":
                        continue
                    if head not in summary:
                        summary[head] = []
                    for instance_id in final_dict:
                        if "BLEU" not in final_dict[instance_id]:
                            continue
                        summary[head].append(float(final_dict[instance_id][head]))
                if rule not in final_summary:
                    final_summary[rule] = {}
                for head in summary:
                    if head == "rule":
                        continue
                    final_summary[rule][head] = round(sum(summary[head])/len(summary[head]),2)
    utils.write_header_csv(save_to, header)
    for rule in final_summary:
        final_summary[rule].update({"rule": rule})
        utils.write_dict_csv(save_to, header, final_summary[rule])
        print(rule, ",", [value for value in final_summary[rule].keys()])
        print(rule, ",", [value for value in final_summary[rule].values()])

if __name__ == "__main__":
    args = sys.argv[1:]
    csv_dir = args[0]
    save_dir = args[1]
    combine_files(csv_dir, save_dir)