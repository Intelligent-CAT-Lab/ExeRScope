ProgramIDCSV=$1
OuputDir=$2
ProjectDir=$3

echo STARTING at $(date)
git rev-parse HEAD
timeStamp=$(echo -n $(date "+%Y-%m-%d %H:%M:%S") | shasum | cut -f 1 -d " ")

MainDir=/home/yang/Benchmark/tool/metrics
LogDir=${MainDir}/${OuputDir}/${timeStamp}
ResultDir=${MainDir}/${OuputDir}/${timeStamp}/CSV
Projects=${MainDir}/${ProjectDir}

mkdir -p ${ResultDir}
mkdir -p ${LogDir}
mkdir -p ${Projects}
ResultCSV=${ResultDir}/swe_complexity.csv
echo "File, Base complexity, Predicates with operators, Nested levels, Variable max distance(sum), Variable max distance(average), Complex code structures, Third-Party calls, Inter_dependencies, Intra_dependencies, Final value, Log" > ${ResultCSV}

process_line() {
    local url="$1"
    local sha="$2"
    local file="$3"
    
    local repo_name=$(basename $url .git)

    cd ${Projects}
    if [ ! -d "$repo_name" ]; then
        git clone $url
    fi

    cd $repo_name
    git checkout $sha
    timeout 60 python3 /home/yang/Benchmark/tool/metrics/my_metric.py $file ${LogDir} ${ResultCSV}
    cd ..
}

while IFS=',' read -r url sha file; do
    echo "Processing file: $file in $url at commit $sha"
    process_line "$url" "$sha" "$file"
done < ${ProgramIDCSV}


echo END at $(date)
