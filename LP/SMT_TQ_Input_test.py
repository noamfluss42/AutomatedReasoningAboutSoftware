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

# num 2
# types 0&1
# {'0': [-2.0, ['x1', 'x4', 'x2', 'x3'], [1.0, -10.0, 11.0, 8.0]],
#  '1': [2.0, ['x1', 'x4', 'x2', 'x3'], [-1.0, 10.0, -11.0, -8.0]]}
parse_single_frml1 = "5x1-2(5.5x2+4x3)-2=6x1+-10x4"

# num 3
# types (1&y>0)|(2&y>0)
# {'1': [2.0, ['x1', 'x2', 'x3', 'x4', 'y'], [-1.0, -11.0, -8.0, 10.0, 1]],
#  '2': [-2.0, ['x1', 'x4', 'x2', 'x3', 'y'], [1.0, -10.0, 11.0, 8.0, 1]]}
parse_single_frml2 = "5x1-2(5.5x2+4x3)-2!=6x1+-10x4"

# num 2
# types 1
# [-2.0, ['x1', 'x4', 'x2', 'x3', 'y'], [1.0, -10.0, 11.0, 8.0, 1]]
parse_single_frml3 = "5x1-2(5.5x2+4x3)-2>6x1+-10x4"

# num 2
# types 1
# [-2.0, ['x1', 'x4', 'x2', 'x3', 'y'], [1.0, -10.0, 11.0, 8.0, 1]]
parse_single_frml4 = "5x1-2(5.5x2+4x3)-2<6x1+-10x4"

# num 3
# types 1&2
# {'1': [6.0, ['x1', 'x4', 'x2', 'x3'], [106.0, -10.0, 1000.0, -4.0]],
#  '2': [-6.0, ['x1', 'x4', 'x2', 'x3'], [-106.0, 10.0, -1000.0, 4.0]]}
parse_single_frml5 = "-20(x1+10x2)5+4x3+1=6x1+-10x4-5"

parse_frml1 = "(" + parse_single_frml3 + "|" + parse_single_frml4 + ")&(" + parse_single_frml5 + ")"

parse_frml2 = "(x1+4x2<6)|4x1+-6x3!=2x3"

parse_frml3 = "(x1+4x2<6)->(4x1+-6x3!=2x3)<-->(x1<4)"

parse_frml4 = "((a)>>(b))|(c&d)"

parse_frml5 = "((~a)|(b))&(c&d)"

parse_frml6 = "~(a>>b)|c"
parse_frml7 = "(((~P1a)|P2v)&((~P2)>>P1))"

parse_frml8 = "a|(a&~a)|(~a&~b)|(~a&~c)|(~a&~d)|(~a&~f)|(~d&~f)|(b&c&~a)"#|(~d&~f)|(b&c&~a)"
