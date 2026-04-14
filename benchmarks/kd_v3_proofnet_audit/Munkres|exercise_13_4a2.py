import kdrag as kd
from kdrag.smt import *

def verify():
    checks = []
    all_passed = True
    
    check1 = {
        "name": "counterexample_union_not_topology",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        Element = kd.sort('Element')
        Subset = kd.relation('Subset', Element)
        InTopology1 = kd.relation('InTopology1', Subset)
        InTopology2 = kd.relation('InTopology2', Subset)
        InUnion = kd.relation('InUnion', Subset)
        Union = kd.function('Union', Subset, Subset, Subset)
        
        x, y, z = kd.consts('x y z', Element)
        A, B = kd.consts('A B', Subset)
        empty = kd.define('empty', Subset)
        full = kd.define('full', Subset)
        
        axioms = [
            kd.QForAll([x], ~(x << empty)),
            kd.QForAll([x], x << full),
            x << A,
            ~(y << A),
            ~(z << A),
            x << B,
            y << B,
            ~(z << B),
            Union(A, B) == kd.define('AB', Subset),
            kd.QForAll([x], (x << Union(A, B)) == ((x << A) | (x << B))),
            InTopology1(empty),
            InTopology1(full),
            InTopology1(A),
            ~InTopology1(B),
            ~InTopology1(Union(A, B)),
            InTopology2(empty),
            InTopology2(full),
            ~InTopology2(A),
            InTopology2(B),
            ~InTopology2(Union(A, B)),
            kd.QForAll([A], InUnion(A) == (InTopology1(A) | InTopology2(A)))
        ]
        
        kd.lemma(kd.QExists([A, B], InUnion(A) & InUnion(B) & ~InUnion(Union(A, B))), by=axioms)
        
        check1["status"] = "proved"
        check1["message"] = "Counterexample: union of topologies not closed under finite intersection"
    except kd.kernel.LemmaError as e:
        check1["status"] = "failed"
        check1["message"] = f"Proof failed: {str(e)}"
        all_passed = False
    except Exception as e:
        check1["status"] = "error"
        check1["message"] = str(e)
        all_passed = False
    
    checks.append(check1)
    return {"checks": checks, "all_passed": all_passed}