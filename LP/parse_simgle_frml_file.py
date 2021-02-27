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


def parse_single_frml_smaller(sides, start_index):
    """
    :param sides: [a (<) b]
    """
    num1, types1, final_vars_count1 = create_final_vars_and_const_with_brackets(sides[0])
    num2, types2, final_vars_count2 = create_final_vars_and_const_with_brackets(sides[1])
    num, types, final_vars_count = move_vars_and_const(num1, types1, final_vars_count1, num2, types2, final_vars_count2)
    types.append("y")
    final_vars_count.append(1)
    return start_index + 1, "a" + str(start_index), [num, types, final_vars_count]


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
        return start_index + 1, "a" + str(start_index), {
            "a" + str(start_index): parse_single_frml_smaller_eq(single_frml)}
    elif "=>" in single_frml:
        return start_index + 1, "a" + str(start_index), {
            "a" + str(start_index): parse_single_frml_bigger_eq(single_frml)}
    elif ">" in single_frml:
        sides = single_frml.split(">")
        parse_single_frml_smaller_res = parse_single_frml_smaller([sides[1], sides[0]], start_index)
        return parse_single_frml_smaller_res[0], parse_single_frml_smaller_res[1], {
            "a" + str(start_index): parse_single_frml_smaller_res[2]}
    elif "<" in single_frml:
        sides = single_frml.split("<")
        parse_single_frml_smaller_res = parse_single_frml_smaller(sides, start_index)
        return parse_single_frml_smaller_res[0], parse_single_frml_smaller_res[1], {
            "a" + str(start_index): parse_single_frml_smaller_res[2]}
    elif "!=" in single_frml:
        sides = single_frml.split("!=")
        parse_single_frml_smaller_res1 = parse_single_frml_smaller(sides, start_index)
        parse_single_frml_smaller_res2 = parse_single_frml_smaller([sides[1], sides[0]], start_index + 1)
        return start_index + 2, "(" + "a" + str(start_index) + "&y>0)|(" + "a" + str(start_index + 1) + "&y>0)", {
            "a" + str(start_index): parse_single_frml_smaller_res1[2],
            "a" + str(start_index + 1): parse_single_frml_smaller_res2[2]}
    else:  # =
        parse_single_frml_eq_res = parse_single_frml_eq(single_frml)
        return start_index + 2, "a" + str(start_index) + "&" + "a" + str(start_index + 1), {
            "a" + str(start_index): parse_single_frml_eq_res[0],
            "a" + str(start_index + 1): parse_single_frml_eq_res[1]}



