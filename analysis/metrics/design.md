# Metrics Design

## Existing Metrics 

| Code Structure | Cyclomatic Complexity (CC) | Cognitive Complexity (CoG) | Halstead Metric (HM) | Comments | 
|--|--|--|--|--|
| **Control Flow (decision points)** |
| `if` | Y (+1) | Y (+1) | - | An `if` is a single desicion. |
| `elif` | Y (+1) | Y (+1) | - | `elif` adds a decision. |
| `else` | - | Y (+1) | - | CC considers the decision is made at `if` and `else` does not increase decisions. |
| `for` | Y (+1) | Y (+1) | - | A desicion at the start of the loop. |
| `while` | Y (+1) | Y (+1) | - | |
| `continue` | - | Y (+1) | - | We should add `continue`. |
| `break` | - | Y(+1) | - | We should add `break`. | 
| `except` in `try-except-(else)-(finally)` | Y (+1) | Y (+1) | - | `except` adds a conditional path. |
| `else` in `try-except-(else)-(finally)` | - | - | - | 
| `finally` in `try-except-(else)-(finally)` | - | - | - | `finally` is always executed after `try` no matter if there's exception. We should not count it since no new branch created. |
| `Comprehension` | Y (+1) | - | - | A `list/set/dict` comprehension of generator expression is equivalent to a `for` loop. CoG ignores this, but we should add it. |
| **Nested Code Structures** |
| Nested `if` | - | Y (+nested_level) | - | |
| Nested `for` | - | Y (+nested_level) | - | |
| Nested `while` | - | Y (+nested_level) | - | |
| **Operators and Operands** |
| Boolean Operator | Y (+1) | Y (+1) | Y | `and` and `or` adds decision points. But some other operators (e.g., below `not`, `in`) also add decision points, why not include them?? |
| Binary Operator | - | - | Y |
| Unary Operator | - | - | Y  |
| **Advanced Features** |
| Complex data structures | - | - | - | |
<!-- | **Function Dependencies** |
| Inter | Y | - | - | |
| Intra | - | - | - | |
| **Data Flow** |
| Def-Use| - | - | - | | -->
<!-- | **Others** |
| Compare Operator | - | - | Y |
| Operands | - | - | Y | |
| Lines of Code (LoC) | - | - | - | CC and CoG are function-level, CC will increase one for each function definition. |
| AST Depth | - | - | - | | -->
<!-- `else` is executed if no exception. Both CC and Cog do not consider the `else`, but it should be considered as a branch?? |  -->
<!-- | `assert` | Y (+1) | - | - | CC considers it as an equally conditional statement. | -->
<!-- | Nested `else, elif` | - | - | - | Nested level already added at the `if` | -->
<!-- | Nested `except` in `try-except-(else)-(finally)` | - | Y (+nested_level) | - | | -->
 <!-- `Add | Sub | Mult | MatMult | Div | Mod | Pow | LShift | RShift | BitOr | BitXor | BitAnd | FloorDiv`  | -->
<!-- | `Invert | Not | UAdd | USub` | -->
<!-- | `Eq | NotEq | Lt | LtE | Gt | GtE | Is | IsNot | In | NotIn` | -->
<!-- | Concurrency | - | - | - | |
| Decorator | - | - | - | | -->
<!-- | Caller-Callee | - | - | - | | -->
<!-- | Data Flow Dependencies | - | - | - | | -->
Links:
- cyclomatic complexity: https://radon.readthedocs.io/en/latest/intro.html
- cyclomatic complexity density: https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=106988
- cognitive complexity: https://dl.acm.org/doi/pdf/10.1145/3194164.3194186
- https://www.sonarsource.com/blog/cognitive-complexity-because-testability-understandability/
- operators: https://docs.python.org/3/library/ast.html
- [TSE 2023] [How much does software complexity matter for maintainenance Productivity? The link between team instability and diversity.](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=9953033)
- [ICST 2022] https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=9787846
