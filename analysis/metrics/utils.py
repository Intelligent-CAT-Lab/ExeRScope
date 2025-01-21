import ast
import csv
import json
import os
import sys
import subprocess
from codebleu import calc_codebleu

def clear_string(old_string):
    lines = old_string.splitlines()
    stripped_lines = [line.rstrip() for line in lines]
    cleaned_string = "\n".join(stripped_lines)
    return cleaned_string

def write_header_csv(csv_path, fields):
    """To set up headers for a csv file. 
       Followed by the following function `write_dict_csv` to write content in the csv file.
    """
    with open(csv_path, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()

def write_dict_csv(csv_path, fields, dict_data):
    """To add rows into a csv file with property `a`.
       Usually after setting up csv headers by calling the above function `write_header_csv`.
    """
    with open(csv_path, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writerow(dict_data)

def create_import(name, asname):
    """Create and return an ast Import node in the following format:
    import name as asname
    """
    ImportNode = ast.Import(names=[ast.alias(name=name, asname=asname)])
    return ImportNode

def create_importFrom(module, name, asname, level):
    """Create and return an ast ImportFrom node in the following format:
    from module import name as asname
    level=0 for absolute import, level=1 for relative import (e.g., .module).
    """
    ImportFromNode = ast.ImportFrom(
        module= module,
        names=[ast.alias(name=name, asname=asname)],
        level=level
    )
    return ImportFromNode

def get_imports(root):
    import_nodes = []
    for node in ast.iter_child_nodes(root):
        if isinstance(node, ast.Import):
            if node not in import_nodes:
                import_nodes.append(node)
        elif isinstance(node, ast.ImportFrom):
            if node not in import_nodes:
                import_nodes.append(node)
    return import_nodes

def read_file(file_path):
    file = open(file_path, 'r')
    content = file.read()
    return content

def write_file(file_path,content):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
    except:
        pass
    f = open(file_path, "w")
    f.write(content)
    f.close()

def write_json(file_path, dict):
    with open(file_path, 'w') as fp:
        json.dump(dict, fp)

def git_diff(file_path):
    diff_path = file_path.replace(".py","_diff.patch")
    diff_opts = ["git", "diff", file_path] #, "|& tee", diff_path
    print(" ".join(diff_opts), flush=True)
    diff = subprocess.run(diff_opts, stdout=subprocess.PIPE)
    diff_output = diff.stdout.decode('utf-8')
    write_file(diff_path, diff_output)
    # print(diff_output)
    return diff_path

def diff(source_file, target_file):
    diff_path = target_file.replace(".py","_diff.patch")
    diff_opts = ["diff", "-u", source_file, target_file]
    diff_output = run_cmds(diff_opts, None)
    write_file(diff_path, diff_output)
    # print(diff_output)
    return diff_output, diff_path

def run_cmds(cmd_list, timeoutVal):
    """To run commands with subprocess and set up a timeout value, stdout is `subprocess.PIPE`
        Command will be printed, output be returned.
    """
    cmds = " ".join(cmd_list)
    print(cmds, flush=True)
    if timeoutVal != None:
        run_cmds = subprocess.run(cmd_list, stdout=subprocess.PIPE, timeout=timeoutVal) #check=True, capture_output=True, shell=True
    else:
        run_cmds = subprocess.run(cmd_list, stdout=subprocess.PIPE)
    output = run_cmds.stdout.decode('utf-8')
    return output

def run_cmds_nopipe(cmd_list, timeoutVal):
    """To run commands with subprocess but without PIPE and set up a timeout value.
        Command will be printed, output be returned.
    """
    cmds = " ".join(cmd_list)
    print(cmds, flush=True)
    if timeoutVal != None:
        run_cmds = subprocess.run(cmds, check=True, capture_output=True, shell=True, timeout=timeoutVal) #check=True, capture_output=True, shell=True
    else:
        run_cmds = subprocess.run(cmds, check=True, capture_output=True, shell=True)
    output = run_cmds.stdout.decode('utf-8')
    # print(output, flush=True)
    return output

def git_checkout(file_path):
    git_checkout_opts = ["git", "checkout", file_path]
    print(" ".join(git_checkout_opts), flush=True)
    git_checkout = subprocess.run(git_checkout_opts, stdout=subprocess.PIPE)
    git_checkout_output = git_checkout.stdout.decode('utf-8')
    return git_checkout_output