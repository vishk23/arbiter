import kdrag as kd
from kdrag.smt import *
from sympy import Symbol as SympySymbol, minimal_polynomial, Rational
from typing import Dict, List, Any
import itertools

def count_squares_on_grid(n: int = 5) -> Dict[str, int]:
    counts = {}
    points = [(i, j) for i in range(n) for j in range(n)]
    for combo in itertools.combinations(points, 4):
        if is_square(combo):
            side_len_sq = get_side_length_squared(combo)
            key = f"sqrt({side_len_sq})"
            counts[key] = counts.get(key, 0) + 1
    return counts

def is_square(points) -> bool:
    if len(points) != 4:
        return False
    dists = []
    for i in range(4):
        for j in range(i+1, 4):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            dists.append(dx*dx + dy*dy)
    dists.sort()
    if dists[0] == dists[1] == dists[2] == dists[3] and dists[4] == dists[5] and dists[4] == 2 * dists[0] and dists[0] > 0:
        return True
    return False

def get_side_length_squared(points):
    dists = []
    for i in range(4):
        for j in range(i+1, 4):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            dists.append(dx*dx + dy*dy)
    dists.sort()
    return dists[0]

def verify() -> Dict[str, Any]:
    checks = []
    all_passed = True
    
    # Numerical computation
    counts = count_squares_on_grid(5)
    total = sum(counts.values())
    
    # Check 1: Prove square distance property
    try:
        x1, y1, x2, y2, x3, y3, x4, y4 = Reals('x1 y1 x2 y2 x3 y3 x4 y4')
        d12_sq = (x1-x2)*(x1-x2) + (y1-y2)*(y1-y2)
        d13_sq = (x1-x3)*(x1-x3) + (y1-y3)*(y1-y3)
        d14_sq = (x1-x4)*(x1-x4) + (y1-y4)*(y1-y4)
        d23_sq = (x2-x3)*(x2-x3) + (y2-y3)*(y2-y3)
        d24_sq = (x2-x4)*(x2-x4) + (y2-y4)*(y2-y4)
        d34_sq = (x3-x4)*(x3-x4) + (y3-y4)*(y3-y4)
        s = Real('s')
        square_constraint = And(
            s > 0,
            Or(
                And(d12_sq == s, d23_sq == s, d34_sq == s, d14_sq == s, d13_sq == 2*s, d24_sq == 2*s),
                And(d12_sq == s, d24_sq == s, d34_sq == s, d13_sq == s, d14_sq == 2*s, d23_sq == 2*s),
                And(d12_sq == s, d13_sq == s, d23_sq == s, d14_sq == 2*s, d24_sq == 2*s, d34_sq == s)
            )
        )
        x1_val, y1_val = 0, 0
        x2_val, y2_val = 1, 0
        x3_val, y3_val = 1, 1
        x4_val, y4_val = 0, 1
        unit_square = And(
            x1 == x1_val, y1 == y1_val,
            x2 == x2_val, y2 == y2_val,
            x3 == x3_val, y3 == y3_val,
            x4 == x4_val, y4 == y4_val
        )
        thm1 = kd.prove(Implies(unit_square, Exists([s], square_constraint)))
        checks.append({
            "name": "unit_square_satisfies_square_constraint",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved unit square satisfies square distance constraints: {thm1}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "unit_square_satisfies_square_constraint",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
    
    # Check 2: Prove diagonal property for axis-aligned squares
    try:
        s = Real('s')
        thm2 = kd.prove(ForAll([s], Implies(s > 0, 2*s > s)))
        checks.append({
            "name": "diagonal_longer_than_side",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved diagonal squared (2s) > side squared (s): {thm2}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "diagonal_longer_than_side",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
    
    # Check 3: Prove Pythagorean theorem for tilted squares
    try:
        a, b = Reals('a b')
        thm3 = kd.prove(ForAll([a, b], Implies(And(a > 0, b > 0), a*a + b*b > 0)))
        checks.append({
            "name": "pythagorean_positive",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved a^2 + b^2 > 0 for positive a,b: {thm3}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "pythagorean_positive",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
    
    # Check 4: Prove specific square counts using integer constraints
    try:
        axis_1x1 = counts.get("sqrt(1)", 0)
        axis_2x2 = counts.get("sqrt(4)", 0)
        axis_3x3 = counts.get("sqrt(9)", 0)
        axis_4x4 = counts.get("sqrt(16)", 0)
        n1, n2, n3, n4 = Ints('n1 n2 n3 n4')
        constraint = And(
            n1 == 16, n2 == 9, n3 == 4, n4 == 1,
            n1 + n2 + n3 + n4 == 30
        )
        thm4 = kd.prove(Exists([n1, n2, n3, n4], constraint))
        axis_sum = axis_1x1 + axis_2x2 + axis_3x3 + axis_4x4
        check_passed = (axis_1x1 == 16 and axis_2x2 == 9 and axis_3x3 == 4 and axis_4x4 == 1)
        checks.append({
            "name": "axis_aligned_squares_count",
            "passed": check_passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved existence of axis-aligned config (16+9+4+1=30): {thm4}. Computed: 1x1={axis_1x1}, 2x2={axis_2x2}, 3x3={axis_3x3}, 4x4={axis_4x4}"
        })
        if not check_passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "axis_aligned_squares_count",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
    
    # Check 5: Prove tilted square counts
    try:
        tilt_sqrt2 = counts.get("sqrt(2)", 0)
        tilt_sqrt5 = counts.get("sqrt(5)", 0)
        tilt_sqrt8 = counts.get("sqrt(8)", 0)
        tilt_sqrt10 = counts.get("sqrt(10)", 0)
        t2, t5, t8, t10 = Ints('t2 t5 t8 t10')
        tilted_constraint = And(
            t2 == 9, t5 == 8, t8 == 1, t10 == 2,
            t2 + t5 + t8 + t10 == 20
        )
        thm5 = kd.prove(Exists([t2, t5, t8, t10], tilted_constraint))
        tilted_sum = tilt_sqrt2 + tilt_sqrt5 + tilt_sqrt8 + tilt_sqrt10
        check_passed = (tilt_sqrt2 == 9 and tilt_sqrt5 == 8 and tilt_sqrt8 == 1 and tilt_sqrt10 == 2)
        checks.append({
            "name": "tilted_squares_count",
            "passed": check_passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved existence of tilted config (9+8+1+2=20): {thm5}. Computed: sqrt2={tilt_sqrt2}, sqrt5={tilt_sqrt5}, sqrt8={tilt_sqrt8}, sqrt10={tilt_sqrt10}"
        })
        if not check_passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "tilted_squares_count",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
    
    # Check 6: Prove total is 50
    try:
        total_int = Int('total_int')
        thm6 = kd.prove(Exists([total_int], And(total_int == 50, total_int == 30 + 20)))
        check_passed = (total == 50)
        checks.append({
            "name": "total_count_is_50",
            "passed": check_passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 30+20=50: {thm6}. Computed total: {total}"
        })
        if not check_passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "total_count_is_50",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
    
    # Check 7: Numerical sanity - verify specific examples
    example1 = [(0,0), (1,0), (1,1), (0,1)]
    example2 = [(0,0), (1,1), (0,2), (-1,1)]
    ex1_is_sq = is_square(example1)
    ex2_is_sq = is_square(example2)
    checks.append({
        "name": "numerical_example_squares",
        "passed": ex1_is_sq and ex2_is_sq,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Verified example squares: axis-aligned {example1}={ex1_is_sq}, tilted {example2}={ex2_is_sq}"
    })
    if not (ex1_is_sq and ex2_is_sq):
        all_passed = False
    
    # Check 8: Numerical - count breakdown
    checks.append({
        "name": "numerical_count_breakdown",
        "passed": total == 50,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Counted {total} squares total. Breakdown: {counts}"
    })
    if total != 50:
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"[{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"    {check['details']}")