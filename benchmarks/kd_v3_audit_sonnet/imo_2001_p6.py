import kdrag as kd
from kdrag.smt import *
from sympy import factorint

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify the algebraic identity from the hint
    # (K+L-M+N)(-K+L+M+N) = L^2 + LN + N^2 - K^2 + KM - M^2
    K, L, M, N = Ints('K L M N')
    lhs = (K + L - M + N) * (-K + L + M + N)
    rhs = L*L + L*N + N*N - K*K + K*M - M*M
    identity = kd.prove(ForAll([K, L, M, N], lhs == rhs))
    checks.append({
        'name': 'algebraic_identity',
        'passed': True,
        'backend': 'kdrag',
        'proof_type': 'certificate',
        'details': 'Proved (K+L-M+N)(-K+L+M+N) = L^2+LN+N^2-K^2+KM-M^2'
    })
    
    # Check 2: Under constraint KM+LN = (K+L-M+N)(-K+L+M+N), verify L^2+LN+N^2 = K^2-KM+M^2
    constraint = (K*M + L*N == (K + L - M + N) * (-K + L + M + N))
    equality = (L*L + L*N + N*N == K*K - K*M + M*M)
    constraint_implies_equality = kd.prove(ForAll([K, L, M, N], Implies(constraint, equality)))
    checks.append({
        'name': 'constraint_implies_equality',
        'passed': True,
        'backend': 'kdrag',
        'proof_type': 'certificate',
        'details': 'Under KM+LN=(K+L-M+N)(-K+L+M+N), proved L^2+LN+N^2=K^2-KM+M^2'
    })
    
    # Check 3: Verify the key divisibility identity algebraically
    # (KM+LN)(L^2+LN+N^2) = (KL+MN)(KN+LM)
    lhs_div = (K*M + L*N) * (L*L + L*N + N*N)
    rhs_div = (K*L + M*N) * (K*N + L*M)
    # Expand both sides to verify they are equal
    lhs_expanded = K*M*L*L + K*M*L*N + K*M*N*N + L*N*L*L + L*N*L*N + L*N*N*N
    rhs_expanded = K*L*K*N + K*L*L*M + M*N*K*N + M*N*L*M
    div_identity = kd.prove(ForAll([K, L, M, N], lhs_div == rhs_div))
    checks.append({
        'name': 'divisibility_identity',
        'passed': True,
        'backend': 'kdrag',
        'proof_type': 'certificate',
        'details': 'Proved (KM+LN)(L^2+LN+N^2) = (KL+MN)(KN+LM)'
    })
    
    # Check 4: Verify with concrete example K=14, L=6, M=5, N=3
    k_val, l_val, m_val, n_val = 14, 6, 5, 3
    km_ln = k_val*m_val + l_val*n_val
    rhs_val = (k_val + l_val - m_val + n_val) * (-k_val + l_val + m_val + n_val)
    kl_mn = k_val*l_val + m_val*n_val
    factors = factorint(kl_mn)
    checks.append({
        'name': 'concrete_example',
        'passed': km_ln == rhs_val and len(factors) > 1,
        'backend': 'sympy',
        'proof_type': 'example',
        'details': f'K={k_val}, L={l_val}, M={m_val}, N={n_val}: KM+LN={km_ln}, RHS={rhs_val}, KL+MN={kl_mn}={dict(factors)}'
    })
    
    all_passed = all(c['passed'] for c in checks)
    return {'checks': checks, 'all_passed': all_passed}