**Significant analysis**: original deterministically-success (S) and deterministically-unsuccess(U) cases:

Codenet (200): #Sc = 94; #Uc = 61

Avatar(250): #Sa = 40; #Ua = 170

Total S = 134; U = 231

https://docs.google.com/spreadsheets/d/1wpL5y7xssNHBrSdj6sElgAQ6j335DTlUe9veoXAnk7k/edit#gid=0

**To define complexity**:
Define complexity to show: 1) control flow complexity and 2) data flow complexity
1. Complexity from control flow —- decision points:
- Cognitive complexity (Cog)

2. Complexity from data flow:
- Operators/Operands (Unique/Total numbers of operators and operands, but Halstead Value (Hal) combines them)
- Def-use chain

Combination = Cog + Hal + Total_Use/Max_Use*Total_Def

**TODO:calculate the table; come up with more formula**


**Questions**
> 1- Do we need both cyclomatic complexity and cognitive complexity in the formula? Cog seems to subsume CC. 

Cog subsumes CC (per-function level), no need for CC.
[have modified Cog with adding comprehension]

> 2- Does the AST depth consider the complexity caused by trailing effect? This is specifically important because it challenges the "chain of though" of the LLMs, i.e., breaking down a bigger problem into smaller one. & Can use-def chain length be useful?

There are two files `tmp1.py` and `tmp2.py` with the following difference:
```diff
--- tmp1.py     
+++ tmp2.py    
@@ -3,10 +3,8 @@
 y1 = int(p[1])
 x2 = int(p[2])
 y2 = int(p[3])
-DIF1 = x2 - x1
-DIF2 = y2 - y1
-x3 = x2 - DIF2
-y3 = y2 + DIF1
-x4 = x1 - DIF2
-y4 = y1 + DIF1
+x3 = x2 - ( y2 - y1)
+y3 = y2 + (x2 - x1)
+x4 = x1 - ( y2 - y1)
+y4 = y1 + (x2 - x1)
 print(str(x3) + " " + str(y3) + " " + str(x4) + " " + str(y4))
```

1. Consider the following code `tmp1.py`:
```1.py
p = input().split(" ")
x1 = int(p[0])
y1 = int(p[1])
x2 = int(p[2])
y2 = int(p[3])
DIF1 = x2 - x1
DIF2 = y2 - y1
x3 = x2 - DIF2
y3 = y2 + DIF1
x4 = x1 - DIF2
y4 = y1 + DIF1
print(str(x3) + " " + str(y3) + " " + str(x4) + " " + str(y4))
```

- AST depths of operators:
```
[5, 6, 7, 8, 9, 10, 4, 4, 4, 4, 4, 4]

([['binary_operator', 5], ['binary_operator', 6], ['binary_operator', 7], ['binary_operator', 8], ['binary_operator', 9], ['binary_operator', 10], ['binary_operator', 4], ['binary_operator', 4], ['binary_operator', 4], ['binary_operator', 4], ['binary_operator', 4], ['binary_operator', 4]], 12)
```
- def-use chain:
```
{'p': 4, 'x1': 2, 'y1': 2, 'x2': 2, 'y2': 2, 'DIF1': 2, 'DIF2': 2, 'x3': 1, 'y3': 1, 'x4': 1, 'y4': 1}
```
- Operators/Operands:
```
unique_operators, all_operators, unique_operands, all_operands, (halstead effort)
2, 16, 12, 24, (225)
```

2. The following code `tmp2.py`:
```
p = input().split(" ")
x1 = int(p[0])
y1 = int(p[1])
x2 = int(p[2])
y2 = int(p[3])
x3 = x2 - ( y2 - y1)
y3 = y2 + (x2 - x1)
x4 = x1 - ( y2 - y1)
y4 = y1 + (x2 - x1)
print(str(x3) + " " + str(y3) + " " + str(x4) + " " + str(y4))
```
- AST depths of operators:
```
[5, 6, 7, 8, 9, 10, 4, 6, 4, 6, 4, 6, 4, 6] #

([['binary_operator', 5], ['binary_operator', 6], ['binary_operator', 7], ['binary_operator', 8], ['binary_operator', 9], ['binary_operator', 10], ['binary_operator', 4], ['binary_operator', 6], ['binary_operator', 4], ['binary_operator', 6], ['binary_operator', 4], ['binary_operator', 6], ['binary_operator', 4], ['binary_operator', 6]], 12)
```
- def-use chain:
```
{'p': 4, 'x1': 3, 'y1': 3, 'x2': 3, 'y2': 3, 'x3': 1, 'y3': 1, 'x4': 1, 'y4': 1}
```
- Operators/Operands:
```
unique_operators, all_operators, unique_operands, all_operands, (halstead effort)
2, 18, 14, 28, (282)
```

Overall:
- The average ast depths for each operator is higher
- The length of def-use is different, max `use` is higher 
- Tricky to consider operators locations in ast, ignore them.

/home/yang/Benchmark/tool/metrics/statistics/create_functions/all.csv

> 3- What would be the difference between counting the number of operators and operands compared to considering their locations?
We should consider `the number of operators and operands` and `def-use`, but not focus on operators locations.
Locations(depths) can show the priority of operators, but this is not necessary to impacting complexity

```diff
--- tmp3.py     
+++ tmp4.py     
@@ -1,4 +1,4 @@
 a = 1
 b = 2
 c = 3
-D = a * b + c  + (b - a)
+D = a - b + c - b + a
```
Lengths for `tmp3.py`: [4, 6, 5, 6]

Lengths for `tmp4.py`: [4, 5, 6, 7]
