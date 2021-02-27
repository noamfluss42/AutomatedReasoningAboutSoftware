import re
from typing import Optional


def neg_literal(lit: str):
    return "^" + lit if lit[0] != "^" else lit[1:]


def get_sub_formulas(formula: str, P="P", add_prefix = "") -> list:
    sub_formulas = []
    # split the formula to the different subformulas
    while re.search("(\^" + P + "\d+|[(][^()]*[)])", formula) is not None:
        a = re.search("(\^" + P + "\d+)", formula)
        if a is None:
            a = re.search("(\^" + P + "\d+|[(][^()]*[)])", formula)
        start = a.start(0)
        end = a.end(0)
        sub_formulas.append(formula[start:end])
        formula = formula.replace(sub_formulas[-1], P + str(len(sub_formulas)) + add_prefix, 1)
    if not re.fullmatch(P + "\d+", formula):
        sub_formulas.append("(" + formula + ")")
    return sub_formulas

#
# print(get_sub_formulas("2((3+5)+3.2f+(-53.2(-5s+4))-3d)+(3)", P="!",add_prefix="%"))
# print(get_sub_formulas("", P="!"))


def tseitin_to_cnf(formula: str, index: int) -> list:
    if re.fullmatch("\^P\d+", formula):
        return ["^P{0}|{1}".format(index, formula), "P{0}|{1}".format(index, formula[1:])]
    formula = formula[1:-1]  # move the brackets at the start and the end
    if "<->" in formula:
        literals = formula.split("<->")
        cnf = [
            "^P{0}|^{1}|{2}".format(index, literals[0], literals[1]),
            "^P{0}|{1}|^{2}".format(index, literals[0], literals[1]),
            "P{0}|{1}|{2}".format(index, literals[0], literals[1]),
            "P{0}|^{1}|^{2}".format(index, literals[0], literals[1])
        ]
        return cnf
    if "&" in formula:
        sep = "&"
        literals = formula.split(sep)

        frml = formula.replace("&", "|^")
        frml = "P{0}|^{1}".format(index, frml)
        cnf = [frml]
        for literal in literals:
            cnf.append("^P{0}|{1}".format(index, literal))
        return cnf
    if "->" in formula:
        formula = "^" + formula.replace("->", "|")
    if "|" in formula:
        sep = "|"
        literals = formula.split(sep)

        frml = "^P{0}|{1}".format(index, formula)
        cnf = [frml]
        for literal in literals:
            cnf.append("P{0}|^{1}".format(index, literal))
        return cnf

    return [formula]


def tseitin_transformation(formula: str) -> list:
    """

    :param formula:
    :return: the formula after performing tseitin's transformation.
    """
    formula = formula.replace(" ", "")
    sub_formulas = get_sub_formulas(formula)
    # change to CNF
    cnf_formulas = []
    for i in range(len(sub_formulas)):
        cnf_formulas += tseitin_to_cnf(sub_formulas[i], i + 1)
    cnf_formulas.append("P" + str(len(sub_formulas)))

    return cnf_formulas


def preprocessing(cnf_formula: list) -> list:
    new_cnf_formula = []
    for frml in cnf_formula:
        frml = frml.replace("^^", "")
        literals = frml.split("|")
        normal = set([x for x in literals if x[0] != "^"])
        neg = set([x[1:] for x in literals if x[0] == "^"])
        if not normal.isdisjoint(neg):
            continue
        new_frml = "|".join(set(literals))
        if new_frml not in new_cnf_formula:
            new_cnf_formula.append(new_frml)
    return new_cnf_formula


def assign_literal(lit: str, t_assigned_order: list, t_assigned_dec: list, t_assigned_frml: list, frml="split",
                   offset=0):
    t_assigned_order.append(lit)
    t_assigned_frml.append(frml)
    if len(t_assigned_dec) == 0:
        t_assigned_dec.append(offset)
    else:
        t_assigned_dec.append(t_assigned_dec[-1] + offset)


# def unit_propagation(cnf_formula: list, t_order: list, t_dec: list, t_frml: list) -> Optional[str]:
#     for frml in cnf_formula:
#         literals = frml.split("|")
#         if not set(literals).isdisjoint(set(t_order)):
#             continue
#         new_literals = []
#         for lit in literals:
#             neg_lit = neg_literal(lit)
#             if neg_lit not in t_order:
#                 new_literals.append(lit)
#         if len(new_literals) == 0:
#             return frml
#         if len(new_literals) == 1:
#             assign_literal(new_literals[-1], t_order, t_dec, t_frml, frml=frml)
#     return None


def reset_watch_literals(cnf_formula: list, watch_literals: list, t_order: list):
    for i in range(len(cnf_formula)):
        literals = cnf_formula[i].split("|")
        if not set(literals).isdisjoint(set(t_order)):
            continue
        new_literals = []
        for lit in literals:
            neg_lit = neg_literal(lit)
            if neg_lit not in t_order:
                new_literals.append(lit)
                if len(new_literals) >= 2:
                    break
        watch_literals[i] = new_literals


def update_watch_literals(cnf_formula: list, update_wtach: str, watch_literals: list, t_order: list):
    for i in range(len(cnf_formula)):
        literals = cnf_formula[i].split("|")
        if not set(literals).isdisjoint(set(t_order)):
            continue
        neg = neg_literal(update_wtach)
        if neg in watch_literals[i]:
            new_literals = []
            for lit in literals:
                neg_lit = neg_literal(lit)
                if neg_lit not in t_order:
                    new_literals.append(lit)
                    if len(new_literals) >= 2:
                        break
            watch_literals[i] = new_literals


def watch_propagation(cnf_formula: list, watch_literals: list, t_assigned_order: list, t_assigned_dec: list,
                      t_assigned_frml: list):
    for i in range(len(cnf_formula)):
        literals = cnf_formula[i].split("|")
        if not set(literals).isdisjoint(set(t_assigned_order)):
            continue
        if len(watch_literals[i]) == 0:
            return cnf_formula[i]
        if len(watch_literals[i]) == 1:
            assign_literal(watch_literals[i][0], t_assigned_order, t_assigned_dec, t_assigned_frml, frml=cnf_formula[i])
            update_watch_literals(cnf_formula, watch_literals[i][0], watch_literals, t_assigned_order)
            return None


def case_splitting(t_assigned_order: list, t_assigned_dec: list, t_assigned_frml: list, all_literals: list):
    for lit in all_literals:
        if lit not in t_assigned_order and neg_literal(lit) not in t_assigned_order:
            assign_literal(lit, t_assigned_order, t_assigned_dec, t_assigned_frml, offset=1)
            break


def DLIS(cnf: list, watch_literals: list, t_assigned_order: list, t_assigned_dec: list, t_assigned_frml: list):
    num_of_satisf_clauses = {}
    for frml in cnf:
        literals = frml.split("|")
        if not set(literals).isdisjoint(set(t_assigned_order)):
            continue
        for lit in literals:
            if lit in t_assigned_order or neg_literal(lit) in t_assigned_order:
                continue
            if lit in num_of_satisf_clauses:
                num_of_satisf_clauses[lit] = num_of_satisf_clauses[lit] + 1
            else:
                num_of_satisf_clauses[lit] = 0
    lit_to_add = max(num_of_satisf_clauses, key=num_of_satisf_clauses.get)
    assign_literal(lit_to_add, t_assigned_order, t_assigned_dec,
                   t_assigned_frml, offset=1)
    update_watch_literals(cnf, lit_to_add, watch_literals, t_assigned_order)


def check_assign_sat_cnf(cnf_formula: list, t_assigned: list) -> bool:
    for frml in cnf_formula:
        literals = frml.split("|")
        if set(literals).isdisjoint(set(t_assigned)):
            return False
    return True


def check_one_lit_in_last_dec_lvl(lits: list, t_order: list, t_dec: list) -> bool:
    flag = False
    for lit in lits:
        indx = t_order.index(neg_literal(lit))
        if t_dec[indx] == t_dec[-1]:
            if flag:
                return False
            flag = True
    if flag:
        return True
    print("0 literals in the last dec lvl")
    return False


def process_after_conflict(conflict_literals, lit_to_remove):
    frml = "|".join(conflict_literals)
    frml.replace("^^", "")
    conflict_literals = frml.split("|")
    conflict_literals = list(set(conflict_literals))
    conflict_literals.remove(lit_to_remove)
    conflict_literals.remove(neg_literal(lit_to_remove))
    return conflict_literals


def handle_conflict(conflict, t_order, t_dec, t_frml) -> str:
    conflict_literals = conflict.split("|")
    for i in range(1, len(t_order) + 1):
        if check_one_lit_in_last_dec_lvl(conflict_literals, t_order, t_dec):
            break
        lit = t_order[-i]
        if neg_literal(lit) in conflict_literals:
            conflict_literals += t_frml[-i].split("|")
            conflict_literals = process_after_conflict(conflict_literals, lit)
    return "|".join(conflict_literals)


def find_level_to_backjump(conflict, t_order, t_dec):
    dec_lvls = []
    for lit in conflict.split("|"):
        indx = t_order.index(neg_literal(lit))
        dec_lvls.append(t_dec[indx])
    if len(dec_lvls) < 2:
        return 0
    dec_lvls.sort()
    return dec_lvls[-2]


def main():
    org_formula = "(x1 <-> x2) & (x1 <-> ^x2)"
    cnf = tseitin_transformation(org_formula)
    print(cnf)
    cnf = preprocessing(cnf)
    print(cnf)
    watch_literals = [cla.split("|")[:2] for cla in cnf]
    all_literals = []
    for frml in cnf:
        all_literals += frml.split("|")
    all_literals = list(set(all_literals))

    t_assigned_order = []  # the literal that get a True assignment
    t_assigned_dec = []  # the decision level
    t_assigned_frml = []  # the fornula we used (or "split" for case splitting

    print(org_formula)

    while True:
        old = len(t_assigned_order)
        # conflict = unit_propagation(cnf, t_assigned_order, t_assigned_dec, t_assigned_frml)
        conflict = watch_propagation(cnf, watch_literals, t_assigned_order, t_assigned_dec, t_assigned_frml)
        if conflict is not None:
            if t_assigned_dec[-1] == 0:
                print("UNSAT")
                exit()
            conflict = handle_conflict(conflict, t_assigned_order, t_assigned_dec, t_assigned_frml)
            lvl_to_backjump = find_level_to_backjump(conflict, t_assigned_order, t_assigned_dec)
            indx_to_backjump = t_assigned_dec.index(lvl_to_backjump + 1)
            cnf.append(conflict)
            watch_literals.append([])
            t_assigned_order = t_assigned_order[:indx_to_backjump]
            t_assigned_dec = t_assigned_dec[:indx_to_backjump]
            t_assigned_frml = t_assigned_frml[:indx_to_backjump]
            reset_watch_literals(cnf, watch_literals, t_assigned_order)
            continue

        new = len(t_assigned_order)
        # cant propagate any more
        if old == new:
            if check_assign_sat_cnf(cnf, t_assigned_order):
                break
            DLIS(cnf, watch_literals, t_assigned_order, t_assigned_dec, t_assigned_frml)

    # complete the assignment to all the literals:
    old = 0
    new = 1
    while old != new:
        old = len(t_assigned_order)
        case_splitting(t_assigned_order, t_assigned_dec, t_assigned_frml, all_literals)
        new = len(t_assigned_order)

    # print the final assignment
    t_assigned_order.sort()
    print("SAT")
    print([i for i in t_assigned_order if i[0] != "P" and i[:2] != "^P"])
#
if __name__ == "__main__":
    #print(get_sub_formulas("2((3+5)+3.2f+(-53.2(-5s+4))-3d)+(3)", P="!",add_prefix="%"))
    #print(get_sub_formulas("", P="!"))
    #main()
    print(get_sub_formulas("3&(^3|2&(9&4)|1)"))

# cnf = [
#     "x2|x3|^x4",
#     "^x2|^x1",
#     "^x3|^x4",
#     "x4|x5|x6",
#     "^x5|x7",
#     "^x6|x7|^x8"
# ]

# t_assigned_order = ["x1", "^x2", "x8", "^x7", "^x5", "^x6", "x4", "^x3"]
# t_assigned_dec = [0, 0, 1, 2, 2, 2, 2, 2]
# t_assigned_frml = ["split", "^x2|^x1", "split", "split", "^x5|x7", "^x6|x7|^x8", "x4|x5|x6", "^x3|^x4"]
