# 3-SAT solvers (a side quest)

Nothing to do with container redemption. This folder holds two small 3-SAT solvers written to see, first-hand, why nobody has collected the $1 million prize for P versus NP. Written and measured November 22, 2026.

| File | What it is |
| --- | --- |
| [sat3.py](https://github.com/wbp318/georgia-business-2027/blob/main/sat-solver/sat3.py) | Plain backtracking search (DPLL) with unit propagation |
| [cdcl.py](https://github.com/wbp318/georgia-business-2027/blob/main/sat-solver/cdcl.py) | The same search with clause learning, backjumping, activity-based branching, phase saving, restarts, and learned-clause cleanup (CDCL) |

Both are pure Python with no dependencies.

## What the test does

1. **Correctness.** Each solver is checked against brute force on small random formulas, and every satisfying assignment it returns is checked against the formula.
2. **Scaling.** Both solvers run on the same random 3-SAT formulas at 4.26 clauses per variable, the ratio where random formulas are hardest. Sizes grow by 25 variables until the median time for one size passes the budget.

## Results

Fifteen formulas per size. Times are medians on one laptop, so the growth matters, not the absolute numbers.

| Variables | DPLL decisions | DPLL seconds | CDCL conflicts | CDCL seconds |
| --- | --- | --- | --- | --- |
| 50 | 57 | 0.002 | 60 | 0.003 |
| 75 | 190 | 0.006 | 141 | 0.009 |
| 100 | 820 | 0.042 | 378 | 0.032 |
| 125 | 2,843 | 0.130 | 852 | 0.081 |
| 150 | 14,477 | 0.659 | 2,329 | 0.339 |
| 175 | 37,573 | 1.662 | 4,288 | 0.658 |
| 200 | 230,861 | 13.522 | 13,849 | 2.717 |
| 225 | not run | not run | 49,687 | 16.420 |

- **Correctness:** DPLL matched brute force on 400 small formulas and CDCL on 600. The two solvers gave the same answer on every formula both ran.
- **Clause learning helps.** At 200 variables CDCL is about five times faster and does about a sixteenth of the search.
- **It is still exponential.** In an earlier DPLL-only run, time doubled about every 12 variables. CDCL's time doubles about every 14.5 variables. Learning stretches the curve; it does not flatten it.
- **Extrapolated from eight points, so order-of-magnitude only:** CDCL would need about two months at 500 variables and about four billion years at 1,000.

## Why this wins no prize

A proof that P = NP needs an algorithm that is fast on every possible input, with a proof of that bound. A solver that looks fast in tests proves nothing, and these don't even look fast. Clause learning does much better on structured problems from industry than on random formulas like these, but every known solver has inputs that take exponential time.

## Run it

```
python sat-solver/sat3.py 6
python sat-solver/cdcl.py 10 200
```

The first number is the median-seconds budget at which the size ladder stops. For cdcl.py, the second is the largest size at which DPLL is also run for comparison. The full CDCL comparison takes several minutes.
