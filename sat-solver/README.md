# 3-SAT solvers (a side quest)

Nothing to do with container redemption. This folder holds two small SAT solvers written to see, first-hand, why nobody has collected the $1 million prize for P versus NP. Written and measured November 22, 2026.

| File | What it is |
| --- | --- |
| [sat3.py](https://github.com/wbp318/georgia-business-2027/blob/main/sat-solver/sat3.py) | Plain backtracking search (DPLL) with unit propagation |
| [cdcl.py](https://github.com/wbp318/georgia-business-2027/blob/main/sat-solver/cdcl.py) | The same search with clause learning, backjumping, activity-based branching, phase saving, restarts, and learned-clause cleanup (CDCL), plus a counting check that runs once before search |
| [structured.py](https://github.com/wbp318/georgia-business-2027/blob/main/sat-solver/structured.py) | Runs both solvers on four families of structured problems |
| [PARITY-PLAN.md](https://github.com/wbp318/georgia-business-2027/blob/main/sat-solver/PARITY-PLAN.md) | The plan for the next step: a parity check using Gaussian elimination |

All three programs are pure Python with no dependencies.

## Random formulas: what the test does

1. **Correctness.** Each solver is checked against brute force on small random formulas, and every satisfying assignment it returns is checked against the formula.
2. **Scaling.** Both solvers run on the same random 3-SAT formulas at 4.26 clauses per variable, the ratio where random formulas are hardest. Sizes grow by 25 variables until the median time for one size passes the budget.

## Random formulas: results

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

## Structured problems

Random formulas are close to the worst case for clause learning. These four families have the kind of structure real problems have. One run per size for the adder and pigeonhole families and the median of three for the other two, with a 10-second limit per run. After a solver times out, larger sizes are skipped for it.

**Adder equivalence (unsatisfiable).** Two different gate-level designs of an n-bit adder, with a claim that some output differs. This is circuit verification in miniature.

| Bits | Variables | DPLL decisions | DPLL seconds | CDCL conflicts | CDCL seconds |
| --- | --- | --- | --- | --- | --- |
| 2 | 32 | 31 | 0.001 | 27 | 0.002 |
| 4 | 62 | 511 | 0.027 | 95 | 0.007 |
| 6 | 92 | 8,191 | 0.251 | 176 | 0.009 |
| 8 | 122 | 131,071 | 3.789 | 375 | 0.022 |
| 12 | 182 | timeout | over 10 | 645 | 0.061 |
| 16 | 242 | skipped | | 545 | 0.047 |
| 24 | 362 | skipped | | 603 | 0.083 |
| 32 | 482 | skipped | | 679 | 0.174 |

**Buried contradiction (unsatisfiable).** Five pigeons in four holes, hidden among independent, easily satisfied blocks of 12 variables that share nothing with it.

| Blocks | Variables | DPLL decisions | DPLL seconds | CDCL conflicts | CDCL seconds |
| --- | --- | --- | --- | --- | --- |
| 1 | 32 | 2,344 | 0.019 | 29 | 0.001 |
| 2 | 44 | 436,133 | 3.610 | 29 | 0.001 |
| 3 | 56 | timeout | over 10 | 30 | 0.001 |
| 4 | 68 | skipped | | 30 | 0.001 |
| 8 | 116 | skipped | | 33 | 0.001 |
| 16 | 212 | skipped | | 36 | 0.002 |
| 32 | 404 | skipped | | 49 | 0.005 |

**Latin square completion (satisfiable).** Fill in a Latin square with 42% of its cells blank, a generalized Sudoku.

| Order | Variables | DPLL decisions | DPLL seconds | CDCL conflicts | CDCL seconds |
| --- | --- | --- | --- | --- | --- |
| 6 | 216 | 0 | 0.001 | 0 | 0.001 |
| 9 | 729 | 2 | 0.007 | 0 | 0.004 |
| 12 | 1,728 | 4 | 0.024 | 0 | 0.015 |
| 15 | 3,375 | 19 | 0.085 | 8 | 0.064 |
| 18 | 5,832 | 7 | 0.258 | 64 | 0.143 |
| 21 | 9,261 | timeout | over 10 | 671 | 1.054 |

**Pigeonhole (unsatisfiable).** One more pigeon than holes, on its own, with variable names and clause order scrambled. The CDCL column is shown with its counting check off and on.

| Holes | Variables | DPLL decisions | DPLL seconds | CDCL conflicts, check off | CDCL seconds, check off | CDCL conflicts, check on | CDCL seconds, check on |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4 | 20 | 29 | 0.000 | 32 | 0.001 | 0 | 0.000 |
| 5 | 30 | 193 | 0.002 | 148 | 0.006 | 0 | 0.000 |
| 6 | 42 | 1,777 | 0.023 | 991 | 0.114 | 0 | 0.000 |
| 7 | 56 | 16,364 | 0.227 | 8,096 | 1.897 | 0 | 0.000 |
| 8 | 72 | 139,200 | 2.240 | timeout | over 10 | 0 | 0.001 |
| 9 | 90 | timeout | over 10 | skipped | | 0 | 0.001 |
| 12 | 156 | skipped | | skipped | | 0 | 0.002 |
| 20 | 420 | skipped | | skipped | | 0 | 0.008 |
| 40 | 1,640 | skipped | | skipped | | 0 | 0.071 |
| 60 | 3,660 | skipped | | skipped | | 0 | 0.275 |

The adder, buried-contradiction, and Latin square tables above were measured before the counting check existed. With it on, the adder and Latin square numbers are unchanged, and the buried contradiction is refuted with no search at every size.

What these show:

- **Adder:** DPLL's work multiplies by 16 for every two bits (511, 8,191, 131,071 are 2^9, 2^13, 2^17, each minus one). CDCL's conflicts stay under 700 from 12 to 32 bits. It learns that each bit position matches and never re-proves it.
- **Buried contradiction:** DPLL re-proves the same small contradiction under every way of satisfying the unrelated blocks, so two blocks cost about 190 times one. CDCL learns clauses that mention only the pigeons and is unaffected by the clutter: 29 conflicts at one block, 49 at thirty-two.
- **Latin square:** both are fine until order 21, where most DPLL runs get stuck in a bad early choice. Restarts and learning get CDCL out in about a second.
- **Pigeonhole:** structure is not the same as easy. By search alone both solvers grow roughly ten-fold per hole, and CDCL's extra bookkeeping makes it the slower of the two. This family is proven to need exponentially long proofs in the reasoning system clause learning uses, so no amount of tuning the search fixes it. It takes a different kind of reasoning.

## Beating pigeonhole: the counting check

Clause learning cannot count. The fix is to count before searching:

1. **Find at-most-one groups.** A two-literal clause says two things cannot both be true. A set of literals where every pair clashes that way can have at most one member true. For pigeonhole, each hole is one such group.
2. **Pick clauses that share no literals.** Each needs a true literal of its own. For pigeonhole, these are the pigeons.
3. **Match clauses to groups.** If the clauses cannot all be given distinct groups, the formula is unsatisfiable. Sixty-one pigeons cannot be matched to sixty holes.

That replaces an exponential search with a polynomial matching: 60 holes, with 3,660 variables and 109,861 clauses, takes 0.28 seconds and zero conflicts.

It was checked for soundness on 7,000 small formulas against brute force (4,000 random and 3,000 assignment-style ones with missing constraints, noise clauses, and flipped signs): the solver's answer always matched, and the check never fired on a satisfiable formula.

What it does not do:

- **It is a special-purpose rule, not a general speed-up.** It fired on only 21 of the 1,707 unsatisfiable assignment-style test formulas and on none of the random ones. Most contradictions are not counting arguments visible at the top level.
- **It only sees one encoding.** If the at-most-one constraints are written another way (for example with helper variables instead of pairwise clauses), or the pigeonhole only appears after some decisions, the check finds nothing and the solver falls back to exponential search.
- **There is always another family.** Parity constraints are the next classic one that defeats clause learning, and they need yet another technique (Gaussian elimination). Every solver is a collection of such techniques, and each one has hard inputs left over.

## Why this wins no prize

A proof that P = NP needs an algorithm that is fast on every possible input, with a proof of that bound. A solver that looks fast in tests proves nothing, and these don't even look fast. Clause learning does far better on structured problems than on random ones, as the tables above show, but every known solver has inputs that take exponential time. Adding the counting check moved pigeonhole from that list to the solved list and left the list non-empty.

## Run it

```
python sat-solver/sat3.py 6
python sat-solver/cdcl.py 10 200
python sat-solver/structured.py 10
```

The first number is the median-seconds budget at which the size ladder stops. For cdcl.py, the second is the largest size at which DPLL is also run for comparison. The full CDCL comparison takes several minutes. For structured.py the number is the time limit per run in seconds; add family names (adder, buried, latin, pigeon) to run only those, and --no-counting to switch the counting check off.
