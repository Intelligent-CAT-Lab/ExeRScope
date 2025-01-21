import beniget, gast as ast
import sys
import utils

def get_def_use(code):
    root = ast.parse(code)
    duc = beniget.DefUseChains()
    duc.visit(root)
    all_chains = {}
    idx = 0
    for node in root.body:
        for head in duc.locals[node]:
            name = head.name() + "_func" + str(idx)
            if name not in all_chains:
                all_chains[name] = []
            all_chains[name].append(len(head.users()))
            # print(head)
        idx += 1
    for head in duc.locals[root]:
        name = head.name()
        if name not in all_chains:
            all_chains[name] = []
        all_chains[name].append(len(head.users()))
        # print(head)
    return all_chains
if __name__ == "__main__":
    file1 = sys.argv[1]
    content = utils.clear_string(utils.read_file(file1))
    print(get_def_use(content))