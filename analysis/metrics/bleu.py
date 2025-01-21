from codebleu import calc_codebleu
from nltk.translate.bleu_score import sentence_bleu

def get_bleu(content1, content2):
    bleu_score = sentence_bleu([content1], content2)
    return bleu_score

def get_codebleu(content1, content2):
    codebleu_score = calc_codebleu([" ".join(content1)], [" ".join(content2)], lang="python", weights=(0.25, 0.25, 0.25, 0.25), tokenizer=None)["codebleu"]
    return codebleu_score