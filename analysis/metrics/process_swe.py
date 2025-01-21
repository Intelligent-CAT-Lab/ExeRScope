import jsonlines

repos = {}

def get_modified_file(patch):
    files = []
    for line in patch.split("\n"):
        if line.startswith("diff --git "):
            file = line.split(" ")[-1].replace("b/", "", 1)
            if file not in files:
                files.append(file)
    return files

with jsonlines.open("/home/yang/Benchmark/dataset/original/swe-bench.jsonl") as file:
    data = list(file.iter())
    for line in data:
        # print(line.keys())
        short_name = line["repo"]
        environment_setup_commit = line["environment_setup_commit"]
        patch = line["patch"]
        repo = "https://github.com/" + short_name
        if repo not in repos:
            repos[repo] = {
                "repo": repo,
                "sha_files": {}
            }
        if environment_setup_commit not in repos[repo]["sha_files"]:
            repos[repo]["sha_files"][environment_setup_commit] = []
        for file in get_modified_file(patch):
            if file not in repos[repo]["sha_files"][environment_setup_commit]:
                repos[repo]["sha_files"][environment_setup_commit].append(file)
    for repo in repos:
        for sha in repos[repo]["sha_files"]:
            for file in repos[repo]["sha_files"][sha]:
                print("{},{},{}".format(repo, sha, file))