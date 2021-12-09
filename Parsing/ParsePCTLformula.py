from lark import Lark, Transformer, Tree
from lark import UnexpectedCharacters, UnexpectedToken
from lark.load_grammar import _TERMINAL_NAMES

from Core.Formula import Formula, AtomicProposition
import Parsing.ParseBCSL

GRAMMAR = """
    start: state_formula
    !state_formula: TRUE | ap | state_formula (AND|OR) state_formula | NOT state_formula | prob | brackets
    !path_formula: NEXT state_formula | state_formula UNTIL state_formula | FUTURE state_formula | GLOBAL state_formula

    !brackets: "(" state_formula ")"
    TRUE: "True"
    NOT: "!"
    AND: "&"
    OR: "|"
    !prob: ( pq | pneq ) LB path_formula RB
    NEXT: "X"
    UNTIL: "U"
    FUTURE: "F"
    GLOBAL: "G"

    ap: rate_complex sign_ap number
    sign: e_sign | ne_sign
    e_sign.1: GE | LE
    ne_sign.0: L | G
    sign_ap: EQ | sign

    !pq.1: "P" "=" "?"
    !pneq.0: "P" sign number

    EQ: "="
    GE: ">="
    G: ">"
    LE: "<="
    L: "<"

    LB: "["
    RB: "]"

    number: NUMBER

    %import common.NUMBER
    %import common.WS
    %ignore WS
"""


class TreeToStrings(Transformer):
    def _extend_ws(self, matches):
        return " " + str(matches) + " "

    def LB(self, matches):
        return " " + str(matches)

    def sign_ap(self, matches):
        if type(matches[0]) == str:
            return matches[0]
        else:
            return self._extend_ws(matches[0])

    def sign(self, matches):
        return self._extend_ws(matches[0].children[0])

    def AND(self, matches):
        return self._extend_ws(matches)

    def OR(self, matches):
        return self._extend_ws(matches)

    def UNTIL(self, matches):
        return self._extend_ws(matches)

    def NEXT(self, matches):
        return str(matches) + " "

    def FUTURE(self, matches):
        return str(matches) + " "

    def number(self, matches):
        return matches[0]

    def agent(self, matches):
        return matches[0]

    def ap(self, matches):
        return Tree("ap", [AtomicProposition(*matches)])


class PCTLparser:
    def __init__(self):
        grammar = GRAMMAR + Parsing.ParseBCSL.COMPLEX_GRAMMAR
        self.parser = Lark(grammar, parser='lalr',
                           propagate_positions=False,
                           maybe_placeholders=False,
                           transformer=Parsing.ParseBCSL.TreeToComplex()
                           )

        self.terminals = dict((v, k) for k, v in _TERMINAL_NAMES.items())
        self.terminals.update({"NEXT": "X",
                               "UNTIL": "U",
                               "FUTURE": "F",
                               "EQ": "=", "GE": ">=", "G": ">", "LE": "<=", "L": "<",
                               "DOUBLE_COLON": "::"
                               })

    def replace(self, expected: set) -> set:
        return set([self.terminals.get(item, item) for item in filter(lambda item: item != 'CNAME', expected)])

    def parse(self, expression: str) -> Formula:
        try:
            tree = self.parser.parse(expression)
            tree = TreeToStrings(visit_tokens=True).transform(tree)
            return Formula(True, tree.children[0])
        except UnexpectedCharacters as u:
            return Formula(False, {"unexpected": expression[u.pos_in_stream],
                                   "expected": self.replace(u.allowed),
                                   "line": u.line, "column": u.column})
        except UnexpectedToken as u:
            return Formula(False, {"unexpected": str(u.token),
                                   "expected": self.replace(u.expected),
                                   "line": u.line, "column": u.column})
