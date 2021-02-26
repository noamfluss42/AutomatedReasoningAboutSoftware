# ['2a', '2', '-4', '-3a', '-v', '23x', 'z', '-3.5', '-2.1s', '3!1%', '3.2f', '-!3%5', '-3d']
create_final_vars_and_const_separate1 = "2a+2-4+-3a-v+23x+z+-3.5+-2.1s+3!1%+3.2f+-!3%5-3d"

# {'1': (8.0, [], []),
#  '2': (80.0, ['f', 'd'], [3.2, -3.0]),
#  '3': (160.0, ['f', 'd'], [6.4, -6.0])}
create_final_vars_and_const_with_brackets1 = "2(5(3+5)2+3.2f4-3d)"

# {'1': (-4.0, [], []),
#  '2': (-4.0, ['f', 'd'], [1, 2.5]),
#  '3': (4.0, ['r', 'f', 'd'], [5.0, -1, -2.5])}
create_final_vars_and_const_with_brackets2 = "5r2-(f+2.5d+(1-5-0.5p))"

# [(-156.0, ['f', 'd', 'r', 'p'], [7.4, -3.5, -5.0, -0.5])]
parse_single_frml_smaller_eq1 = create_final_vars_and_const_with_brackets1 + "<=" + create_final_vars_and_const_with_brackets2

# [(156.0, ['r', 'f', 'd', 'p'], [5.0, -7.4, 3.5, 0.5])]
parse_single_frml_bigger_eq1 = create_final_vars_and_const_with_brackets1 + "=>" + create_final_vars_and_const_with_brackets2
