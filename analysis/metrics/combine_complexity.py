import csv
import os
import sys
import utils

def combine_files(dir, save_dir):
    final_summary = {}
    for dirpath, _, files in os.walk(dir):
        for file in files:
            if file.endswith("csv") and "_before" in file:
                rule = file.split("_before")[0]
                save_to = os.path.join(save_dir, rule + ".csv")
                before_file_path = os.path.join(dirpath, file)
                after_file_path = before_file_path.replace("before", "after")
                final_dict = {}
                summary = {}
                with open(before_file_path, mode ='r')as file:
                    csvFile = csv.reader(file)
                    for line in csvFile:
                        if "File" in line:
                            continue
                        # if "File:" not in str(line):
                        #     continue
                        instance_id = line[0].split("/")[-1].strip()
                        base = line[1].split(":")[-1].strip()
                        predicates = line[2].split(":")[-1].strip()
                        nested = line[3].split(":")[-1].strip()
                        sum_distance = line[4].split(":")[-1].strip()
                        avg_distance = line[5].split(":")[-1].strip()
                        complex_constructs = line[6].split(":")[-1].strip()
                        third = line[7].split(":")[-1].strip()
                        inter = line[8].split(":")[-1].strip()
                        intra = line[9].split(":")[-1].strip()
                        final = line[10].split(":")[-1].strip()
                        
                        if instance_id not in final_dict:
                            final_dict[instance_id] = {
                                "rule":rule,
                                "id": instance_id,
                                "base_complexity_before": base, 
                                "predicates_with_operators_before":predicates,
                                "nested_levels_before":nested,
                                "sum_var_distance_before":sum_distance,
                                "avg_distance_before":avg_distance,
                                "complex_constructs_before":complex_constructs,
                                "third_party_apis_before":third,
                                "inter_dependencies_before": inter,
                                "intra_dependencies_before": intra,
                                "final_before":final
                            }
                with open(after_file_path, mode ='r')as file:
                    csvFile = csv.reader(file)
                    for line in csvFile:
                        if "File" in line:
                            continue
                        # if "File:" not in str(line):
                        #     continue
                        instance_id = line[0].split("/")[-1].strip()
                        base = line[1].split(":")[-1].strip()
                        predicates = line[2].split(":")[-1].strip()
                        nested = line[3].split(":")[-1].strip()
                        sum_distance = line[4].split(":")[-1].strip()
                        avg_distance = line[5].split(":")[-1].strip()
                        complex_constructs = line[6].split(":")[-1].strip()
                        third = line[7].split(":")[-1].strip()
                        inter = line[8].split(":")[-1].strip()
                        intra = line[9].split(":")[-1].strip()
                        final = line[10].split(":")[-1].strip()
                        if instance_id not in final_dict:
                            # print(rule, instance_id)
                            continue
                        final_dict[instance_id].update({
                                "base_complexity_after": base,
                                "predicates_with_operators_after":predicates,
                                "nested_levels_after":nested,
                                "sum_var_distance_after":sum_distance,
                                "avg_distance_after":avg_distance,
                                "complex_constructs_after":complex_constructs,
                                "third_party_apis_after":third,
                                "inter_dependencies_after": inter,
                                "intra_dependencies_after": intra,
                                "final_after":final,
                            })
                        final_dict[instance_id].update({"final_diff": float(final_dict[instance_id]["final_after"]) - float(final_dict[instance_id]["final_before"])})
                header = ["rule", "id", "base_complexity_before", "base_complexity_after", "predicates_with_operators_before",
                    "predicates_with_operators_after", "nested_levels_before", "nested_levels_after",
                        "sum_var_distance_before", "sum_var_distance_after", "avg_distance_before",
                            "avg_distance_after", "complex_constructs_before", "complex_constructs_after",
                                "third_party_apis_before", "third_party_apis_after", "inter_dependencies_before", "inter_dependencies_after",
                                "intra_dependencies_before", "intra_dependencies_after",
                                "final_before", "final_after", "final_diff"]
                utils.write_header_csv(save_to, header)
                for instance_id in final_dict:
                    # print(final_dict[instance_id])
                    # print(header)
                    utils.write_dict_csv(save_to, header, final_dict[instance_id])
                for head in header:
                    if head == "id" or head == "rule":
                        continue
                    if head not in summary:
                        summary[head] = []
                    for instance_id in final_dict:
                        if "base_complexity_after" not in final_dict[instance_id]:
                            continue
                        summary[head].append(float(final_dict[instance_id][head]))
                if rule not in final_summary:
                    final_summary[rule] = {}
                for head in summary:
                    if head == "rule":
                        continue
                    # print(head, summary[head])
                    final_summary[rule][head] = round(sum(summary[head])/len(summary[head]),2)
    final_save = os.path.join(save_dir, "complexity.csv")
    final_header = ["rule", "base_complexity_before", "base_complexity_after", "predicates_with_operators_before",
                    "predicates_with_operators_after", "nested_levels_before", "nested_levels_after",
                        "sum_var_distance_before", "sum_var_distance_after", "avg_distance_before",
                            "avg_distance_after", "complex_constructs_before", "complex_constructs_after",
                                "third_party_apis_before", "third_party_apis_after", "inter_dependencies_before", "inter_dependencies_after",
                                "intra_dependencies_before", "intra_dependencies_after",
                                "final_before", "final_after", "final_diff"]
    utils.write_header_csv(final_save, final_header)
    for rule in final_summary:
        final_summary[rule].update({"rule": rule})
        utils.write_dict_csv(final_save, final_header, final_summary[rule])
        
        # print(rule, ",", [value for value in final_summary[rule].values()])

if __name__ == "__main__":
    args = sys.argv[1:]
    csv_dir = args[0]
    save_dir = args[1]
    combine_files(csv_dir, save_dir)