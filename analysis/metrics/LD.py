import sys
import utils
from Levenshtein import distance
from utils import clear_string as clear_string

def cal_LD(content1, content2):
    return distance(clear_string(content1), clear_string(content2))

def cal_LD_file(file1, file2):
    content1 = clear_string(utils.read_file(file1))
    content2 = clear_string(utils.read_file(file2))
    print(content1)
    print(content2)
    return distance(content1, content2)

def get_LD_similarity(content1, content2):
    #return 1 - distance(content1, content2)/max(len(content1), len(content2))
    return distance(content1, content2)

if __name__ == "__main__":
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    print(cal_LD_file(file1, file2), similarity(file1, file2))