import re


def neg_literal(lit: str):
    return "^" + lit if lit[0] != "^" else lit[1:]
    # return ("^" + lit).replace("^^", "")


def get_equation_and_predicates(formula: str) -> (list, list, list):
    formula = formula.replace(" ", "")
    equations = []
    op_predicates = []
    frml_args = []
    open_brck = []
    for i in range(len(formula)):
        if formula[i] == "(":
            open_brck.append(i)
        elif formula[i] == ")":
            if len(open_brck) == 0:
                print("problem...")
            open_indx = open_brck.pop()
            for part in re.split("[&|]", formula[(open_indx + 1):i]):
                if "=" in part:
                    equations.append(part)
                elif "(" in part or ")" in part:
                    op_predicates.append(part)
            frml_args += re.split("[&|=]", formula[(open_indx + 1):i])
    if len(open_brck) != 0:
        print("problem...")
    final_args = [arg.replace("!", "") for arg in frml_args]
    check_frml = "".join(equations)
    predicates = [pre for pre in op_predicates if pre not in check_frml]
    return list(set(equations)), list(set(predicates)), list(set(final_args))


def main():
    frml = "(w+q <= 4|(r(o)+3)=e)&(r(r(r(t))) = t)& (g(a) = c) & (f(g(a)) != f(c) | g(a) = d) & (c != d) & (p(a) | p(b)) & (p(a) | ^p(b))"
    frml = frml.replace(" ", "")
    sub_frml, sub_prdc, args = get_equation_and_predicates(frml)
    print(frml)
    print("->")
    print(sub_frml)
    print(sub_prdc)
    print(args)
    frml = preprocess_formula(frml, sub_frml, sub_prdc, args)
    print(frml)

if __name__ == "__main__":
    main()
