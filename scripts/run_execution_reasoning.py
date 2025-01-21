import argparse
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
import openai
from tqdm import tqdm
from create_prompt_ier import create_prompt
from prompt import chatgpt_generator, huggingface_generator, huggingface_generator_chat, generator_lllm, generator_vllm, generator_gemini
import json
from vllm import LLM

AUTH_TOKEN = os.getenv('AUTH_TOKEN')
MAX_NEW_TOKEN=1024
def find_path(dataset, pl, der, model, task):
    root = "../dataset"
    if dataset == "HumanEvalFix":
        data_path = "../dataset/Intermediate/Repair/HumanEvalFix_new"
    elif dataset == "HumanEval_Trans":
        data_path = "../dataset/humaneval"
    elif not der:
        if dataset in ["CodeNet", "Avatar"]:
            data_path = os.path.join(root, dataset, f"{dataset}-{pl}")
        else:
            data_path = os.path.join(root, dataset)
        if not os.path.exists(data_path):
            print(f'{dataset} does not exist')
    else:
        root_der = f"../Experiment_Results/DER/{task}/"
        if dataset in ["CodeNet", "Avatar"]:
            data_path = os.path.join(root_der, model.split("/")[-1], f"{dataset}-{pl}")
        else:
            data_path = os.path.join(root_der, model.split("/")[-1], dataset)
        if not os.path.exists(data_path):
            print(f'{dataset} does not exist')
    return data_path

def load_model(model_id, cache_dir, api_type):
    ## huggingface models
    if api_type == 'huggingface':
        # print(cache_dir)
        model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", use_auth_token=AUTH_TOKEN, cache_dir=cache_dir)
        tokenizer = AutoTokenizer.from_pretrained(model_id, device_map="auto", use_auth_token=AUTH_TOKEN, cache_dir=cache_dir)
        return model, tokenizer
    elif api_type == "vllm":
        if "deepseek-coder-33b" in model_id:
            model = LLM(model=model_id, max_model_len=35000, download_dir=cache_dir)
        else:
            model = LLM(model=model_id, download_dir=cache_dir, max_model_len=4810, tensor_parallel_size=3)
        return model, None
    else:
        return model_id, None    



def main(model_id, dataset, cache_dir, write_dir, task, pl, der, wo_icl):
    json_path = "../model_config.json"
    model_config = json.load(open(json_path, 'r'))
    api_type = model_config[model_id]["api"]
    root_dir = find_path(dataset, pl, der, model_id, task)
    if der:
        if dataset in ['CodeNet', 'Avatar']:
            write_root = os.path.join(write_dir, 'DER', task, model_id.split("/")[-1], f"{dataset}-{pl}")
        else:
            write_root = os.path.join(write_dir, 'DER', task, model_id.split("/")[-1], dataset)
    elif wo_icl: 
        if dataset in ['CodeNet', 'Avatar']:
            write_root = os.path.join(write_dir, 'IER', 'vanilla', model_id.split("/")[-1], f"{dataset}-{pl}")
        else:
            write_root = os.path.join(write_dir, 'IER', 'vanilla', model_id.split("/")[-1], dataset)    
    else:
        if dataset in ['CodeNet', 'Avatar']:
            write_root = os.path.join(write_dir, 'IER', model_id.split("/")[-1], f"{dataset}-{pl}")
        else:
            write_root = os.path.join(write_dir, 'IER', model_id.split("/")[-1], dataset)
    if not os.path.exists(write_root):
        os.makedirs(write_root)
    model, tokenizer = load_model(model_id, cache_dir, api_type)
    for d in tqdm(os.listdir(root_dir)):
        if pl == 'Java':
            ##  read java files
            code_path = os.path.join(root_dir, d, 'Main.java')
        else:
            if dataset == "HumanEval_Trans:":
                code_path = os.path.join(root_dir, d, 'transformation.py')
            else:
                code_path = os.path.join(root_dir, d, 'main.py')
        input_path = os.path.join(root_dir, d, 'input.txt')
        if not os.path.exists(code_path) or not os.path.exists(input_path):
            continue
        if dataset=='HumanEval_Trans' and "__" in d:
            continue
        code = open(code_path, 'r').read().strip("\n")
        code_input = open(input_path, 'r').read().strip("\n")
        prompt = create_prompt(model_id, code, code_input, dataset, pl, wo_icl)

        write_folder = os.path.join(write_root, d)
        if not os.path.exists(write_folder):
            os.mkdir(write_folder)
        write_path = os.path.join(write_folder, 'response.txt')
        if os.path.exists(write_path):
            continue

        if api_type=="openai":
            err_flg, response = chatgpt_generator(model_id, prompt)
            if err_flg:
                response = 'ERR: reaches maximum context length'
        if api_type == "huggingface":
            response = huggingface_generator((model, tokenizer), prompt, MAX_NEW_TOKEN)
        if api_type == "huggingface_chat":
            response = huggingface_generator_chat((model, tokenizer), prompt, MAX_NEW_TOKEN)
        if api_type == "vllm":
            response = generator_vllm(model, prompt, MAX_NEW_TOKEN)
        if api_type == "litellm":
            try:
                response = generator_lllm(model, prompt)
            except:
                response = "err"
                print(d)
        if api_type == "gai":
           response = generator_gemini(model_id, prompt)
        
        with open(write_path, 'w') as wr:
            if response:
                wr.write(response)
            else:
                wr.write("None")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default='none')
    parser.add_argument("--dataset", type=str, default='none', help="select one from [CodeNet, Avatar, cruxeval, mbpp, humaneval, classeval]")
    parser.add_argument("--cache", type=str, default="./cache")
    parser.add_argument("--writePath", type=str, default="../Experiment_Results")
    parser.add_argument("--task", type=str, default="IER")
    parser.add_argument("--pl", type=str, default="Python", help="select one from [Python, Java]")
    parser.add_argument("--der", help='der inference', action='store_true')
    parser.add_argument("--wo_icl", action="store_true")
    args = parser.parse_args()

    model_id = args.model
    dataset = args.dataset
    cache_dir = args.cache
    write_dir = args.writePath
    task = args.task
    pl = args.pl
    der = args.der
    wo_icl = args.wo_icl
    main(model_id, dataset, cache_dir, write_dir, task, pl, der, wo_icl)
    # find_path(dataset, pl)
