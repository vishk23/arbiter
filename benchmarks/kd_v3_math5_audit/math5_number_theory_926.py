import kdrag as kd
from kdrag.smt import *
from sympy import fibonacci as sym_fib

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify Fibonacci sequence mod 7 has period 16
    check1 = {
        "name": "fibonacci_period_16_mod_7",
        "backend": "numerical",
        "proof_type": "numerical"
    }
    try:
        fib_mod7 = []
        a, b = 0, 1
        for i in range(32):
            fib_mod7.append(a % 7)
            a, b = b, (a + b)
        
        expected = [0,1,1,2,3,5,1,6,0,6,6,5,4,2,6,1]
        period_verified = (fib_mod7[:16] == expected and fib_mod7[16:32] == expected)
        
        check1["passed"] = period_verified
        check1["details"] = f"First 16 terms mod 7: {fib_mod7[:16]}, Second 16: {fib_mod7[16:32]}, Period 16 verified: {period_verified}"
        if not period_verified:
            all_passed = False
    except Exception as e:
        check1["passed"] = False
        check1["details"] = f"Error: {str(e)}"
        all_passed = False
    checks.append(check1)
    
    # Check 2: Verify t_5 mod 7 = 5 using kdrag
    check2 = {
        "name": "t5_mod7_equals_5",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        # Define Fibonacci function symbolically
        n = Int("n")
        t = Function("t", IntSort(), IntSort())
        
        # Axioms for Fibonacci
        ax0 = kd.axiom(t(0) == 0)
        ax1 = kd.axiom(t(1) == 1)
        ax_rec = kd.axiom(ForAll([n], Implies(n >= 2, t(n) == t(n-1) + t(n-2))))
        
        # Chain proofs to compute t(5)
        t2_proof = kd.prove(t(2) == 1, by=[ax_rec, ax0, ax1])
        t3_proof = kd.prove(t(3) == 2, by=[ax_rec, ax1, t2_proof])
        t4_proof = kd.prove(t(4) == 3, by=[ax_rec, t2_proof, t3_proof])
        t5_proof = kd.prove(t(5) == 5, by=[ax_rec, t3_proof, t4_proof])
        
        # Verify t(5) mod 7 == 5
        proof_mod = kd.prove(t(5) % 7 == 5, by=[t5_proof])
        
        check2["passed"] = True
        check2["details"] = f"Proved t(5) = 5, hence t(5) mod 7 = 5. Proof object: {proof_mod}"
    except Exception as e:
        check2["passed"] = False
        check2["details"] = f"kdrag proof failed: {str(e)}"
        all_passed = False
    checks.append(check2)
    
    # Check 3: Verify t_10 mod 7 = 6 using kdrag chain
    check3 = {
        "name": "t10_mod7_equals_6",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        n = Int("n")
        t = Function("t", IntSort(), IntSort())
        ax0 = kd.axiom(t(0) == 0)
        ax1 = kd.axiom(t(1) == 1)
        ax_rec = kd.axiom(ForAll([n], Implies(n >= 2, t(n) == t(n-1) + t(n-2))))
        
        # Build up to t(10)
        t2 = kd.prove(t(2) == 1, by=[ax_rec, ax0, ax1])
        t3 = kd.prove(t(3) == 2, by=[ax_rec, ax1, t2])
        t4 = kd.prove(t(4) == 3, by=[ax_rec, t2, t3])
        t5 = kd.prove(t(5) == 5, by=[ax_rec, t3, t4])
        t6 = kd.prove(t(6) == 8, by=[ax_rec, t4, t5])
        t7 = kd.prove(t(7) == 13, by=[ax_rec, t5, t6])
        t8 = kd.prove(t(8) == 21, by=[ax_rec, t6, t7])
        t9 = kd.prove(t(9) == 34, by=[ax_rec, t7, t8])
        t10 = kd.prove(t(10) == 55, by=[ax_rec, t8, t9])
        
        # 55 mod 7 = 6
        proof_mod = kd.prove(t(10) % 7 == 6, by=[t10])
        
        check3["passed"] = True
        check3["details"] = f"Proved t(10) = 55, hence t(10) mod 7 = 6. Proof: {proof_mod}"
    except Exception as e:
        check3["passed"] = False
        check3["details"] = f"kdrag proof failed: {str(e)}"
        all_passed = False
    checks.append(check3)
    
    # Check 4: Verify t_15 mod 7 = 1 using kdrag chain
    check4 = {
        "name": "t15_mod7_equals_1",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        n = Int("n")
        t = Function("t", IntSort(), IntSort())
        ax0 = kd.axiom(t(0) == 0)
        ax1 = kd.axiom(t(1) == 1)
        ax_rec = kd.axiom(ForAll([n], Implies(n >= 2, t(n) == t(n-1) + t(n-2))))
        
        proofs = {0: ax0, 1: ax1}
        for i in range(2, 16):
            proofs[i] = kd.prove(t(i) == t(i-1) + t(i-2), by=[ax_rec, proofs[i-1], proofs[i-2]])
        
        # t(15) = 610, 610 mod 7 = 1
        t15_val = kd.prove(t(15) == 610, by=[ax_rec, proofs[13], proofs[14]])
        proof_mod = kd.prove(t(15) % 7 == 1, by=[t15_val])
        
        check4["passed"] = True
        check4["details"] = f"Proved t(15) = 610, hence t(15) mod 7 = 1. Proof: {proof_mod}"
    except Exception as e:
        check4["passed"] = False
        check4["details"] = f"kdrag proof failed: {str(e)}"
        all_passed = False
    checks.append(check4)
    
    # Check 5: Verify sum mod 7 using kdrag
    check5 = {
        "name": "sum_mod7_equals_5",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        # Given t_a mod 7 = 5, t_b mod 7 = 6, t_c mod 7 = 1
        ta, tb, tc = Ints("ta tb tc")
        ax_ta = kd.axiom(ta % 7 == 5)
        ax_tb = kd.axiom(tb % 7 == 6)
        ax_tc = kd.axiom(tc % 7 == 1)
        
        # Prove (ta + tb + tc) mod 7 = 5
        sum_proof = kd.prove((ta + tb + tc) % 7 == 5, by=[ax_ta, ax_tb, ax_tc])
        
        check5["passed"] = True
        check5["details"] = f"Proved (5 + 6 + 1) mod 7 = 12 mod 7 = 5. Proof: {sum_proof}"
    except Exception as e:
        check5["passed"] = False
        check5["details"] = f"kdrag proof failed: {str(e)}"
        all_passed = False
    checks.append(check5)
    
    # Check 6: Numerical verification with SymPy
    check6 = {
        "name": "numerical_verification_sympy",
        "backend": "sympy",
        "proof_type": "numerical"
    }
    try:
        # SymPy Fibonacci is 1-indexed: F(0)=0, F(1)=1, ...
        t5 = sym_fib(5) % 7
        t10 = sym_fib(10) % 7
        t15 = sym_fib(15) % 7
        total = (t5 + t10 + t15) % 7
        
        verified = (t5 == 5 and t10 == 6 and t15 == 1 and total == 5)
        
        check6["passed"] = verified
        check6["details"] = f"SymPy: t_5 mod 7 = {t5}, t_10 mod 7 = {t10}, t_15 mod 7 = {t15}, sum mod 7 = {total}"
        if not verified:
            all_passed = False
    except Exception as e:
        check6["passed"] = False
        check6["details"] = f"SymPy error: {str(e)}"
        all_passed = False
    checks.append(check6)
    
    return {"proved": all_passed, "checks": checks}

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"[{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"  {check['details']}")