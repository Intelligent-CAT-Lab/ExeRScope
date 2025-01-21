
## Intuition:

### About Cyclomatic Complexity (and other metrics)
Cyclomatic complexity represents linearly independent paths in a program. However it can not fully represent program complexity. It is unfair to use these existing metric to compare different programs when performing tasks with models.


> `CC = E - N + 2 * P` can display inter-procedural dependencies. (But existing tools only calculate based on function-levels, e.g., radon, lizard.)
One thing I do not understand, CC considers linearly independent paths, then why including logical operator??

For example, 
<!-- inter-dependency for program A is more complex than program B (function `r()` is called in A but not in B), CC-A is higher than CC-B: -->

Program A (P = 2): 

`E = 13, N = 13, P = 2. CC = 13 - 13 + 2 * 2 = 4.`
```Python
def t(a, b):
    if a and b:
        print(a)
        
def r(a,b):
    a += b
    return a
        
a, b = 1, 2
if (a + b) > 3:
    t(a,b)
print("done")
```
CFG for Program A:

<img src="tmp1.py.png" width="300" height="400">
<!-- ![CFG](tmp1.py.png) -->


Program B (P = 1):

`E = 15, N = 14, P = 1. CC = 15 - 14 + 2 * 1 = 3.`

```Python
def t(a, b):
    if a and b:
        print(a)
        
def r(a,b):
    a += b
    return a
        
a, b = 1, 2
if (a + b) > 3:
    t(a,b)
    r(a,b)
print("done")
```
CFG for Program B:

<img src="tmp2.py.png" width="300" height="600"> 


### Intuitive Examples to show unfairness
However, cyclomatic complexity and other metrics can not fairly show the complexity of programs. No existing metric can show the complexity of them.

1. Code with nested code structures is harder to understand. --> **Intuition 1: To weigh more on nested code structures.**

- Always failed program: codeforces_32_B.py (CC = 3, HM = 213)
<!-- atcoder_ABC128_C.py (CC = 7, HM = 480):-->
```Python
s = input()
result = [''][0]
i = [0][0]
while i < len(s):
    if s[i] == '.':
        result += ['0'][0]
    else:
        i += [1][0]
        if s[i] == '.':
            result += ['1'][0]
        else:
            result += ['2'][0]
    i += [1][0]
print(result)
```

- Always successful program: s814885508.py (CC = 3, HM = 637)

```Python
def main():
    X, K, D = map(int, input().split())

    r = X // D
    if abs(r) > K:
        print(abs(X) - K * D)
        exit()
    a = X - r * D
    if (K - r) % 2 == 0:
        print(a)
    else:
        print(abs(D - a))

if __name__ == '__main__':
    main()
```

2. Code with comprehension or more "combined" statements are harder. --> **Intuition 2: To consider comprehensive code structures (Also needs to add an operator for this).**

- Always failed program: atcoder_ABC149_B.py (CC = 2, HM = 83)
```Python
cookies = [int(x) for x in input().split()]
leftOver = cookies[0] - cookies[2]
takahashi = max(0, leftOver)
print(str(takahashi) + ' ' +
      (str(cookies[1]) if takahashi > 0 else str(max(0, cookies[1] - abs(leftOver)))))
```

- Always successful program: s000375264.py (CC = 2, HM = 94)

```Python
X, t = map(int, input().split())

if X > t:
    answer = X - t
elif X <= t:
    answer = 0

print(answer)
```

3. Code with complex data structures (Or, advanced features/constructure). --> **Intuition 3: To consider complex data structures.** 

- Always failed program: atcoder_ABC164_D.py (CC=1, HM=294)

```
fail:
yang@maverick:~/Benchmark/dataset$ cat python_avatar/atcoder_ABC164_D.py 
s, l = (input(), 2019)
m, a, r = ([1] + [0] * l, 0, 0)
for i, e in enumerate(s[:: - 1]):
    a += int(e) * pow(10, i, l)
    r += m[a % l]
    m[a % l] += 1
print(r)
```

- Always successful program: codeforces_379_A.py (CC=2, HM=781)

```Python
import re
candeleIntere, b = map(int, input().split())
s = 0
restoSciolte = 0
while candeleIntere > 0 or restoSciolte >= b:
    candeleIntere += restoSciolte // b
    restoSciolte %= b
    s += candeleIntere
    restoSciolte += candeleIntere % b
    candeleIntere //= b
print(s)
```

4. Hard to understand code/third party: s763208424.py (CC=2, HM=72)

```Python
from math import floor
from heapq import heappush, heappop
n, m = map(int, input().split())
a = []
for i in map(int, input().split()):
    heappush(a, -i)

def dis(x, y): return x // 2**y

for _ in range(m):
    heappush(a, -dis(-heappop(a), 1))
print(-sum(a))
```
atcoder_ABC150_C.py (CC=0, HM=15)

```Python
import itertools
n = int(input())
orig = list(itertools.permutations(list(range(1, n + 1))))
p = tuple(map(int, input().split()))
q = tuple(map(int, input().split()))
pn = orig.index(p)
qn = orig.index(q)
print(abs(pn - qn))
```

5. Dataflow and trailing effect

atcoder_ABC127_B.py (CC=1, HM=389):

```Python
r, D, x = map(int, input().split())
for i in range(2, 12):
    print(int((r ** (i - 1)) * (x + D / (1 - r)) - D / (1 - r)))
```
```
r -> (r -> (BinOp -> (BinOp -> (BinOp -> (Call -> (Call -> ()))))), r -> (BinOp -> (BinOp -> (BinOp -> (BinOp -> (BinOp -> (Call -> (Call -> ()))))))), r -> (BinOp -> (BinOp -> (BinOp -> (Call -> (Call -> ()))))))
D -> (D -> (BinOp -> (BinOp -> (BinOp -> (BinOp -> (Call -> (Call -> ())))))), D -> (BinOp -> (BinOp -> (Call -> (Call -> ())))))
x -> (x -> (BinOp -> (BinOp -> (BinOp -> (Call -> (Call -> ()))))))
i -> (i -> (BinOp -> (BinOp -> (BinOp -> (BinOp -> (Call -> (Call -> ())))))))
{'r': 3, 'D': 2, 'x': 1, 'i': 1}
```

```
r, D, x = map(int, input().split()) 
for i in range(2, 12): 
    a = (r ** (i - 1))
    b = (1 - r)
    c = (x + D / b)
    d = D / b
    e = a * c - d
    print(int(e))
```
```
r -> (r -> (BinOp -> ()), r -> (BinOp -> ()))
D -> (D -> (BinOp -> (BinOp -> ())), D -> (BinOp -> ()))
x -> (x -> (BinOp -> ()))
i -> (i -> (BinOp -> (BinOp -> ())))
a -> (a -> (BinOp -> (BinOp -> ())))
b -> (b -> (BinOp -> (BinOp -> ())), b -> (BinOp -> ()))
c -> (c -> (BinOp -> (BinOp -> ())))
d -> (d -> (BinOp -> ()))
e -> (e -> (Call -> (Call -> ())))
{'r': 2, 'D': 2, 'x': 1, 'i': 1, 'a': 1, 'b': 2, 'c': 1, 'd': 1, 'e': 1}
```


<!-- 
5. 

```
fail:
yang@maverick:~/Benchmark/dataset$ cat python_codenet/s828550015.py 
x, y, a, b, c = map(int, input().split())
p = sorted([int(i) for i in input().split()], reverse=True)[:x]
q = sorted([int(i) for i in input().split()], reverse=True)[:y]
r = sorted([int(i) for i in input().split()], reverse=True)
pq = sorted(p+q)
for i in range(min(x+y, a+b, c)):
    if pq[i] < r[i]:
        pq[i] = r[i]
print(sum(pq))

pass:

``` -->
