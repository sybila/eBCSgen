from lark import Lark, Transformer, Tree
from lark import UnexpectedCharacters, UnexpectedToken
from lark.load_grammar import _TERMINAL_NAMES

from Core.Formula import Formula, AtomicProposition
from Parsing.ParseBCSL import COMPLEX_GRAMMAR, TreeToComplex


GRAMMAR = """
    start: state_formula
    !state_formula: TRUE | ap | state_formula AND state_formula | NOT state_formula | prob "(" path_formula ")"
    !path_formula: NEXT state_formula | state_formula UNTIL state_formula | FUTURE state_formula

    TRUE: "True"
    NOT: "!"
    AND: "&"
    OR: "|"
    !prob: "P" SIGN number | "P=?"
    NEXT: "X"
    UNTIL: "U"
    FUTURE: "F"

    ap: "[" rate_complex SIGN number "]"
    SIGN: "<" | ">" | "=<" | "=>"

    number: NUMBER

    %import common.NUMBER
    %import common.WS
    %ignore WS
"""

class TreeToStrings(Transformer):
    def _extend_ws(self, matches):
        return " " + str(matches) + " "

    def SIGN(self, matches):
        return self._extend_ws(matches)

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
        grammar = GRAMMAR + COMPLEX_GRAMMAR
        self.parser = Lark(grammar, parser='lalr',
                           propagate_positions=False,
                           maybe_placeholders=False,
                           transformer=TreeToComplex()
                           )

        self.terminals = dict((v, k) for k, v in _TERMINAL_NAMES.items())
        self.terminals.update({"NEXT": "X",
                               "UNTIL": "U",
                               "FUTURE": "F"
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
