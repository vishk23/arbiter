#!/usr/bin/env python3
"""Verified proof that lines s=9-2t and t=3s+1 intersect at (1,4)."""

import kdrag as kd
from kdrag.smt import Real, ForAll, Exists, And, Implies
from sympy import symbols, solve, Eq
from sympy import N as sympy_N

def verify() -> dict:
    """Verify that the lines s=9-2t and t=3s+1 intersect at (1,4)."""
    checks = []
    
    # CHECK 1: kdrag proof that (1,4) satisfies both equations
    try:
        s, t = Real('s'), Real('t')
        eq1 = (s == 9 - 2*t)
        eq2 = (t == 3*s + 1)
        claim = And(eq1, eq2)
        point_claim = claim.substitute([(s, 1.0), (t, 4.0)])
        thm = kd.prove(point_claim)
        checks.append({
            "name": "kdrag_point_satisfies_both_equations",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved that (1,4) satisfies both equations: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_point_satisfies_both_equations",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
    
    # CHECK 2: kdrag proof of uniqueness - if both equations hold, then s=1 and t=4
    try:
        s, t = Real('s'), Real('t')
        eq1 = (s == 9 - 2*t)
        eq2 = (t == 3*s + 1)
        hypothesis = And(eq1, eq2)
        conclusion = And(s == 1, t == 4)
        uniqueness = ForAll([s, t], Implies(hypothesis, conclusion))
        thm = kd.prove(uniqueness)
        checks.append({
            "name": "kdrag_uniqueness",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved uniqueness: if both equations hold, then s=1 and t=4: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_uniqueness",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
    
    # CHECK 3: SymPy symbolic solution
    try:
        s_sym, t_sym = symbols('s t', real=True)
        eq1_sym = Eq(s_sym, 9 - 2*t_sym)
        eq2_sym = Eq(t_sym, 3*s_sym + 1)
        solution = solve([eq1_sym, eq2_sym], [s_sym, t_sym])
        is_correct = (solution == {s_sym: 1, t_sym: 4})
        checks.append({
            "name": "sympy_symbolic_solve",
            "passed": is_correct,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solve gave {solution}, expected {{s: 1, t: 4}}: {is_correct}"
        })
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_solve",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {e}"
        })
    
    # CHECK 4: Numerical sanity check - substitute (1,4) into both equations
    try:
        s_val, t_val = 1, 4
        eq1_lhs = s_val
        eq1_rhs = 9 - 2*t_val
        eq2_lhs = t_val
        eq2_rhs = 3*s_val + 1
        eq1_satisfied = abs(eq1_lhs - eq1_rhs) < 1e-10
        eq2_satisfied = abs(eq2_lhs - eq2_rhs) < 1e-10
        passed = eq1_satisfied and eq2_satisfied
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"eq1: {s_val} == {eq1_rhs} ({eq1_satisfied}), eq2: {t_val} == {eq2_rhs} ({eq2_satisfied})"
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {e}"
        })
    
    # CHECK 5: kdrag proof that intersection exists and is unique
    try:
        s, t = Real('s'), Real('t')
        eq1 = (s == 9 - 2*t)
        eq2 = (t == 3*s + 1)
        existence = Exists([s, t], And(eq1, eq2))
        thm = kd.prove(existence)
        checks.append({
            "name": "kdrag_existence",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved existence of intersection: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_existence",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
    
    all_passed = all(check["passed"] for check in checks)
    return {"proved": all_passed, "checks": checks}

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result["checks"]:
        status = "✓" if check["passed"] else "✗"
        print(f"  {status} {check['name']} ({check['backend']})")
        print(f"    {check['details']}")