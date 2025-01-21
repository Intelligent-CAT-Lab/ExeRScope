import sys
import utils
from datasketch import MinHash
from utils import clear_string as clear_string

def jaccard(file1, file2):
    content1 = set(clear_string(utils.read_file(file1)).split(" "))
    content2 = set(clear_string(utils.read_file(file2)).split(" "))
    m1, m2 = MinHash(), MinHash()
    for d in content1:
        m1.update(d.encode('utf8'))
    for d in content2:
        m2.update(d.encode('utf8'))
    print("Estimated Jaccard for data1 and data2 is", m1.jaccard(m2))

    s1 = set(content1)
    s2 = set(content2)
    actual_jaccard = float(len(s1.intersection(s2)))/float(len(s1.union(s2)))
    return actual_jaccard
    # print("Actual Jaccard for data1 and data2 is", actual_jaccard)
    
def jaccard_content(content1, content2):
    m1, m2 = MinHash(), MinHash()
    for d in content1:
        m1.update(d.encode('utf8'))
    for d in content2:
        m2.update(d.encode('utf8'))
    print("Estimated Jaccard for data1 and data2 is", m1.jaccard(m2))

    s1 = set(content1)
    s2 = set(content2)
    actual_jaccard = float(len(s1.intersection(s2)))/float(len(s1.union(s2)))
    return actual_jaccard

def jaccard_tokens(tokens1, tokens2):
    s1 = set(tokens1)
    s2 = set(tokens2)
    actual_jaccard = float(len(s1.intersection(s2)))/float(len(s1.union(s2)))
    return actual_jaccard

if __name__ == "__main__":
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    print(jaccard(file1, file2))