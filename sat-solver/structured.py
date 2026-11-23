"""Structured SAT benchmarks: plain DPLL (sat3.py) against clause learning (cdcl.py).

Families:
  adder      circuit equivalence: two different n-bit adder designs give the same output (UNSAT)
  buried     a small contradiction hidden among many unrelated, easy constraints (UNSAT)
  latin      complete a partly filled Latin square, like a generalized Sudoku (SAT)
  pigeon     n+1 pigeons into n holes (UNSAT, and provably hard for clause learning)
"""
import random
import statistics
import sys
import time

from cdcl import solve as cdcl_solve
from sat3 import satisfies, solve as dpll


def cdcl(n, clauses, deadline=None):
    return cdcl_solve(n, clauses, deadline=deadline, counting=COUNTING)


COUNTING = True


class CNF:
    def __init__(self):
        self.n, self.clauses = 0, []

    def var(self):
        self.n += 1
        return self.n

    def add(self, *lits):
        self.clauses.append(list(lits))

    def AND(self, a, b):
        z = self.var()
        self.add(-z, a); self.add(-z, b); self.add(z, -a, -b)
        return z

    def OR(self, a, b):
        z = self.var()
        self.add(z, -a); self.add(z, -b); self.add(-z, a, b)
        return z

    def XOR(self, a, b):
        z = self.var()
        self.add(-z, a, b); self.add(-z, -a, -b); self.add(z, -a, b); self.add(z, a, -b)
        return z


def adder(bits, rng):
    """Miter of two ripple-carry adders built from different gate arrangements."""
    f = CNF()
    a = [f.var() for _ in range(bits)]
    b = [f.var() for _ in range(bits)]
    cin = f.var()
    c1 = c2 = cin
    diffs = []
    for i in range(bits):
        x1 = f.XOR(a[i], b[i])                       # design 1: (a^b)^c, carry = ab + c(a^b)
        s1 = f.XOR(x1, c1)
        c1 = f.OR(f.AND(a[i], b[i]), f.AND(c1, x1))
        s2 = f.XOR(a[i], f.XOR(b[i], c2))            # design 2: a^(b^c), carry = ab + ac + bc
        c2 = f.OR(f.OR(f.AND(a[i], b[i]), f.AND(a[i], c2)), f.AND(b[i], c2))
        diffs.append(f.XOR(s1, s2))
    diffs.append(f.XOR(c1, c2))
    f.add(*diffs)                                    # some output differs
    return f, False


def pigeon_clauses(f, pigeons, holes):
    p = [[f.var() for _ in range(holes)] for _ in range(pigeons)]
    for i in range(pigeons):
        f.add(*p[i])
    for h in range(holes):
        for i in range(pigeons):
            for j in range(i + 1, pigeons):
                f.add(-p[i][h], -p[j][h])


def pigeon(holes, rng):
    """Pigeonhole with variable names, clause order, and literal order scrambled."""
    f = CNF()
    pigeon_clauses(f, holes + 1, holes)
    names = [0] + rng.sample(range(1, f.n + 1), f.n)
    f.clauses = [rng.sample([names[l] if l > 0 else -names[-l] for l in c], len(c))
                 for c in rng.sample(f.clauses, len(f.clauses))]
    return f, False


def buried(blocks, rng):
    """`blocks` independent satisfiable sub-problems, plus a 5-pigeons-in-4-holes
    contradiction that shares no variables with them."""
    f = CNF()
    for _ in range(blocks):
        vs = [f.var() for _ in range(12)]
        hidden = {v: rng.random() < 0.5 for v in vs}
        made = 0
        while made < 30:                             # 2.5 clauses per variable, planted solution
            c = [v if rng.random() < 0.5 else -v for v in rng.sample(vs, 3)]
            if any(hidden[abs(l)] == (l > 0) for l in c):
                f.add(*c)
                made += 1
    pigeon_clauses(f, 5, 4)
    return f, False


def latin(order, rng):
    """Latin square of the given order with 42% of the cells blanked."""
    f = CNF()
    x = [[[f.var() for _ in range(order)] for _ in range(order)] for _ in range(order)]
    for r in range(order):
        for c in range(order):
            f.add(*x[r][c])
            for v in range(order):
                for w in range(v + 1, order):
                    f.add(-x[r][c][v], -x[r][c][w])
    for v in range(order):
        for i in range(order):
            for j in range(order):
                for k in range(j + 1, order):
                    f.add(-x[i][j][v], -x[i][k][v])  # once per row
                    f.add(-x[j][i][v], -x[k][i][v])  # once per column
    rows, cols, syms = (rng.sample(range(order), order) for _ in range(3))
    for r in range(order):
        for c in range(order):
            if rng.random() >= 0.42:
                f.add(x[r][c][syms[(rows[r] + cols[c]) % order]])
    return f, True


FAMILIES = {
    "adder": ("Adder equivalence (UNSAT)", "bits", adder, [2, 4, 6, 8, 12, 16, 24, 32], 1),
    "buried": ("Buried contradiction (UNSAT)", "blocks", buried, [1, 2, 3, 4, 6, 8, 16, 32], 3),
    "latin": ("Latin square completion (SAT)", "order", latin, [6, 9, 12, 15, 18, 21], 3),
    "pigeon": ("Pigeonhole (UNSAT)", "holes", pigeon, [4, 5, 6, 7, 8, 9, 12, 20, 40, 60], 1),
}


def run(solver, f, limit):
    """Return (seconds or None on timeout, work count, answer)."""
    t = time.perf_counter()
    try:
        model, work = solver(f.n, f.clauses, deadline=t + limit)
    except TimeoutError:
        return None, None, None
    secs = time.perf_counter() - t
    if isinstance(work, dict):
        work = work["conflicts"]
    if model is not None:
        assert satisfies(model, f.clauses), "returned a model that does not satisfy"
    return secs, work, model is not None


def main():
    global COUNTING
    args = [a for a in sys.argv[1:] if a != "--no-counting"]
    COUNTING = "--no-counting" not in sys.argv
    limit = float(args[0]) if args else 10.0
    names = args[1:] or list(FAMILIES)
    print("CDCL counting check:", "on" if COUNTING else "off")
    for name in names:
        title, unit, gen, sizes, seeds = FAMILIES[name]
        print(f"\n{title}, {seeds} instance(s) per size, {limit:g} s limit per run")
        print(f"{unit:>7} {'vars':>6} {'clauses':>8} | {'DPLL decisions':>14} {'DPLL sec':>9} | "
              f"{'CDCL conflicts':>14} {'CDCL sec':>9}")
        dead = {"dpll": False, "cdcl": False}
        for size in sizes:
            insts = [gen(size, random.Random(100 * size + s)) for s in range(seeds)]
            cells = []
            for key, solver in (("dpll", dpll), ("cdcl", cdcl)):
                if dead[key]:
                    cells.append(("skipped", "-"))
                    continue
                res = [run(solver, f, limit) for f, _ in insts]
                for (secs, _, ans), (_, expect) in zip(res, insts):
                    assert secs is None or ans == expect, f"{key} gave a wrong answer on {name} {size}"
                if sum(r[0] is None for r in res) > len(res) // 2:
                    dead[key] = True
                    cells.append(("timeout", f">{limit:g}"))
                else:
                    done = sorted((r for r in res if r[0] is not None), key=lambda r: r[0])
                    med = done[min(len(res) // 2, len(done) - 1)]
                    cells.append((f"{med[1]:,}", f"{med[0]:.3f}"))
            f0 = insts[0][0]
            print(f"{size:>7} {f0.n:>6} {len(f0.clauses):>8} | {cells[0][0]:>14} {cells[0][1]:>9} | "
                  f"{cells[1][0]:>14} {cells[1][1]:>9}", flush=True)
            if all(dead.values()):
                break


if __name__ == "__main__":
    main()
