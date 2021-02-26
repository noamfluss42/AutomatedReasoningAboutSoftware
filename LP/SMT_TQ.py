# y is kept var
import re
from part_one import get_sub_formulas
import pprint
from LP.SMT_TQ_Input_test import *
from part_two import get_equation_and_predicates
import numpy as np
from LP.LPInput import LPInput


# separate the string to list such that if we sum the values we get the string
def create_final_vars_and_const_separate(single_frml_side):
    vars_and_const = re.split("\+", single_frml_side)
    final_vars_and_const_separate = []
    for i in range(len(vars_and_const)):
        if "-" in vars_and_const[i][1:]:
            vars_and_const_minus = vars_and_const[i].split("-")
            start_index_minus = len(final_vars_and_const_separate)
            for j in range(len(vars_and_const_minus)):
                final_vars_and_const_separate.append("-" + vars_and_const_minus[j])
            if vars_and_const[i][0] == "-":
                del final_vars_and_const_separate[start_index_minus]
            else:
                final_vars_and_const_separate[start_index_minus] = final_vars_and_const_separate[start_index_minus][1:]
        else:
            final_vars_and_const_separate.append(vars_and_const[i])
    return final_vars_and_const_separate


# TODO smart
def to_float(s):
    if s == "-":
        return -1
    try:
        f_s = float(s)
    except ValueError:
        f_s = None
    return f_s


# TODO do not return types
def sum_mul_const_single_frml_side(num, types, final_vars_count, coefficient):
    num *= coefficient
    final_vars_count = [i * coefficient for i in final_vars_count]
    return num, types, final_vars_count


def sum_2_single_frml_side(num1, types1, final_vars_count1, num2, types2, final_vars_count2):
    num = num1 + num2
    # TODO need copy?
    types = types1.copy()
    final_vars_count = final_vars_count1.copy()
    for type_index in range(len(types2)):
        if types2[type_index] not in types:
            types.append(types2[type_index])
            final_vars_count.append(final_vars_count2[type_index])
        else:
            final_vars_count[types.index(types2[type_index])] += final_vars_count2[type_index]
    return num, types, final_vars_count


def create_final_vars_and_const(single_frml_side, single_frml_side_without_bracket_solved: dict):
    """
    :param single_frml_side: string without =,!=,<,>,(,)
    :return: num - the sum of the numerical values
            types - the var names
            final_vars_count - the coefficient of the var in types with the same index
    """
    final_vars_and_const_separate = create_final_vars_and_const_separate(single_frml_side)

    types = []
    num = 0
    final_vars_count = []
    for i in range(len(final_vars_and_const_separate)):

        element = final_vars_and_const_separate[i]
        to_float_res = to_float(element)
        if to_float_res is not None:
            num += to_float_res
        else:
            if "!" not in element:
                start_name_index = element.find(re.findall("[a-zA-Z]", element)[0])
            else:
                start_name_index = element.find("!")
            type_name = element[start_name_index:]
            if start_name_index == 0:
                type_num = 1
            elif element[0] == "-" and start_name_index == 1:
                type_num = -1
            else:
                type_num = to_float(element[:start_name_index])

            if "!" in element and element.find("%") != len(element) - 1:
                type_num *= to_float(element[element.find("%") + 1:])
            if "!" in element:
                num_element, types_element, final_vars_count_element = single_frml_side_without_bracket_solved[
                    type_name[type_name.find("!") + 1:type_name.find("%")]]
                num_element, types_element, final_vars_count_element = sum_mul_const_single_frml_side(num_element,
                                                                                                      types_element,
                                                                                                      final_vars_count_element,
                                                                                                      type_num)
                num, types, final_vars_count = sum_2_single_frml_side(num, types, final_vars_count, num_element,
                                                                      types_element, final_vars_count_element)
            else:
                if type_name not in types:
                    types.append(type_name)
                    final_vars_count.append(type_num)
                else:
                    final_vars_count[types.index(type_name)] += type_num

    return num, types, final_vars_count


def create_final_vars_and_const_with_brackets(single_frml_side):
    """
    :param single_frml_side: string without =,!=,<,>
    :return: num - the sum of the numerical values
            types - the var names
            final_vars_count - the coefficient of the var in types with the same index
    """
    if "(" not in single_frml_side:
        return create_final_vars_and_const(single_frml_side, {})

    single_frml_side_without_bracket = get_sub_formulas(single_frml_side, P="!", add_prefix="%")
    single_frml_side_without_bracket_solved = {}

    for current_index in range(len(single_frml_side_without_bracket)):
        single_frml_side_without_bracket_solved[str(current_index + 1)] = create_final_vars_and_const(
            single_frml_side_without_bracket[current_index][1:-1], single_frml_side_without_bracket_solved)
    return single_frml_side_without_bracket_solved[str(len(single_frml_side_without_bracket))]


def move_vars_and_const(num1, types1, final_vars_count1, num2, types2, final_vars_count2):
    """
    :return: num is in the 2 side
            the vars are in 1 side
    """
    num2, types2, final_vars_count2 = sum_mul_const_single_frml_side(num2, types2, final_vars_count2, -1)
    num, types, final_vars_count = sum_2_single_frml_side(num1, types1, final_vars_count1, num2, types2,
                                                          final_vars_count2)
    return -num, types, final_vars_count


def parse_single_frml_smaller_eq(single_frml):
    sides = single_frml.split("<=")
    print("sides\n", sides)
    num1, types1, final_vars_count1 = create_final_vars_and_const_with_brackets(sides[0])
    num2, types2, final_vars_count2 = create_final_vars_and_const_with_brackets(sides[1])
    return list(move_vars_and_const(num1, types1, final_vars_count1, num2, types2, final_vars_count2))


def parse_single_frml_bigger_eq(single_frml):
    sides = single_frml.split("=>")
    num1, types1, final_vars_count1 = create_final_vars_and_const_with_brackets(sides[0])
    num2, types2, final_vars_count2 = create_final_vars_and_const_with_brackets(sides[1])
    return list(move_vars_and_const(num2, types2, final_vars_count2, num1, types1, final_vars_count1))


def parse_single_frml_eq(single_frml):
    sides = single_frml.split("=")
    num1, types1, final_vars_count1 = create_final_vars_and_const_with_brackets(sides[0])
    num2, types2, final_vars_count2 = create_final_vars_and_const_with_brackets(sides[1])
    num, types, final_vars_count = move_vars_and_const(num2, types2, final_vars_count2, num1, types1, final_vars_count1)
    num_rev, types_rev, final_vars_count_rev = sum_mul_const_single_frml_side(num, types, final_vars_count, -1)
    return [[num, types, final_vars_count], [num_rev, types_rev, final_vars_count_rev]]


def parse_single_frml_bigger(sides, start_index):
    """
    :param sides: [a (<) b]
    """
    num1, types1, final_vars_count1 = create_final_vars_and_const_with_brackets(sides[0])
    num2, types2, final_vars_count2 = create_final_vars_and_const_with_brackets(sides[1])
    num, types, final_vars_count = move_vars_and_const(num1, types1, final_vars_count1, num2, types2, final_vars_count2)
    types.append("y")
    final_vars_count.append(1)
    return start_index + 1, str(start_index), [num, types, final_vars_count]


# TODO =,!=, <, >
def parse_single_frml(single_frml, start_index):
    """

    :param single_frml:
    :param start_index:
    :return:
            new start_index
            sat string to replace frml with
            dict from index to parsed frml
    """
    if "<=" in single_frml:
        return start_index + 1, str(start_index), {str(start_index): parse_single_frml_smaller_eq(single_frml)}
    elif "=>" in single_frml:
        return start_index + 1, str(start_index), {str(start_index): parse_single_frml_bigger_eq(single_frml)}
    elif ">" in single_frml:
        sides = single_frml.split(">")
        return parse_single_frml_bigger(sides, start_index)
    elif "<" in single_frml:
        sides = single_frml.split(">")
        return parse_single_frml_bigger([sides[1], sides[0]], start_index)
    elif "!=" in single_frml:
        sides = single_frml.split("!=")
        parse_single_frml_bigger_res1 = parse_single_frml_bigger(sides, start_index)
        parse_single_frml_bigger_res2 = parse_single_frml_bigger([sides[1], sides[0]], start_index + 1)
        return start_index + 2, "(" + str(start_index) + "&y>0)|(" + str(start_index + 1) + "&y>0)", {
            str(start_index): parse_single_frml_bigger_res1[2], str(start_index + 1): parse_single_frml_bigger_res2[2]}
    else:  # =
        parse_single_frml_eq_res = parse_single_frml_eq(single_frml)
        return start_index + 2, str(start_index) + "&" + str(start_index + 1), {
            str(start_index): parse_single_frml_eq_res[0], str(start_index + 1): parse_single_frml_eq_res[1]}


def convert_to_dnf(frml):
    """
    :param frml:
    :return: list of lists
            each inner list is the conjunction of tha values
            the outer list is the disjunction of the inner lists
            the values in the inner list are index (as string) from the frml
            if there are few y > 0 remove such that there is only one in each inner
    """

    return frml


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
    dnf_frml = convert_to_dnf(frml)
    # check LP satisfiability
    return check_LP_satisfiability(dnf_frml, index_sub_frml_dict)


if __name__ == "__main__":
    frml = "(w+q <= 4|(r(o)+3)=e)&(r(r(r(t))) = t)& (g(a) = c) & (f(g(a)) != f(c) | g(a) = d) & (c != d) & (p(a) | p(b)) & (p(a) | ^p(b))"
    print(frml)
    print(get_sub_formulas(frml))
    pprint.pprint(parse_single_frml_smaller_eq(parse_single_frml_smaller_eq1))
    pprint.pprint(parse_single_frml_bigger_eq(parse_single_frml_bigger_eq1))
