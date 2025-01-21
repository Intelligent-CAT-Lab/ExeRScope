cd analysis
echo "**Overall Performaces of LLMs**"
echo "RUNNING parse_results.sh"
bash parse_results.sh

echo "**Analyzing Program Constructs...**"
echo "RUNNING analyze_constructs.sh"
bash analyze_constructs.sh
echo "Find reports under /Experiment_Results/figures/constructs"

echo "**Analyzing Program Complexity...**"
echo "RUNNING analyze_complexity.sh"
bash analyze_complexity.sh
echo "Find reports under /Experiment_Results/figures/program_complexity"

echo "**Analyzing Dynamic Properties...**"
echo "RUNNING analyze_dynamic.sh"
bash analyze_dynamic.sh
echo "Find reports under /Experiment_Results/figures/dynamic_property"

echo "**Analyzing Output Variable Types...**"
echo "RUNNING analyze_types.sh"
bash analyze_types.sh
echo "Find reports under /Experiment_Results/figures/variable_types"