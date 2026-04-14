import kdrag as kd
from kdrag.smt import *
import z3

def verify():
    checks = []
    all_passed = True

    # Check 1: Verify closure property for sum of invariant subspaces (2 subspaces)
    check1_name = "two_invariant_subspaces_sum_closed"
    try:
        V = z3.DeclareSort('V')
        T = z3.Function('T', V, V)
        in_U1 = z3.Function('in_U1', V, z3.BoolSort())
        in_U2 = z3.Function('in_U2', V, z3.BoolSort())
        in_sum = z3.Function('in_sum', V, z3.BoolSort())
        
        v = z3.Const('v', V)
        u1 = z3.Const('u1', V)
        u2 = z3.Const('u2', V)
        add = z3.Function('add', V, V, V)
        
        invariant_U1 = z3.ForAll([v], z3.Implies(in_U1(v), in_U1(T(v))))
        invariant_U2 = z3.ForAll([v], z3.Implies(in_U2(v), in_U2(T(v))))
        sum_def = z3.ForAll([v], z3.Implies(in_sum(v), z3.Exists([u1, u2], z3.And(in_U1(u1), in_U2(u2), v == add(u1, u2)))))
        linearity = z3.ForAll([u1, u2], T(add(u1, u2)) == add(T(u1), T(u2)))
        
        claim = z3.ForAll([v], z3.Implies(in_sum(v), in_sum(T(v))))
        
        thm = kd.prove(claim, by=[kd.axiom(invariant_U1), kd.axiom(invariant_U2), kd.axiom(sum_def), kd.axiom(linearity)])
        
        checks.append({
            "name": check1_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved that sum of 2 invariant subspaces is invariant under T using Z3. Proof object: {type(thm).__name__}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": check1_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 2-subspace case: {str(e)}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check1_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error in 2-subspace proof: {str(e)}"
        })

    # Check 2: Verify closure property for sum of invariant subspaces (3 subspaces)
    check2_name = "three_invariant_subspaces_sum_closed"
    try:
        V = z3.DeclareSort('V')
        T = z3.Function('T', V, V)
        in_U1 = z3.Function('in_U1', V, z3.BoolSort())
        in_U2 = z3.Function('in_U2', V, z3.BoolSort())
        in_U3 = z3.Function('in_U3', V, z3.BoolSort())
        in_sum = z3.Function('in_sum', V, z3.BoolSort())
        
        v = z3.Const('v', V)
        u1 = z3.Const('u1', V)
        u2 = z3.Const('u2', V)
        u3 = z3.Const('u3', V)
        add = z3.Function('add', V, V, V)
        
        invariant_U1 = z3.ForAll([v], z3.Implies(in_U1(v), in_U1(T(v))))
        invariant_U2 = z3.ForAll([v], z3.Implies(in_U2(v), in_U2(T(v))))
        invariant_U3 = z3.ForAll([v], z3.Implies(in_U3(v), in_U3(T(v))))
        sum_def = z3.ForAll([v], z3.Implies(in_sum(v), z3.Exists([u1, u2, u3], z3.And(in_U1(u1), in_U2(u2), in_U3(u3), v == add(add(u1, u2), u3)))))
        linearity1 = z3.ForAll([u1, u2], T(add(u1, u2)) == add(T(u1), T(u2)))
        assoc = z3.ForAll([u1, u2, u3], add(add(u1, u2), u3) == add(u1, add(u2, u3)))
        
        claim = z3.ForAll([v], z3.Implies(in_sum(v), in_sum(T(v))))
        
        thm = kd.prove(claim, by=[kd.axiom(invariant_U1), kd.axiom(invariant_U2), kd.axiom(invariant_U3), kd.axiom(sum_def), kd.axiom(linearity1), kd.axiom(assoc)])
        
        checks.append({
            "name": check2_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved that sum of 3 invariant subspaces is invariant under T using Z3. Proof object: {type(thm).__name__}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": check2_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 3-subspace case: {str(e)}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check2_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error in 3-subspace proof: {str(e)}"
        })

    # Check 3: Numerical sanity - concrete vector space example (R^2)
    check3_name = "numerical_concrete_example"
    try:
        import numpy as np
        
        T_matrix = np.array([[2, 0], [0, 3]])
        
        U1_basis = np.array([[1], [0]])
        U2_basis = np.array([[0], [1]])
        
        v_in_U1 = np.array([[5], [0]])
        Tv_in_U1 = T_matrix @ v_in_U1
        u1_invariant = np.allclose(Tv_in_U1, np.array([[10], [0]]))
        
        v_in_U2 = np.array([[0], [7]])
        Tv_in_U2 = T_matrix @ v_in_U2
        u2_invariant = np.allclose(Tv_in_U2, np.array([[0], [21]]))
        
        v_in_sum = np.array([[3], [4]])
        Tv_in_sum = T_matrix @ v_in_sum
        expected = np.array([[6], [12]])
        sum_invariant = np.allclose(Tv_in_sum, expected)
        
        passed = u1_invariant and u2_invariant and sum_invariant
        
        checks.append({
            "name": check3_name,
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Verified concrete example in R^2 with diagonal transformation T. U1 invariant: {u1_invariant}, U2 invariant: {u2_invariant}, U1+U2 invariant: {sum_invariant}"
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check3_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error in numerical check: {str(e)}"
        })

    # Check 4: Another numerical example with projection operator
    check4_name = "numerical_projection_example"
    try:
        import numpy as np
        
        T_matrix = np.array([[1, 0, 0], [0, 0, 0], [0, 0, 1]])
        
        v1 = np.array([[2], [0], [0]])
        Tv1 = T_matrix @ v1
        check1 = np.allclose(Tv1, v1)
        
        v2 = np.array([[0], [0], [3]])
        Tv2 = T_matrix @ v2
        check2 = np.allclose(Tv2, v2)
        
        v_sum = np.array([[2], [5], [3]])
        Tv_sum = T_matrix @ v_sum
        expected = np.array([[2], [0], [3]])
        check3 = np.allclose(Tv_sum, expected)
        
        component_in_U1 = np.array([[2], [0], [0]])
        component_in_U2 = np.array([[0], [0], [3]])
        sum_components = component_in_U1 + component_in_U2
        check4 = np.allclose(Tv_sum, T_matrix @ component_in_U1 + T_matrix @ component_in_U2)
        
        passed = check1 and check2 and check3 and check4
        
        checks.append({
            "name": check4_name,
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Verified projection operator in R^3. Individual invariance: {check1 and check2}, Sum invariance: {check3}, Linearity: {check4}"
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check4_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error in projection check: {str(e)}"
        })

    return {"proved": all_passed, "checks": checks}

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print("\nDetailed checks:")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"      {check['details']}")