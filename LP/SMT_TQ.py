# y is kept var
import re
from part_one import get_sub_formulas, tseitin_to_cnf
import pprint
from LP.SMT_TQ_Input_test import *
from part_two import get_equation_and_predicates
import numpy as np
from LP.LPInput import LPInput
import copy
from sympy.logic.boolalg import to_dnf
from sympy.logic import simplify_logic

from LP.parse_simgle_frml_file import parse_single_frml


def remove_iff_single_frml(frml):
    if "<->" in frml:
        literals = frml.split("<->")
        frml = "({}&{})|(~{}&~{})".format(literals[0], literals[1], literals[1], literals[0])
    return "(" + frml + ")"


def convert_to_dnf(frml):
    # frml = to_dnf(frml, force=True).replace(" ","")
    frml = frml.replace("^", "~")
    sub_frml = get_sub_formulas(frml, P="P", add_prefix="Q")
    for single_sub_frml_index in range(len(sub_frml)):
        sub_frml[single_sub_frml_index] = remove_iff_single_frml(
            sub_frml[single_sub_frml_index][1:-1])
        print(sub_frml[single_sub_frml_index])
        sub_frml[single_sub_frml_index] = str(to_dnf(sub_frml[single_sub_frml_index], force=True)).replace(" ", "")
    for i in range(len(sub_frml)):
        current_index = sub_frml[i].find("P", 0)
        while current_index != -1:
            end_index = sub_frml[i].find("Q", current_index + 1)
            to_switch_index = int(sub_frml[i][current_index + 1:end_index]) - 1
            sub_frml[i] = sub_frml[i].replace("P" + str(to_switch_index + 1) + "Q", sub_frml[to_switch_index])
            current_index = sub_frml[i].find("P", current_index + 1)
    return simplify_logic(str(to_dnf(sub_frml[-1], force=True)).replace(" ", ""), force=True)


def check_LP_conjunction_satisfiability(LP_conjunction, index_sub_frml_dict):
    b_size = len(LP_conjunction)
    current_vars = []
    if "y>0" in LP_conjunction:
        b_size -= 1
        current_vars.append("y")
    A = []
    b = np.zeros(b_size)
    current_constrain_index_in_b = 0
    for constrain_index in range(len(LP_conjunction)):
        if LP_conjunction[constrain_index] == "y>0":
            continue
        A_row = [0 for i in range(len(current_vars))]
        num, types, final_vars_count = index_sub_frml_dict[LP_conjunction[constrain_index]]

        b[current_constrain_index_in_b] = num
        for var_name_index in range(len(types)):
            if types[var_name_index] not in A_row:
                current_vars.append(types[var_name_index])
                A_row.append(final_vars_count[var_name_index])
            else:
                A_row[current_vars.index(types[var_name_index])] = final_vars_count[var_name_index]
        current_constrain_index_in_b += 1
        A.append(A_row)

    A = np.array([np.pad(A_row, [0, len(current_vars) - len(A_row)]) for A_row in A])
    c = np.zeros(len(current_vars))
    if "y>0" in LP_conjunction:
        c[0] = 1
    res = LPInput(A, b, c)
    if res.solve() > 0:
        return True


def check_LP_satisfiability(dnf_frml, index_sub_frml_dict):
    for conjunction in dnf_frml:
        if check_LP_conjunction_satisfiability(conjunction, index_sub_frml_dict):
            return True
    return False


def parse_frml(frml):
    frml = frml.replace(" ", "")
    print("frml")
    print(frml)

    sub_frml, sub_prdc, args = get_equation_and_predicates(frml)
    current_constrain_index = 0
    index_sub_frml_dict = {}
    sub_frml_as_sat = []
    for i in range(len(sub_frml)):
        current_constrain_index, single_frml_rep, current_index_sub_frml_dict = parse_single_frml(sub_frml[i],
                                                                                                  current_constrain_index)
        index_sub_frml_dict.update(current_index_sub_frml_dict)
        sub_frml_as_sat.append(single_frml_rep)
        frml = frml.replace(sub_frml[i], single_frml_rep)
    pprint.pprint(index_sub_frml_dict)
    dnf_frml = convert_to_dnf(frml)
    if dnf_frml == "False" or dnf_frml == "True":
        return frml
    return dnf_frml, index_sub_frml_dict


def check_formula_LP(frml):
    print(frml)
    frml_parsed, index_sub_frml_dict = parse_frml(frml)
    print("frml_parsed", frml_parsed)
    return check_LP_satisfiability(frml_parsed, index_sub_frml_dict)


if __name__ == "__main__":
    # print(simplify_logic(parse_frml8,deep=True))
    # print("to dnf", str(to_dnf(parse_frml7, force=True)))
    # print(convert_to_dnf("((a|c)<->(b&^a))<->(f<->d)"))
    parse_frml(parse_frml1)
