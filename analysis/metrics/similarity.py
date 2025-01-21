import csv
import editdistance
import os 
import sys
from bleu import get_bleu
from bleu import get_codebleu, get_codebleu
from jaccard import jaccard_tokens
from LD import get_LD_similarity
from nltk import word_tokenize
from utils import read_file, write_dict_csv


def tokenize_code(code):
    tokens = word_tokenize(code)
    return tokens

def bleu(file1_tokens, file2_tokens):
    return get_bleu(file1_tokens, file2_tokens)

def codebleu(file1_tokens, file2_tokens):
    return get_codebleu(file1_tokens, file2_tokens)

def get_jaccard(file1_tokens, file2_tokens):
    return jaccard_tokens(file1_tokens, file2_tokens)

def LD_distance(file1_tokens, file2_tokens):
    content1 = " ".join(file1_tokens)
    content2 = " ".join(file2_tokens)
    return get_LD_similarity(content1, content2)

def token_LD_distance(file1_tokens, file2_tokens):
    token_LD = editdistance.eval(file1_tokens, file2_tokens)
    return token_LD

def save_to_file(fil1, file2, save_to, bleu_score, codebleu_score, jacard_score, ld_distance, token_ld_distance):
    result = {
        "File1": file1,
        "File2": file2,
        "BLEU": bleu_score, 
        "CodeBLEU": codebleu_score,
        "Jaccard": jacard_score,
        "LD": ld_distance,
        "token_LD": token_ld_distance
    }
    # print(result)
    fields = list(result.keys())
    write_dict_csv(save_to, fields, result)
    
def get_similarity_between_files(file1, file2):
    file1_tokens = tokenize_code(read_file(file1))
    file2_tokens = tokenize_code(read_file(file2))
    token_ld_distance = token_LD_distance(file1_tokens, file2_tokens)
    return token_ld_distance

if __name__ == "__main__":
    args = sys.argv[1:]
    file1 = args[0]
    file2 = args[1]
    save_to = args[2]
    file1_tokens = tokenize_code(read_file(file1))
    file2_tokens = tokenize_code(read_file(file2))
    
    bleu_score = bleu(file1_tokens, file2_tokens)
    codebleu_score = codebleu(file1_tokens, file2_tokens)
    jacard_score = get_jaccard(file1_tokens, file2_tokens)
    ld_distance = LD_distance(file1_tokens, file2_tokens)
    token_ld_distance = token_LD_distance(file1_tokens, file2_tokens)
    print(token_ld_distance)
    save_to_file(file1, file2, save_to, bleu_score, codebleu_score, jacard_score, ld_distance, token_ld_distance)