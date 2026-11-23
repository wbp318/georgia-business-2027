# Plan: make the SAT solver beat parity

Status: planned, not yet built. Written November 22, 2026.

## Why

The learning solver in [cdcl.py](https://github.com/wbp318/georgia-business-2027/blob/main/sat-solver/cdcl.py) now refutes pigeonhole through a counting check, and the [README](https://github.com/wbp318/georgia-business-2027/blob/main/sat-solver/README.md) names parity constraints as the next family that defeats clause learning. Parity (XOR) formulas are proven to need exponentially long proofs in the reasoning system clause learning uses. They are also just linear equations over 0 and 1, which Gaussian elimination solves in polynomial time. The goal is to add that technique, measure it with the check on and off, and write it up with its limits, the same way pigeonhole was done.

## Step 1: parity check in the learning solver

A new check that runs once before the search, next to the counting check, with a switch to turn it off.

1. **Find XOR constraints.** Group clauses by their set of variables (2 to 6 variables). A group counts as "x1 xor ... xk = b" only if every one of the 2^(k-1) clauses that encoding needs is present. A partial set is ignored, so every equation used is implied by the formula. That is what keeps the check sound.
2. **Substitute** variables already fixed before the search starts.
3. **Gaussian elimination** over 0 and 1, with each equation stored as one integer bitmask so a row operation is a single XOR.
4. **Outcomes:**
   - A row reading 0 = 1 means the formula is unsatisfiable.
   - A row with a single variable forces that variable, and the solver sets it before searching.
   - Otherwise nothing changes and the search runs as before.

## Step 2: parity benchmarks

Three new families in [structured.py](https://github.com/wbp318/georgia-business-2027/blob/main/sat-solver/structured.py), all with variable names, clause order, and literal order scrambled:

| Family | Answer | What it is |
| --- | --- | --- |
| tseitin | Unsatisfiable | A random connected graph with three edges at every vertex. One variable per edge. Each vertex says the xor of its edges equals its charge, and the charges add up to an odd number. The classic parity family that is hard for clause learning. |
| chain | Unsatisfiable | The same variables xored together in two different random orders through helper variables, one total set to 0 and the other to 1. Tests that the check works when the parity is spread across helper variables. |
| tseitin-sat | Satisfiable | The tseitin graphs with an even total charge, to measure what happens when the check cannot refute. |

A flag switches the parity check off, like the existing one for the counting check. Sizes get chosen after a first run so the check-off column reaches its 10-second timeout.

## Step 3: verify

- **Soundness against brute force:** several thousand small formulas mixing full XOR encodings, XOR encodings with one clause removed, random three-literal clauses, and unit clauses. The solver's answer must always match, every returned model must satisfy the formula, and the check must never fire on a satisfiable formula. Count how often it fires on unsatisfiable ones.
- Re-run the existing correctness test and the four existing families to confirm nothing changed.
- Run the new families with the check on and off.

## Step 4: write up and push

A new README section with on and off tables, how the check works, and its limits. Limits expected, to be confirmed by measurement and not assumed:

- It only sees XORs written as the full set of clauses, at the top level.
- XORs over more than 6 variables written directly are not detected.
- Satisfiable parity instances get help only from forced variables and otherwise still need search.
- Other hard families remain.

Results get reported whether or not they come out as expected.
