def eval_term(term: str, x: float, y: float) -> float:
    if ('x' not in term) and ('y' not in term):
        return float(int(term))

    if 'x^' in term:
        if term.startswith('x^'):
            exponent = term[2:]
            return x ** int(exponent)
        constant, exponent = term.split('x^')
        return int(constant) * (x ** int(exponent))

    if 'y^' in term:
        if term.startswith('y^'):
            exponent = term[2:]
            return y ** int(exponent)
        constant, exponent = term.split('y^')
        return int(constant) * (y ** int(exponent))

    # linear term: "3x", "-2y", "x", "y"
    constant = term[:-1]
    if constant == "":
        constant = 1
    variable = term[-1]
    if variable == 'x':
        return int(constant) * x
    if variable == 'y':
        return int(constant) * y
    raise ValueError(f"Bad term: {term}")


def eval_polynomial(p: str, x: float, y: float) -> float:
    p = (p or "").strip()
    if p == '':
        return 0.0

    result = 0.0
    sign = 1
    for part in p.split():
        if part == '+':
            sign = 1
        elif part == '-':
            sign = -1
        else:
            result += sign * eval_term(part, x, y)
    return result
