import sys
import utils
from codebleu import calc_codebleu

def cal_codebleu_content(content1, content2):
    score = calc_codebleu([utils.clear_string(content1)], [utils.clear_string(content2)], lang="python", weights=(0.25, 0.25, 0.25, 0.25), tokenizer=None)
    return score

def cal_codebleu_file(file1, file2):
    content1 = utils.read_file(file1)
    content2 = utils.read_file(file2)
    return cal_codebleu_content(content1, content2)

if __name__ == "__main__":
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    print(cal_codebleu_file(file1, file2))