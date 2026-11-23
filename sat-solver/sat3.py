"""A complete 3-SAT solver (DPLL with two-watched-literal unit propagation),
checked against brute force, then timed on hard random instances near the
4.26 clause-to-variable threshold to see how the work grows with size."""
import itertools
import math
import random
import statistics
import sys
import time


def solve(n, clauses, deadline=None):
    """Return (model or None, decisions). model[v] is True/False for v in 1..n.
    Clauses may have any length. Raises TimeoutError past `deadline` (perf_counter time)."""
    idx = lambda lit: 2 * abs(lit) + (lit < 0)
    val = [0] * (n + 1)                      # 0 unassigned, 1 true, -1 false
    watches = [[] for _ in range(2 * n + 2)]
    cls = [list(c) for c in clauses]
    occ = [0] * (2 * n + 2)
    for ci, c in enumerate(cls):
        for lit in c:
            occ[idx(lit)] += 1
        if len(c) >= 2:
            watches[idx(c[0])].append(ci)
            watches[idx(c[1])].append(ci)
    # Branch on the most frequent variables first, trying the majority sign first.
    order = sorted(range(1, n + 1), key=lambda v: -(occ[2 * v] + occ[2 * v + 1]))
    first = [0] + [1 if occ[2 * v] >= occ[2 * v + 1] else -1 for v in range(1, n + 1)]

    trail, levels = [], []                   # levels: (trail length, literal, flipped?)
    decisions = 0

    def value(lit):
        return val[abs(lit)] if lit > 0 else -val[abs(lit)]

    def assign(lit):
        val[abs(lit)] = 1 if lit > 0 else -1
        trail.append(lit)

    def propagate(start):
        """Unit-propagate from trail[start:]. Return False on conflict."""
        q = start
        while q < len(trail):
            false_lit = -trail[q]
            q += 1
            wl = watches[idx(false_lit)]
            i = 0
            while i < len(wl):
                c = cls[wl[i]]
                if c[0] == false_lit:
                    c[0], c[1] = c[1], c[0]
                # c[1] is the false watch; c[0] is the other watch
                if value(c[0]) == 1:
                    i += 1
                    continue
                for k in range(2, len(c)):
                    if value(c[k]) != -1:
                        c[1], c[k] = c[k], c[1]
                        watches[idx(c[1])].append(wl[i])
                        wl[i] = wl[-1]
                        wl.pop()
                        break
                else:
                    if value(c[0]) == -1:
                        return False
                    assign(c[0])
                    i += 1
        return True

    def backtrack():
        """Undo to the most recent unflipped decision and flip it. False if none."""
        while levels:
            size, lit, flipped = levels.pop()
            while len(trail) > size:
                val[abs(trail.pop())] = 0
            if not flipped:
                levels.append((size, -lit, True))
                assign(-lit)
                return True
        return False

    for c in cls:                            # empty and unit clauses
        if not c or (len(c) == 1 and value(c[0]) == -1):
            return None, decisions
        if len(c) == 1 and value(c[0]) == 0:
            assign(c[0])

    start = 0
    while True:
        if not propagate(start):
            if not backtrack():
                return None, decisions
            start = len(trail) - 1
            continue
        v = next((v for v in order if val[v] == 0), None)
        if v is None:
            return [None] + [val[u] == 1 for u in range(1, n + 1)], decisions
        decisions += 1
        if deadline is not None and time.perf_counter() > deadline:
            raise TimeoutError
        lit = v * first[v]
        levels.append((len(trail), lit, False))
        start = len(trail)
        assign(lit)


def random_3sat(n, ratio, rng):
    m = round(ratio * n)
    return [[v if rng.random() < 0.5 else -v for v in rng.sample(range(1, n + 1), 3)]
            for _ in range(m)]


def satisfies(model, clauses):
    return all(any(model[abs(l)] == (l > 0) for l in c) for c in clauses)


def brute_force(n, clauses):
    for bits in itertools.product([False, True], repeat=n):
        if satisfies((None,) + bits, clauses):
            return True
    return False


def main():
    rng = random.Random(2026)

    # 1. Correctness: agree with brute force on small instances.
    checked = sat_count = 0
    for _ in range(400):
        n = rng.randint(3, 14)
        f = random_3sat(n, rng.uniform(2.0, 6.5), rng)
        model, _ = solve(n, f)
        truth = brute_force(n, f)
        assert (model is not None) == truth, "disagrees with brute force"
        if model is not None:
            assert satisfies(model, f), "returned a model that does not satisfy"
            sat_count += 1
        checked += 1
    print(f"Correctness: {checked} small instances match brute force "
          f"({sat_count} satisfiable, {checked - sat_count} unsatisfiable).\n")

    # 2. Scaling at the hard ratio.
    per_n, budget = 15, float(sys.argv[1]) if len(sys.argv) > 1 else 6.0
    print(f"Random 3-SAT at ratio 4.26, {per_n} instances per size")
    print(f"{'vars':>5} {'sat':>6} {'median decisions':>17} {'median sec':>11} {'max sec':>9}")
    rows, n = [], 25
    while True:
        dec, secs, sat = [], [], 0
        for _ in range(per_n):
            f = random_3sat(n, 4.26, rng)
            t = time.perf_counter()
            model, d = solve(n, f)
            secs.append(time.perf_counter() - t)
            dec.append(d)
            if model is not None:
                assert satisfies(model, f)
                sat += 1
        md, ms = statistics.median(dec), statistics.median(secs)
        rows.append((n, md, ms))
        print(f"{n:>5} {sat:>3}/{per_n:<2} {md:>17,.0f} {ms:>11.3f} {max(secs):>9.2f}")
        if ms > budget:
            break
        n += 25

    # 3. Fit log2(median decisions) and log2(median time) against n.
    def fit(ys):
        xs = [r[0] for r in rows]
        mx, my = statistics.mean(xs), statistics.mean(ys)
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
        return slope, my - slope * mx

    sd, _ = fit([math.log2(max(r[1], 1)) for r in rows])
    st, it = fit([math.log2(r[2]) for r in rows])
    print(f"\nDecisions double about every {1 / sd:.1f} variables; "
          f"time doubles about every {1 / st:.1f} variables.")
    for target in (500, 1000):
        s = 2 ** (st * target + it)
        print(f"Extrapolated median time at {target} variables: "
              f"{s:.2e} seconds (about {s / 3.15e7:.1e} years).")
    # Polynomial check: if time were n^k, k would be stable between consecutive sizes.
    ks = [math.log(rows[i + 1][2] / rows[i][2]) / math.log(rows[i + 1][0] / rows[i][0])
          for i in range(len(rows) - 1)]
    print("Apparent polynomial degree between consecutive sizes: "
          + ", ".join(f"{k:.1f}" for k in ks))


if __name__ == "__main__":
    main()
