from lark import Lark, Tree, Transformer
from lark import UnexpectedCharacters, UnexpectedToken
from lark.load_grammar import _TERMINAL_NAMES

from Core.Formula import Formula, AtomicProposition
import Parsing.ParseBCSL


class TreeToStrings(Transformer):
    def _extend_ws(self, matches):
        return " " + str(matches) + " "

    def sign_ap(self, matches):
        if type(matches[0]) == str:
            return matches[0]
        else:
            return self._extend_ws(matches[0])

    def sign(self, matches):
        return self._extend_ws(matches[0].children[0])

    def number(self, matches):
        return matches[0]

    def agent(self, matches):
        return matches[0]

    def ap(self, matches):
        return Tree("ap", [AtomicProposition(*matches[1:4])])


class CTLparser:
    """
    A class to parse a CTL formula.
    """

    grammar = r"""
        start: formula
        !formula: "true"
               | "false" 
               | ap
               | "~" formula
               | "(" formula ")"
               | formula ("and" | "&") formula
               | formula ("or" | "|") formula
               | formula "->" formula
               | formula "<->" formula
               | "A" "(" state_formula ")"
               | "E" "(" state_formula ")"
               
        !state_formula: "X" "(" formula ")"
                     | "F" "(" formula ")"
                     | "G" "(" formula ")"
                     | formula "U" formula
                 
        ap: LB rate_complex sign_ap number RB
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

        %import common.ESCAPED_STRING
        %import common.WS
        %ignore WS
        """

    def __init__(self):
        grammar = CTLparser.grammar + Parsing.ParseBCSL.COMPLEX_GRAMMAR
        self.parser = Lark(grammar, parser='lalr',
                           propagate_positions=False,
                           maybe_placeholders=False,
                           transformer=Parsing.ParseBCSL.TreeToComplex()
                           )

        self.terminals = dict((v, k) for k, v in _TERMINAL_NAMES.items())

    def replace(self, expected: set) -> set:
        return set([self.terminals.get(item, item) for item in filter(lambda item: item != 'CNAME', expected)])

    def parse(self, expression: str) -> Formula:
        try:
            tree = self.parser.parse(expression)
            tree = TreeToStrings().transform(tree)
            return Formula(True, tree.children[0])
        except UnexpectedCharacters as u:
            return Formula(False, {"unexpected": expression[u.pos_in_stream],
                                   "expected": self.replace(u.allowed),
                                   "line": u.line, "column": u.column})
        except UnexpectedToken as u:
            return Formula(False, {"unexpected": str(u.token),
                                   "expected": self.replace(u.expected),
                                   "line": u.line, "column": u.column})
