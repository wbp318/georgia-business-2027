"""CDCL 3-SAT solver: clause learning (first UIP), backjumping, activity-based
branching, phase saving, Luby restarts, learned-clause cleanup. Compared with
the plain DPLL solver in sat3.py on the same hard random instances."""
import math
import random
import statistics
import sys
import time

from sat3 import brute_force, random_3sat, satisfies, solve as dpll


def luby(i):
    """i-th term (1-based) of the Luby sequence 1,1,2,1,1,2,4,..."""
    k = 1
    while (1 << k) - 1 < i:
        k += 1
    while (1 << k) - 1 != i:
        i -= (1 << (k - 1)) - 1
        k = 1
        while (1 << k) - 1 < i:
            k += 1
    return 1 << (k - 1)


def solve(n, clauses, restart_unit=100):
    """Return (model or None, stats dict)."""
    idx = lambda lit: 2 * abs(lit) + (lit < 0)
    cls = [list(c) for c in clauses]
    n_orig = len(cls)
    watches = [[] for _ in range(2 * n + 2)]
    for ci, c in enumerate(cls):
        watches[idx(c[0])].append(ci)
        watches[idx(c[1])].append(ci)
    val = [0] * (n + 1)
    level = [0] * (n + 1)
    reason = [-1] * (n + 1)
    phase = [-1] * (n + 1)
    act = [0.0] * (n + 1)
    seen = [False] * (n + 1)
    trail, trail_lim = [], []
    st = {"decisions": 0, "conflicts": 0, "restarts": 0, "learned": 0, "deleted": 0}
    inc = 1.0
    qhead = 0
    max_learnts = max(2000, n_orig // 2)
    live_learnts = 0

    def value(lit):
        return val[lit] if lit > 0 else -val[-lit]

    def assign(lit, why):
        v = abs(lit)
        val[v] = 1 if lit > 0 else -1
        level[v] = len(trail_lim)
        reason[v] = why
        trail.append(lit)

    def propagate():
        nonlocal qhead
        while qhead < len(trail):
            false_lit = -trail[qhead]
            qhead += 1
            wl = watches[idx(false_lit)]
            i = 0
            while i < len(wl):
                ci = wl[i]
                c = cls[ci]
                if c is None:                       # deleted learned clause
                    wl[i] = wl[-1]
                    wl.pop()
                    continue
                if c[0] == false_lit:
                    c[0], c[1] = c[1], c[0]
                if value(c[0]) == 1:
                    i += 1
                    continue
                for k in range(2, len(c)):
                    if value(c[k]) != -1:
                        c[1], c[k] = c[k], c[1]
                        watches[idx(c[1])].append(ci)
                        wl[i] = wl[-1]
                        wl.pop()
                        break
                else:
                    if value(c[0]) == -1:
                        return ci
                    assign(c[0], ci)
                    i += 1
        return -1

    def analyze(confl):
        """First-UIP learning. Return (learned clause, backjump level)."""
        nonlocal inc
        learnt, counter, p, i = [0], 0, None, len(trail) - 1
        cur = len(trail_lim)
        while True:
            for q in cls[confl]:
                if q == p:
                    continue
                v = abs(q)
                if not seen[v] and level[v] > 0:
                    seen[v] = True
                    act[v] += inc
                    if level[v] >= cur:
                        counter += 1
                    else:
                        learnt.append(q)
            while not seen[abs(trail[i])]:
                i -= 1
            p = trail[i]
            i -= 1
            seen[abs(p)] = False
            counter -= 1
            if counter == 0:
                break
            confl = reason[abs(p)]
        learnt[0] = -p
        for q in learnt[1:]:
            seen[abs(q)] = False
        back = 0
        if len(learnt) > 1:
            j = max(range(1, len(learnt)), key=lambda k: level[abs(learnt[k])])
            learnt[1], learnt[j] = learnt[j], learnt[1]
            back = level[abs(learnt[1])]
        inc /= 0.95
        if inc > 1e100:
            for v in range(1, n + 1):
                act[v] *= 1e-100
            inc *= 1e-100
        return learnt, back

    def cancel_until(lvl):
        nonlocal qhead
        if len(trail_lim) <= lvl:
            return
        size = trail_lim[lvl]
        while len(trail) > size:
            lit = trail.pop()
            v = abs(lit)
            phase[v] = val[v]
            val[v] = 0
            reason[v] = -1
        del trail_lim[lvl:]
        qhead = len(trail)

    def reduce_db():
        """Drop the longer half of the learned clauses that aren't in use as reasons."""
        nonlocal live_learnts
        cand = [ci for ci in range(n_orig, len(cls))
                if cls[ci] is not None and len(cls[ci]) > 3
                and not (value(cls[ci][0]) == 1 and reason[abs(cls[ci][0])] == ci)]
        cand.sort(key=lambda ci: -len(cls[ci]))
        for ci in cand[:len(cand) // 2]:
            cls[ci] = None
            live_learnts -= 1
            st["deleted"] += 1

    since_restart, limit = 0, restart_unit * luby(1)
    while True:
        confl = propagate()
        if confl != -1:
            st["conflicts"] += 1
            since_restart += 1
            if not trail_lim:
                return None, st
            learnt, back = analyze(confl)
            cancel_until(back)
            st["learned"] += 1
            if len(learnt) == 1:
                assign(learnt[0], -1)
            else:
                cls.append(learnt)
                ci = len(cls) - 1
                watches[idx(learnt[0])].append(ci)
                watches[idx(learnt[1])].append(ci)
                live_learnts += 1
                assign(learnt[0], ci)
            continue
        if since_restart >= limit:
            st["restarts"] += 1
            since_restart, limit = 0, restart_unit * luby(st["restarts"] + 1)
            cancel_until(0)
            continue
        if live_learnts > max_learnts:
            reduce_db()
            max_learnts = int(max_learnts * 1.1)
        best, best_act = 0, -1.0
        for v in range(1, n + 1):
            if val[v] == 0 and act[v] > best_act:
                best, best_act = v, act[v]
        if best == 0:
            return [None] + [val[v] == 1 for v in range(1, n + 1)], st
        st["decisions"] += 1
        trail_lim.append(len(trail))
        assign(best * phase[best], -1)


def main():
    rng = random.Random(7)
    ok = sat_count = 0
    for _ in range(600):
        n = rng.randint(3, 15)
        f = random_3sat(n, rng.uniform(2.0, 7.0), rng)
        model, _ = solve(n, f, restart_unit=rng.choice([1, 3, 100]))
        assert (model is not None) == brute_force(n, f), "disagrees with brute force"
        if model is not None:
            assert satisfies(model, f)
            sat_count += 1
        ok += 1
    print(f"Correctness: {ok} small instances match brute force "
          f"({sat_count} satisfiable, {ok - sat_count} unsatisfiable).\n")

    per_n = 15
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 10.0
    dpll_max = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    print(f"Random 3-SAT at ratio 4.26, {per_n} instances per size, same instances for both solvers")
    print(f"{'vars':>5} {'sat':>6} | {'DPLL decisions':>14} {'DPLL sec':>9} | "
          f"{'CDCL conflicts':>14} {'CDCL sec':>9} {'CDCL max':>9} | agree")
    rows, n = [], 50
    while True:
        gen = random.Random(1000 + n)
        fs = [random_3sat(n, 4.26, gen) for _ in range(per_n)]
        c_sec, c_conf, c_ans = [], [], []
        for f in fs:
            t = time.perf_counter()
            model, s = solve(n, f)
            c_sec.append(time.perf_counter() - t)
            c_conf.append(s["conflicts"])
            if model is not None:
                assert satisfies(model, f)
            c_ans.append(model is not None)
        d_dec = d_sec = agree = "-"
        if n <= dpll_max:
            dd, ds, da = [], [], []
            for f in fs:
                t = time.perf_counter()
                model, d = dpll(n, f)
                ds.append(time.perf_counter() - t)
                dd.append(d)
                da.append(model is not None)
            d_dec, d_sec = f"{statistics.median(dd):,.0f}", f"{statistics.median(ds):.3f}"
            agree = "yes" if da == c_ans else "NO"
        ms = statistics.median(c_sec)
        rows.append((n, statistics.median(c_conf), ms))
        print(f"{n:>5} {sum(c_ans):>3}/{per_n:<2} | {d_dec:>14} {d_sec:>9} | "
              f"{statistics.median(c_conf):>14,.0f} {ms:>9.3f} {max(c_sec):>9.2f} | {agree}",
              flush=True)
        if ms > budget:
            break
        n += 25

    def fit(ys):
        xs = [r[0] for r in rows]
        mx, my = statistics.mean(xs), statistics.mean(ys)
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
        return slope, my - slope * mx

    sc, _ = fit([math.log2(max(r[1], 1)) for r in rows])
    st, it = fit([math.log2(r[2]) for r in rows])
    print(f"\nCDCL conflicts double about every {1 / sc:.1f} variables; "
          f"time doubles about every {1 / st:.1f} variables.")
    for target in (500, 1000):
        s = 2 ** (st * target + it)
        print(f"Extrapolated CDCL median time at {target} variables: "
              f"{s:.2e} seconds (about {s / 3.15e7:.1e} years).")


if __name__ == "__main__":
    main()
