example_java = '''
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Main {

    public static void main(String[] args) {
        try {
            InputStreamReader isr = new InputStreamReader(System.in);
            BufferedReader br = new BufferedReader(isr);
            String strArr[] = br.readLine().split(" ");

            int n = Integer.parseInt(strArr[0]);
            int a = Integer.parseInt(strArr[1]);
            int b = Integer.parseInt(strArr[2]);
            int answer = 0;

            for (int i = 1; i < n + 1; i++) {
                int num = i;
                int sum = 0;

                while (num != 0) {
                        sum += num % 10;
                        num /= 10;
                }

                if (sum >= a && sum <= b ) {
                        answer = answer + i;
                }
            }
            System.out.println(answer);
            } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
'''

example_python = '''
N, A, B = map(int, input().split())
sum_1 = 0
for i in range(1,N+1):
    sum_order = 0
    i_str = str(i)
    n = len(i_str)
    for j in range(0,n):
        sum_order += int(i_str[j])
    if A <= sum_order <= B:
        sum_1 += i
print(sum_1)
'''

example_python_class='''
import unittest
import itertools

class ArrangementCalculator:
    def __init__(self, datas):
        self.datas = datas

    @staticmethod
    def count(n, m=None):
        if m is None or n == m:
            return ArrangementCalculator.factorial(n)
        else:
            return ArrangementCalculator.factorial(n) // ArrangementCalculator.factorial(n - m)

    @staticmethod
    def count_all(n):
        total = 0
        for i in range(1, n + 1):
            total += ArrangementCalculator.count(n, i)
        return total

    def select(self, m=None):
        if m is None:
            m = len(self.datas)
        result = []
        for permutation in itertools.permutations(self.datas, m):
            result.append(list(permutation))
        return result

    def select_all(self):
        result = []
        for i in range(1, len(self.datas) + 1):
            result.extend(self.select(i))
        return result

    @staticmethod
    def factorial(n):
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result
class Test(unittest.TestCase):
    def test(self):
            res = ArrangementCalculator.factorial(6)
            return res
'''
example_python_function = '''
def sum_of_integer(N, A, B):
    sum_1 = 0
    for i in range(1,N+1):
        sum_order = 0
        i_str = str(i)
        n = len(i_str)
        for j in range(0,n):
            sum_order += int(i_str[j])
        if A <= sum_order <= B:
            sum_1 += i
    return sum_1
'''

example_python_cruxeval = '''
def f(s):
    return s + "a"
'''

format_requirement = """
First analyze step by step about how the code processes the input to generate the output. 
Then print the output of the code based on your analysis.

Follow the following format:
<<<Analysis>>>
{YOUR ANALYSIS}
<<<Output>>>
{OUTPUT}
[END-OF-RESPONSE]
"""

example_reasoning_java = """
<<<Analysis>>>
The variable n, variable a and variable b are initialized with 20, 2 and 5 respectively according to the input. And variable sum is initialized with 0.
It enters a for loop and it iterates from 1 to 20 to check each integer i in this range. The value of variable i is also passed to variable num.
Inside the for loop, it calculates the sum of the digits of the current interger num by repeatedlly extracting the digits of number with a while loop and adding it to variable sum.
Then it checks if the calculated variable sum falls within the range [2, 5]. If it does, it adds the current interger i to variable answer. The condition is met when i is 2,3,4,5,11,12,13,14 and 20.
After the loop finishes, it print the fianl value of variable answer as output, which is 84.
<<<Output>>>
84
[END-OF-RESPONSE]
"""

example_reasoning_python="""
<<<Analysis>>>
The variable N, variable A and variable B are initialized to 20, 2 and 5, respectively.
variable sum_1 is initialized to 0, which will be used to accumulate the sum of numbers meeting the condition.
The code then enters a loop that iterates from 1 to N (inclusive), meaning it will consider numbers from 1 to 20.
For each number i in this range, it calculates the sum of its digits and stores it in sum_order.
The code checks if sum_order is within the range [A, B], which is [2, 5] in this case. If it is, it adds the current number i to sum_1. The condition is met when i is 2,3,4,5,11,12,13,14 and 20.
After the loop finishes, the code prints the final value of sum_1, which is 84.
<<<Output>>>
84
[END-OF-RESPONSE]
"""

example_reasoning_python_cruxeval = """
The function f takes a string s as input and returns the concatenation of s with the string "a".
To determine the output of executing the function f on the input "hi", we need to concatenate "hi" with "a".
Therefore, the output of executing the function f on the input "hi" is "hia".
<<<Output>>>
'hia'
[END-OF-RESPONSE]
"""

example_reasoning_python_classeval="""
Inside the test() method, the ArrangementCalculator.factorial(6) method is invoked. The purpose of this method is to calculate the factorial of a given number n. In this case, n = 6.
Inside the factorial(), the variable result is initialized to 1.
A for loop iterates from 2 to n (which is 6 in this case), multiplying result by each integer in the range.
At the start: result = 1
The first iteration: i=2, result = 1 * 2 = 2
The second iteration: i=3, result = 2 * 3 = 6
The Third iteration: i=4, result = 6 * 4 = 24
The Forth iteration: i=5, result = 24 * 5 = 120
The Sixth iteration: result = 120 * 6 = 720
After the loop completes, the method returns result, which is 720.
<<<Output>>>
720
[END-OF-RESPONSE]
"""

example_input = "20 2 5"
example_input_function = "sum_of_integer(20, 2, 5)"
example_input_cruxeval = 'f("hi")'
example_input_classeval = 'Test.test()'
question_print_output = "What would be the output of code execution given the following input:\n`"
question_return_value = "What would be the return value of "

instruction = """I want you to act as a {language} code executor. I will give you a piece of {language} code and its input. You need to think step by step and then print the output of code execution."""
instruction_classeval = """I want you to act as a Python code executor. I will give you a Python class and you need to predict the return value of a function defined in the class. You need to think step by step and then print the output of code execution."""
def create_prompt_magicoder(code, code_input, dataset, pl):
    prompt_role = "You are an exceptionally intelligent coding assistant that consistently delivers accurate and reliable responses to user instructions."
    template = prompt_role + "\n" + "@@ Instruction\n" + "$PROMPT_INSTRUCTION$\n" + "Below is an example:\n<Example>\nConsider the following code\n" + "$EXAMPLE_CODE$" \
        +"[Question]\n" + "$QUESTION$" + "```"+"$EXAMPLE_INPUT$" + "```$?$" + "\n" + format_requirement \
        +"[Answer]\n" + "$EXAMPLE_REASONING$" + "\n</Example>\n" + "Consider the following code\n" + code + "\n" + "[Question]\n" + "$QUESTION$" \
        + "```"+code_input + "```$?$\n" + format_requirement + "\n[Answer]\n@@ Response"
    if pl == 'Java':
        prompt_instruction = instruction.format(language='Java')
        if dataset in ['CodeNet', 'Avatar']:
            prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
            .replace("$EXAMPLE_CODE$", example_java) \
            .replace("$QUESTION$", question_print_output) \
            .replace("$EXAMPLE_INPUT$", example_input) \
            .replace("$EXAMPLE_REASONING$", example_reasoning_java) \
            .replace("$?$", '')
    if pl == 'Python':
        prompt_instruction = instruction.format(language='Python')
        if dataset in ['CodeNet', 'Avatar']:
            prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
            .replace("$EXAMPLE_CODE$", example_python) \
            .replace("$QUESTION$", question_print_output) \
            .replace("$EXAMPLE_INPUT$", example_input) \
            .replace("$EXAMPLE_REASONING$", example_reasoning_python) \
            .replace("$?$", '')
        if dataset in ["mbpp", "humaneval", "HumanEvalFix", "HumanEval_Trans"]:
            prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
            .replace("$EXAMPLE_CODE$", example_python_function) \
            .replace("$QUESTION$", question_return_value) \
            .replace("$EXAMPLE_INPUT$", example_input_function) \
            .replace("$EXAMPLE_REASONING$", example_reasoning_python) \
            .replace("$?$", "?")
        if dataset in ["cruxeval"]:
            prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
            .replace("$EXAMPLE_CODE$", example_python_cruxeval) \
            .replace("$QUESTION$", question_return_value) \
            .replace("$EXAMPLE_INPUT$", example_input_cruxeval) \
            .replace("$EXAMPLE_REASONING$", example_reasoning_python_cruxeval) \
            .replace("$?$", "?")
                   
    return prompt
            
def create_prompt_gpt_codeqwen(code, code_input, dataset, pl):
    template =  "<Instruction> " + "$PROMPT_INSTRUCTION$\n" + "</Instruction>\n" + "Below is an example:\n<Example>\nConsider the following code\n" + "$EXAMPLE_CODE$" \
    + "\n[Question]\n" + "$QUESTION$" + "```"+"$EXAMPLE_INPUT$" + "```$?$" + format_requirement \
    + "[Answer]\n" + "$EXAMPLE_REASONING$" + "\n</Example>\n" + "Consider the following code\n" + code \
    +  "\n" + "[Question]\n" + "$QUESTION$" + "```"+code_input + "```$?$\n" + format_requirement + "\n[Answer]\n"

    if pl == 'Java':
        prompt_instruction = instruction.format(language='Java')
        if dataset in ['CodeNet', 'Avatar']:
            prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
            .replace("$EXAMPLE_CODE$", example_java) \
            .replace("$QUESTION$", question_print_output) \
            .replace("$EXAMPLE_INPUT$", example_input) \
            .replace("$EXAMPLE_REASONING$", example_reasoning_java) \
            .replace("$?$", '')
    if pl == 'Python':
        prompt_instruction = instruction.format(language='Python')
        if dataset in ['CodeNet', 'Avatar']:
            prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
            .replace("$EXAMPLE_CODE$", example_python) \
            .replace("$QUESTION$", question_print_output) \
            .replace("$EXAMPLE_INPUT$", example_input) \
            .replace("$EXAMPLE_REASONING$", example_reasoning_python) \
            .replace("$?$", '')
        if dataset in ["mbpp", "humaneval", "HumanEvalFix", "HumanEval_Trans"]:
            prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
            .replace("$EXAMPLE_CODE$", example_python_function) \
            .replace("$QUESTION$", question_return_value) \
            .replace("$EXAMPLE_INPUT$", example_input_function) \
            .replace("$EXAMPLE_REASONING$", example_reasoning_python) \
            .replace("$?$", "?")
        if dataset in ["cruxeval"]:
            prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
            .replace("$EXAMPLE_CODE$", example_python_cruxeval) \
            .replace("$QUESTION$", question_return_value) \
            .replace("$EXAMPLE_INPUT$", example_input_cruxeval) \
            .replace("$EXAMPLE_REASONING$", example_reasoning_python_cruxeval) \
            .replace("$?$", "?")
        if dataset in ["classeval"]:
            prompt = template.replace("$PROMPT_INSTRUCTION$", instruction_classeval) \
            .replace("$EXAMPLE_CODE$", example_python_class) \
            .replace("$QUESTION$", question_return_value) \
            .replace("$EXAMPLE_INPUT$", example_input_classeval) \
            .replace("$EXAMPLE_REASONING$", example_reasoning_python_classeval) \
            .replace("$?$", "?")              
    return prompt


def create_prompt_codellama(code, code_input, dataset, pl, wo_icl):
    if wo_icl:
        code = code.strip('\n')
        if dataset in ['cruxeval']:
            prompt = f"[INST]\n{code}\nWhat will be the output of {code_input}?\nEnclose the output of code execution between [Output] and [/Output].\n[/INST]"
    else:
        template =  "[INST] " + "$PROMPT_INSTRUCTION$\n" + "[/INST]\n" + "[INST]\nConsider the following code\n<Code>" + "$EXAMPLE_CODE$" \
        + "</Code>\n" + "$QUESTION$" + "```"+"$EXAMPLE_INPUT$" + "```$?$" + format_requirement + "[/INST]\n" \
        + "$EXAMPLE_REASONING$"  + "\nConsider the following code\n" + "<Code>"+code \
        +  "\n</Code>\n"  + "$QUESTION$" + "```"+code_input + "```$?$\n" + format_requirement

        if pl == 'Java':
            prompt_instruction = instruction.format(language='Java')
            if dataset in ['CodeNet', 'Avatar']:
                prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
                .replace("$EXAMPLE_CODE$", example_java) \
                .replace("$QUESTION$", question_print_output) \
                .replace("$EXAMPLE_INPUT$", example_input) \
                .replace("$EXAMPLE_REASONING$", example_reasoning_java) \
                .replace("$?$", '')
        if pl == 'Python':
            prompt_instruction = instruction.format(language='Python')
            if dataset in ['CodeNet', 'Avatar']:
                prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
                .replace("$EXAMPLE_CODE$", example_python) \
                .replace("$QUESTION$", question_print_output) \
                .replace("$EXAMPLE_INPUT$", example_input) \
                .replace("$EXAMPLE_REASONING$", example_reasoning_python) \
                .replace("$?$", '')
            if dataset in ["mbpp", "humaneval", "HumanEvalFix", "HumanEval_Trans"]:
                prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
                .replace("$EXAMPLE_CODE$", example_python_function) \
                .replace("$QUESTION$", question_return_value) \
                .replace("$EXAMPLE_INPUT$", example_input_function) \
                .replace("$EXAMPLE_REASONING$", example_reasoning_python) \
                .replace("$?$", "?")
            if dataset in ["cruxeval"]:
                prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
                .replace("$EXAMPLE_CODE$", example_python_cruxeval) \
                .replace("$QUESTION$", question_return_value) \
                .replace("$EXAMPLE_INPUT$", example_input_cruxeval) \
                .replace("$EXAMPLE_REASONING$", example_reasoning_python_cruxeval) \
                .replace("$?$", "?")  
    return prompt


def create_prompt_deepseekcoder(code, code_input, dataset, pl):
    prompt_role = "You are an AI programming assistant, utilizing the Deepseek Coder model, developed by Deepseek Company, and you only answer questions related to computer science. For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer."
    template = prompt_role + "\n" + "### Instruction\n" + "$PROMPT_INSTRUCTION$\n" + "Below is an example:\n<Example>\nConsider the following code\n<Code>" + "$EXAMPLE_CODE$" +"</Code>\n"\
        + "$QUESTION$" + "```"+"$EXAMPLE_INPUT$" + "```$?$"  + format_requirement \
        + "$EXAMPLE_REASONING$" + "</Example>\n" + "Consider the following code\n" +'<Code>\n'+ code + "\n</Code>\n" + "$QUESTION$" \
        + "```"+code_input + "```$?$\n" + format_requirement + "### Response"
    if pl == 'Java':
        prompt_instruction = instruction.format(language='Java')
        if dataset in ['CodeNet', 'Avatar']:
            prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
            .replace("$EXAMPLE_CODE$", example_java) \
            .replace("$QUESTION$", question_print_output) \
            .replace("$EXAMPLE_INPUT$", example_input) \
            .replace("$EXAMPLE_REASONING$", example_reasoning_java) \
            .replace("$?$", '')
    if pl == 'Python':
        prompt_instruction = instruction.format(language='Python')
        if dataset in ['CodeNet', 'Avatar']:
            prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
            .replace("$EXAMPLE_CODE$", example_python) \
            .replace("$QUESTION$", question_print_output) \
            .replace("$EXAMPLE_INPUT$", example_input) \
            .replace("$EXAMPLE_REASONING$", example_reasoning_python) \
            .replace("$?$", '')
        if dataset in ["mbpp", "humaneval", "HumanEvalFix", "HumanEval_Trans"]:
            prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
            .replace("$EXAMPLE_CODE$", example_python_function) \
            .replace("$QUESTION$", question_return_value) \
            .replace("$EXAMPLE_INPUT$", example_input_function) \
            .replace("$EXAMPLE_REASONING$", example_reasoning_python) \
            .replace("$?$", "?")
        if dataset in ["cruxeval"]:
            prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
            .replace("$EXAMPLE_CODE$", example_python_cruxeval) \
            .replace("$QUESTION$", question_return_value) \
            .replace("$EXAMPLE_INPUT$", example_input_cruxeval) \
            .replace("$EXAMPLE_REASONING$", example_reasoning_python_cruxeval) \
            .replace("$?$", "?")  
    return prompt   

def create_prompt_starcoder(code, code_input, dataset, pl):
    template =  "Consider the following code:\n" + "<Code>" + "$EXAMPLE_CODE$" + "</Code>\n" + "<<<Question>>>\n" \
        +  "$QUESTION$" + "```"+"$EXAMPLE_INPUT$" + "```$?$" \
        + "First analyze step by step about how the code processes the input to generate the output.\nThen print the output of the code based on your analysis." \
        + "$EXAMPLE_REASONING$" \
        + "\nConsider the following code:\n" + "<Code>\n" + code + "\n</Code>\n" + "<<<Question>>>\n" \
        + "$QUESTION$" + "```"+code_input + "```$?$\n" \
        + "First analyze step by step about how the code processes the input.\nThen print the output of the code based on your analysis.\n" \
        + "<<<Analysis>>>"
    if pl == 'Java':
        prompt_instruction = instruction.format(language='Java')
        if dataset in ['CodeNet', 'Avatar']:
            prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
            .replace("$EXAMPLE_CODE$", example_java) \
            .replace("$QUESTION$", question_print_output) \
            .replace("$EXAMPLE_INPUT$", example_input) \
            .replace("$EXAMPLE_REASONING$", example_reasoning_java) \
            .replace("$?$", '')
    if pl == 'Python':
        prompt_instruction = instruction.format(language='Python')
        if dataset in ['CodeNet', 'Avatar']:
            prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
            .replace("$EXAMPLE_CODE$", example_python) \
            .replace("$QUESTION$", question_print_output) \
            .replace("$EXAMPLE_INPUT$", example_input) \
            .replace("$EXAMPLE_REASONING$", example_reasoning_python) \
            .replace("$?$", '')
        if dataset in ["mbpp", "humaneval", "HumanEvalFix", "HumanEval_Trans"]:
            prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
            .replace("$EXAMPLE_CODE$", example_python_function) \
            .replace("$QUESTION$", question_return_value) \
            .replace("$EXAMPLE_INPUT$", example_input_function) \
            .replace("$EXAMPLE_REASONING$", example_reasoning_python) \
            .replace("$?$", "?")
        if dataset in ["cruxeval"]:
            prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
            .replace("$EXAMPLE_CODE$", example_python_cruxeval) \
            .replace("$QUESTION$", question_return_value) \
            .replace("$EXAMPLE_INPUT$", example_input_cruxeval) \
            .replace("$EXAMPLE_REASONING$", example_reasoning_python_cruxeval) \
            .replace("$?$", "?")  
    return prompt    

def create_prompt_wizardcoder(code, code_input, dataset, pl):
    prompt_role = "Below is an instruction that describes a task, paired with an input that provides further context.  Write a response that appropriately completes the request."
    template = prompt = prompt_role + "\n" + "### Instruction:\n" + "$PROMPT_INSTRUCTION$\n" + "Below is an example:\n<Example>\nConsider the following code\n" + "$EXAMPLE_CODE$" \
        +"[Question]\n" + "$QUESTION$" + "```"+"$EXAMPLE_INPUT$" + "```$?$" + "\n" + format_requirement \
        +"[Answer]\n" + "$EXAMPLE_REASONING$" + "\n</Example>\n" + "Consider the following code\n" + code + "\n" + "[Question]\n" + "$QUESTION$" \
        + "```"+code_input + "```$?$\n" + format_requirement + "\n[Answer]\n### Response:"
    if pl == 'Java':
        prompt_instruction = instruction.format(language='Java')
        if dataset in ['CodeNet', 'Avatar']:
            prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
            .replace("$EXAMPLE_CODE$", example_java) \
            .replace("$QUESTION$", question_print_output) \
            .replace("$EXAMPLE_INPUT$", example_input) \
            .replace("$EXAMPLE_REASONING$", example_reasoning_java) \
            .replace("$?$", '')
    if pl == 'Python':
        prompt_instruction = instruction.format(language='Python')
        if dataset in ['CodeNet', 'Avatar']:
            prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
            .replace("$EXAMPLE_CODE$", example_python) \
            .replace("$QUESTION$", question_print_output) \
            .replace("$EXAMPLE_INPUT$", example_input) \
            .replace("$EXAMPLE_REASONING$", example_reasoning_python) \
            .replace("$?$", '')
        if dataset in ["mbpp", "humaneval", "HumanEvalFix"]:
            prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
            .replace("$EXAMPLE_CODE$", example_python_function) \
            .replace("$QUESTION$", question_return_value) \
            .replace("$EXAMPLE_INPUT$", example_input_function) \
            .replace("$EXAMPLE_REASONING$", example_reasoning_python) \
            .replace("$?$", "?")
        if dataset in ["cruxeval"]:
            prompt = template.replace("$PROMPT_INSTRUCTION$", prompt_instruction) \
            .replace("$EXAMPLE_CODE$", example_python_cruxeval) \
            .replace("$QUESTION$", question_return_value) \
            .replace("$EXAMPLE_INPUT$", example_input_cruxeval) \
            .replace("$EXAMPLE_REASONING$", example_reasoning_python_cruxeval) \
            .replace("$?$", "?")  
    return prompt

def create_prompt_codellama_base(code, code_input, dataset, pl, wo_icl):
    code = code.strip('\n')
    if wo_icl:
        if dataset in ['cruxeval']:
            prompt = f"[INST]\n{code}\nWhat will be the output of {code_input}?\n[/INST]"
    return prompt


def create_prompt(model_id, code, code_input, dataset, pl, wo_icl):
    if "Magicoder" in model_id:
        prompt = create_prompt_magicoder(code, code_input, dataset, pl)
    if "gpt" in model_id or 'CodeQwen' in model_id or "gemini" in model_id or "semcoder" in model_id:
        prompt = create_prompt_gpt_codeqwen(code, code_input, dataset, pl)
    # if 'CodeLlama-13b-hf' in model_id:
    #     prompt = create_prompt_codellama_base(code, code_input, dataset, pl, wo_icl)
    if "CodeLlama" in model_id or "Llama-2" in model_id or "Mistral" in model_id:
        prompt = create_prompt_codellama(code, code_input, dataset, pl, wo_icl)
    if "deepseek-coder" in model_id:
        prompt = create_prompt_deepseekcoder(code, code_input, dataset, pl)
    if "starcoder" in model_id:
        prompt = create_prompt_starcoder(code, code_input, dataset, pl)
    if "WizardCoder" in model_id:
        prompt = create_prompt_wizardcoder(code, code_input, dataset, pl)
    return prompt


        
        
