import re

# coef can be: "", "+", "-", "12", "-3", "+7"
_TERM_RE = re.compile(
    r"^\s*(?P<coef>(?:[+-]?\d+|[+-]))?(?:(?P<var>[xy])(?:\^(?P<pow>\d+))?)?\s*$"
)


def eval_term(term: str, x: float, y: float) -> float:
    term = term.strip()
    if term == "":
        return 0.0

    m = _TERM_RE.match(term)
    if not m:
        raise ValueError(f"Bad term: {term}")

    coef_s = m.group("coef")
    var = m.group("var")
    pow_s = m.group("pow")

    # Determine coefficient
    if coef_s is None or coef_s == "":
        coef = 1
    elif coef_s == "+":
        coef = 1
    elif coef_s == "-":
        coef = -1
    else:
        coef = int(coef_s)

    # Constant term (no variable)
    if var is None:
        return float(coef)

    base = x if var == "x" else y
    power = int(pow_s) if pow_s is not None else 1
    return float(coef) * (base ** power)


def eval_polynomial(p: str, x: float, y: float) -> float:
    """
    Polynomial evaluator supporting x/y, integer coefficients, +/-, and ^ exponent.
    Spaces are optional.

    Examples:
      y
      -x
      y-x
      2x+3y-10
      x^2 - y^2 + 3x - 2y + 5
    """
    p = (p or "").strip()
    if p == "":
        return 0.0

    s = p.replace(" ", "")
    if s == "":
        return 0.0

    # Ensure expression starts with an explicit sign for easy splitting
    if s[0] not in "+-":
        s = "+" + s

    # Split into signed chunks: "+2x", "-y", "+5", "-3x^2", ...
    parts = re.findall(r"[+-][^+-]+", s)

    result = 0.0
    for part in parts:
        sign = part[0]  # '+' or '-'
        term = part[1:]  # remainder
        signed_term = sign + term  # keep the sign for eval_term (handles "+x", "-x")
        result += eval_term(signed_term, x, y)

    return result
