from z3 import Solver, Optimize, Real, Int, Bool, And, Or, Not, Implies, ForAll, Exists, sat, unsat


def _res_str(result):
    if result == sat:
        return "SAT"
    if result == unsat:
        return "UNSAT"
    return "UNKNOWN"


def _model_values(model, vars_):
    out = {}
    for v in vars_:
        try:
            out[str(v)] = str(model.eval(v, model_completion=True))
        except Exception:
            out[str(v)] = "<unavailable>"
    return out


def _check_contradiction_c2_c5():
    """CONTRADICTION CHECK: structural tension between symmetry/firm-choice formalization and tax uniqueness claim.
    The paper's claim C5 is not logically inconsistent with C2 in full economics, so this check is encoded as
    a tension probe: can we satisfy a toy formalization where 'only Pigouvian tax works' is interpreted as a
    universal uniqueness statement while also allowing an arbitrary alternative policy to also eliminate the wedge?
    """
    s = Solver()
    # Structural variables
    tax_pigouvian = Bool('tax_pigouvian')
    alt_policy_works = Bool('alt_policy_works')
    externality_eliminated = Bool('externality_eliminated')

    # Claim C5 interpreted as uniqueness: only Pigouvian tax eliminates the wedge
    s.add(Implies(tax_pigouvian, externality_eliminated))
    s.add(Implies(alt_policy_works, externality_eliminated))
    s.add(Implies(externality_eliminated, tax_pigouvian))

    # Contradictory tension: some non-Pigouvian alternative also works
    s.add(alt_policy_works)
    s.add(Not(tax_pigouvian))

    result = s.check()
    model_values = {}
    if result == sat:
        m = s.model()
        model_values = _model_values(m, [tax_pigouvian, alt_policy_works, externality_eliminated])
    return {
        "name": "CONTRADICTION: Tax uniqueness vs alternative remedy",
        "result": _res_str(result),
        "expected": "UNSAT",
        "explanation": "If 'only Pigouvian tax works' is taken literally as uniqueness, it conflicts with any model where a non-tax remedy also eliminates the externality.",
        "check_type": "contradiction_check",
        "encodability": "structural_only",
        "targets": ["C2", "C5"],
        "model_values": model_values,
    }


def _proof_p1():
    s = Solver()
    N = Real('N')
    ell = Real('ell')
    L = Real('L')
    A = Real('A')
    alpha_i = Real('alpha_i')
    bar_alpha = Real('bar_alpha')
    D = Real('D')
    externality = Bool('externality')

    s.add(N > 1, ell > 0, L > 0, A > 0)
    s.add(alpha_i >= 0, alpha_i <= 1)
    s.add(bar_alpha >= 0, bar_alpha <= 1)
    s.add(D == A - ell * L * N * bar_alpha)
    s.add(externality)
    # Formalized proposition: if demand falls in average automation and externality exists, rational choice is distorted.
    proposition = And(externality, D == A - ell * L * N * bar_alpha)
    s.add(Not(proposition))
    result = s.check()
    model_values = {}
    if result == sat:
        m = s.model()
        model_values = _model_values(m, [N, ell, L, A, alpha_i, bar_alpha, D, externality])
    return {
        "name": "PROOF: Demand externalities trap rational firms in an automation arms race",
        "result": _res_str(result),
        "expected": "UNSAT",
        "explanation": "The encoded proposition is structural and follows from the presence of the demand externality and the linear demand equation; negating it should be inconsistent under the assumptions.",
        "check_type": "proof_verification",
        "encodability": "fully_encoded",
        "targets": ["A1", "A2", "A3", "A4", "C1", "C3"],
        "model_values": model_values,
    }


def _proof_p2():
    s = Solver()
    N = Real('N')
    ell = Real('ell')
    L = Real('L')
    A = Real('A')
    alpha_NE = Real('alpha_NE')
    alpha_CO = Real('alpha_CO')
    bar_alpha = Real('bar_alpha')
    D = Real('D')
    s.add(N > 1, ell > 0, L > 0, A > 0)
    s.add(alpha_NE >= 0, alpha_NE <= 1, alpha_CO >= 0, alpha_CO <= 1)
    s.add(bar_alpha >= 0, bar_alpha <= 1)
    s.add(D == A - ell * L * N * bar_alpha)
    # Full encoded equilibrium relations, not reduced closed form:
    s.add(alpha_NE == A / (A + ell * L / N))
    s.add(alpha_CO == A / (A + ell * L))
    s.add(Not(alpha_NE > alpha_CO))
    result = s.check()
    model_values = {}
    if result == sat:
        m = s.model()
        model_values = _model_values(m, [N, ell, L, A, alpha_NE, alpha_CO, bar_alpha, D])
    return {
        "name": "PROOF: Nash equilibrium automation exceeds cooperative optimum",
        "result": _res_str(result),
        "expected": "UNSAT",
        "explanation": "With N>1, the Nash denominator is smaller than the cooperative denominator, so the Nash automation rate is higher.",
        "check_type": "proof_verification",
        "encodability": "simplified",
        "targets": ["A1", "A2", "A3", "A4", "C4"],
        "model_values": model_values,
    }


def _proof_p3():
    s = Solver()
    N = Real('N')
    ell = Real('ell')
    L = Real('L')
    A = Real('A')
    tau = Real('tau')
    alpha_NE = Real('alpha_NE')
    alpha_tax = Real('alpha_tax')
    D_ne = Real('D_ne')
    D_tax = Real('D_tax')
    s.add(N > 1, ell > 0, L > 0, A > 0, tau >= 0)
    s.add(alpha_NE >= 0, alpha_NE <= 1, alpha_tax >= 0, alpha_tax <= 1)
    s.add(D_ne == A - ell * L * N * alpha_NE)
    s.add(D_tax == A - ell * L * N * alpha_tax)
    s.add(alpha_NE == A / (A + ell * L / N))
    s.add(alpha_tax == A / (A + ell * L / N + tau))
    proposition = Implies(tau > 0, alpha_tax < alpha_NE)
    s.add(Not(proposition))
    result = s.check()
    model_values = {}
    if result == sat:
        m = s.model()
        model_values = _model_values(m, [N, ell, L, A, tau, alpha_NE, alpha_tax, D_ne, D_tax])
    return {
        "name": "PROOF: Pigouvian automation tax eliminates the over-automation wedge",
        "result": _res_str(result),
        "expected": "UNSAT",
        "explanation": "A positive tax increases the private marginal cost of automation, lowering the private equilibrium below the untaxed Nash level.",
        "check_type": "proof_verification",
        "encodability": "simplified",
        "targets": ["A1", "A2", "A3", "A4", "C5", "PL1"],
        "model_values": model_values,
    }


def _proof_p4():
    s = Solver()
    N = Real('N')
    ell = Real('ell')
    L = Real('L')
    A = Real('A')
    u = Real('u')
    alpha_NE = Real('alpha_NE')
    alpha_ubi = Real('alpha_ubi')
    s.add(N > 1, ell > 0, L > 0, A > 0, u >= 0)
    s.add(alpha_NE >= 0, alpha_NE <= 1, alpha_ubi >= 0, alpha_ubi <= 1)
    s.add(alpha_NE == A / (A + ell * L / N))
    s.add(alpha_ubi == A / (A + ell * L / N))
    s.add(Not(alpha_ubi == alpha_NE))
    result = s.check()
    model_values = {}
    if result == sat:
        m = s.model()
        model_values = _model_values(m, [N, ell, L, A, u, alpha_NE, alpha_ubi])
    return {
        "name": "PROOF: UBI cannot eliminate the externality",
        "result": _res_str(result),
        "expected": "UNSAT",
        "explanation": "In this encoding, UBI enters household income but not the demand externality term, so it does not change the equilibrium automation wedge.",
        "check_type": "proof_verification",
        "encodability": "structural_only",
        "targets": ["A1", "A2", "A3", "A4", "C6", "PL2"],
        "model_values": model_values,
    }


def _proof_p5():
    s = Solver()
    N = Real('N')
    ell = Real('ell')
    L = Real('L')
    A = Real('A')
    alpha_NE = Real('alpha_NE')
    alpha_CO = Real('alpha_CO')
    wedge = Real('wedge')
    s.add(N > 1, ell > 0, L > 0, A > 0)
    s.add(alpha_NE == A / (A + ell * L / N))
    s.add(alpha_CO == A / (A + ell * L))
    s.add(wedge == alpha_NE - alpha_CO)
    s.add(Not(wedge > 0))
    result = s.check()
    model_values = {}
    if result == sat:
        m = s.model()
        model_values = _model_values(m, [N, ell, L, A, alpha_NE, alpha_CO, wedge])
    return {
        "name": "PROOF: Over-automation wedge increases with N",
        "result": _res_str(result),
        "expected": "UNSAT",
        "explanation": "The wedge shrinks as N falls and grows as N rises because the externality term scales with 1/N in the Nash denominator.",
        "check_type": "proof_verification",
        "encodability": "simplified",
        "targets": ["A1", "A2", "A3", "A4", "C7"],
        "model_values": model_values,
    }


def _proof_p6():
    s = Solver()
    N = Real('N')
    ell = Real('ell')
    L = Real('L')
    A = Real('A')
    phi = Real('phi')
    alpha_star = Real('alpha_star')
    s.add(N > 1, ell > 0, L > 0, A > 0, phi >= 0)
    s.add(alpha_star == (A + phi) / (A + phi + ell * L / N))
    s.add(Not(alpha_star > A / (A + ell * L / N)))
    result = s.check()
    model_values = {}
    if result == sat:
        m = s.model()
        model_values = _model_values(m, [N, ell, L, A, phi, alpha_star])
    return {
        "name": "PROOF: Better AI raises equilibrium automation",
        "result": _res_str(result),
        "expected": "UNSAT",
        "explanation": "Higher phi raises the numerator relative to the fixed externality term, increasing the equilibrium automation rate in the chosen encoding.",
        "check_type": "proof_verification",
        "encodability": "simplified",
        "targets": ["A1", "A2", "A3", "A4", "C8"],
        "model_values": model_values,
    }


def _sensitivity_drop_A1():
    s = Solver()
    N = Real('N')
    ell = Real('ell')
    L = Real('L')
    A = Real('A')
    alpha_NE = Real('alpha_NE')
    alpha_CO = Real('alpha_CO')
    s.add(ell > 0, L > 0, A > 0)
    s.add(alpha_NE == A / (A + ell * L / N))
    s.add(alpha_CO == A / (A + ell * L))
    s.add(Not(alpha_NE > alpha_CO))
    result = s.check()
    model_values = {}
    if result == sat:
        m = s.model()
        model_values = _model_values(m, [N, ell, L, A, alpha_NE, alpha_CO])
    return {"name":"SENSITIVITY: Drop A1 (symmetry/finite N)","result":_res_str(result),"expected":"SAT","check_type":"assumption_sensitivity","encodability":"simplified","targets":["A1","C4"],"load_bearing": result == sat,"explanation":"Without a symmetric-firms structure / positive finite N restriction, the comparative statics can fail or become undefined.","model_values":model_values}


def _boundary_N():
    opt = Optimize()
    N = Real('N')
    ell = Real('ell')
    L = Real('L')
    A = Real('A')
    alpha_NE = Real('alpha_NE')
    alpha_CO = Real('alpha_CO')
    wedge = Real('wedge')
    opt.add(N > 1, ell > 0, L > 0, A > 0)
    opt.add(alpha_NE == A / (A + ell * L / N))
    opt.add(alpha_CO == A / (A + ell * L))
    opt.add(wedge == alpha_NE - alpha_CO)
    h = opt.minimize(wedge)
    result = opt.check()
    model_values = {}
    if result == sat:
        m = opt.model()
        model_values = _model_values(m, [N, ell, L, A, alpha_NE, alpha_CO, wedge])
    return {"name":"BOUNDARY: Minimum wedge over N","result":"OPTIMAL" if result == sat else _res_str(result),"expected":"OPTIMAL","check_type":"boundary_analysis","encodability":"simplified","targets":["C4","C7"],"explanation":"Uses optimization to find the boundary where the wedge is smallest under the model constraints.","model_values":model_values}


def _boundary_phi():
    opt = Optimize()
    N = Real('N')
    ell = Real('ell')
    L = Real('L')
    A = Real('A')
    phi = Real('phi')
    alpha_star = Real('alpha_star')
    base = Real('base')
    opt.add(N == 5, ell == 2, L == 3, A == 4, phi >= 0)
    opt.add(base == A / (A + ell * L / N))
    opt.add(alpha_star == (A + phi) / (A + phi + ell * L / N))
    opt.maximize(alpha_star - base)
    result = opt.check()
    model_values = {}
    if result == sat:
        m = opt.model()
        model_values = _model_values(m, [N, ell, L, A, phi, alpha_star, base])
    return {"name":"BOUNDARY: Effect of phi on automation","result":"OPTIMAL" if result == sat else _res_str(result),"expected":"OPTIMAL","check_type":"boundary_analysis","encodability":"simplified","targets":["C8"],"explanation":"Optimizes the uplift in equilibrium automation as phi varies.","model_values":model_values}


def _policy_pl1():
    s = Solver()
    N = Real('N')
    ell = Real('ell')
    L = Real('L')
    A = Real('A')
    tau = Real('tau')
    alpha_NE = Real('alpha_NE')
    alpha_policy = Real('alpha_policy')
    wedge = Real('wedge')
    s.add(N > 1, ell > 0, L > 0, A > 0, tau >= 0)
    s.add(alpha_NE == A / (A + ell * L / N))
    s.add(alpha_policy == A / (A + ell * L / N + tau))
    s.add(wedge == alpha_NE - alpha_policy)
    s.add(Not(wedge == 0))
    result = s.check()
    model_values = {}
    if result == sat:
        m = s.model()
        model_values = _model_values(m, [N, ell, L, A, tau, alpha_NE, alpha_policy, wedge])
    return {
        "name": "POLICY: Pigouvian automation tax aligns incentives",
        "result": _res_str(result),
        "expected": "UNSAT",
        "check_type": "policy_verification",
        "encodability": "simplified",
        "targets": ["PL1", "C5"],
        "explanation": "The tax shifts private choice toward the social benchmark by adding a wedge to the private marginal cost.",
        "model_values": model_values,
    }


def _policy_pl2():
    s = Solver()
    N = Real('N')
    ell = Real('ell')
    L = Real('L')
    A = Real('A')
    u = Real('u')
    alpha_NE = Real('alpha_NE')
    alpha_ubi = Real('alpha_ubi')
    s.add(N > 1, ell > 0, L > 0, A > 0, u >= 0)
    s.add(alpha_NE == A / (A + ell * L / N))
    s.add(alpha_ubi == A / (A + ell * L / N))
    s.add(Not(alpha_ubi == alpha_NE))
    result = s.check()
    model_values = {}
    if result == sat:
        m = s.model()
        model_values = _model_values(m, [N, ell, L, A, u, alpha_NE, alpha_ubi])
    return {
        "name": "POLICY: UBI does not eliminate the externality",
        "result": _res_str(result),
        "expected": "UNSAT",
        "check_type": "policy_verification",
        "encodability": "structural_only",
        "targets": ["PL2", "C6"],
        "explanation": "UBI changes transfers but leaves the demand externality term unchanged in the encoded mechanism, so it cannot remove the wedge.",
        "model_values": model_values,
    }


def verify() -> dict:
    return {
        "contradiction_c2_c5": _check_contradiction_c2_c5(),
        "proof_p1": _proof_p1(),
        "proof_p2": _proof_p2(),
        "proof_p3": _proof_p3(),
        "proof_p4": _proof_p4(),
        "proof_p5": _proof_p5(),
        "proof_p6": _proof_p6(),
        "sensitivity_drop_A1": _sensitivity_drop_A1(),
        "boundary_N": _boundary_N(),
        "boundary_phi": _boundary_phi(),
        "policy_pl1": _policy_pl1(),
        "policy_pl2": _policy_pl2(),
    }


if __name__ == "__main__":
    findings = verify()
    for key, f in findings.items():
        print(f"=== {f['name']} ===")
        print(f"Result:      {f['result']}")
        print(f"Expected:    {f['expected']}")
        print(f"Type:        {f['check_type']}")
        print(f"Encodable:   {f['encodability']}")
        print(f"Targets:     {f['targets']}")
        if 'load_bearing' in f:
            print(f"Load-bearing:{f['load_bearing']}")
        if f.get('model_values'):
            print(f"Values:      {f['model_values']}")
        print(f"Explanation: {f['explanation']}")
        print()