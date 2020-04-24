import collections
import json
from numpy import inf
import numpy as np
from copy import deepcopy
from lark import Lark, Transformer, Tree, Token
from lark import UnexpectedCharacters, UnexpectedToken
from lark.load_grammar import _TERMINAL_NAMES

from Core.Atomic import AtomicAgent
from Core.Complex import Complex
import Core.Model
from Core.Rate import Rate
from Core.Rule import Rule
from Core.Structure import StructureAgent
from TS.State import State
from TS.TransitionSystem import TransitionSystem
from TS.Edge import edge_from_dict
from Core.Side import Side


def load_TS_from_json(json_file: str) -> TransitionSystem:
    """
    Loads given JSON and interprets it as a TransitionSystem.

    :param json_file: given TS in JSON
    :return: resulting TransitionSystem
    """
    complex_parser = Parser("rate_complex")
    with open(json_file) as json_file:
        data = json.load(json_file)

        ordering = tuple(map(lambda agent: complex_parser.parse(agent).data.children[0], data['ordering']))
        ts = TransitionSystem(ordering)
        ts.states_encoding = {State(np.array(eval(data['nodes'][node_id]))): int(node_id) for node_id in data['nodes']}
        ts.edges = {edge_from_dict(edge) for edge in data['edges']}
        ts.init = data['initial']

        ts.unprocessed = {State(np.array(eval(state))) for state in data.get('unprocessed', list())}
        ts.processed = ts.states_encoding.keys() - ts.unprocessed
        return ts


class Result:
    """
    Class to represent output from the Parser.
    """
    def __init__(self, success, data):
        self.success = success
        self.data = data


class SideHelper:
    """
    Class to represent side of a rule.
    """
    def __init__(self):
        self.seq = []
        self.comp = []
        self.complexes = []
        self.counter = 0

    def __str__(self):
        return " | ".join([str(self.seq), str(self.comp), str(self.complexes), str(self.counter)])

    def __repr__(self):
        return str(self)

    def to_side(self):
        return Side([Complex(self.seq[c[0]:c[1]+1], self.comp[c[0]]) for c in self.complexes])


GRAMMAR = r"""
    model: rules inits definitions (complexes)?

    rules: RULES_START (rule|COMMENT)+
    inits: INITS_START (init|COMMENT)+
    definitions: DEFNS_START (definition|COMMENT)+
    complexes: COMPLEXES_START (cmplx_dfn|COMMENT)+

    init: const? rate_complex (COMMENT)?
    definition: def_param "=" number (COMMENT)?
    rule: side ARROW side ("@" rate)? (";" variable)? (COMMENT)?
    cmplx_dfn: cmplx_name "=" sequence (COMMENT)?

    side: (const? complex "+")* (const? complex)?
    complex: (abstract_sequence|sequence|cmplx_name) DOUBLE_COLON compartment

    !rate : fun "/" fun | fun
    !fun: const | param | rate_agent | fun "+" fun | fun "-" fun | fun "*" fun | fun POW const | "(" fun ")"

    !rate_agent: "[" rate_complex "]"

    COMMENT: "//" /[^\n]/*

    COM: "//"
    POW: "**"
    ARROW: "=>"
    RULES_START: "#! rules"
    INITS_START: "#! inits"
    DEFNS_START: "#! definitions"
    COMPLEXES_START: "#! complexes"

    param: CNAME
    def_param : CNAME
    number: NUMBER

    const: (INT|DECIMAL)

    %import common.WORD
    %import common.NUMBER
    %import common.INT
    %import common.DECIMAL
    %import common.WS
    %ignore WS
    %ignore COMMENT
"""

EXTENDED_GRAMMAR = """
    abstract_sequence: atomic_complex | atomic_structure_complex | structure_complex
    atomic_complex: atomic ":" (cmplx_name|VAR)
    atomic_structure_complex: atomic ":" structure ":" (cmplx_name|VAR)
    structure_complex: structure ":" (cmplx_name|VAR)

    variable: VAR "=" "{" cmplx_name ("," cmplx_name)+ "}"
    VAR: "?"
"""

COMPLEX_GRAMMAR = """
    rate_complex: (sequence|cmplx_name) DOUBLE_COLON compartment
    sequence: (agent ".")* agent
    agent: atomic | structure
    structure: s_name "(" composition ")"
    composition: (atomic ",")* atomic?
    atomic : a_name "{" state "}"

    a_name: CNAME
    s_name: CNAME
    compartment: CNAME
    cmplx_name: CNAME
    !state: (DIGIT|LETTER|"+"|"-"|"*"|"_")+

    DOUBLE_COLON: "::"

    %import common.CNAME
    %import common.LETTER
    %import common.DIGIT
"""


class ReplaceVariables(Transformer):
    """
    This class is used to replace variables in rule (marked by ?) by
    the given cmplx_name (so far limited only to that).
    """
    def __init__(self, to_replace):
        super(Transformer, self).__init__()
        self.to_replace = to_replace

    def VAR(self, matches):
        return deepcopy(self.to_replace)


class ExtractComplexNames(Transformer):
    """
    Extracts definitions of cmplx_name from #! complexes part.

    Also multiplies rule with variable to its instances using ReplaceVariables Transformer.
    """
    def __init__(self):
        super(Transformer, self).__init__()
        self.complex_defns = dict()

    def cmplx_dfn(self, matches):
        self.complex_defns[str(matches[0].children[0])] = matches[1]

    def rules(self, matches):
        new_rules = [matches[0]]
        for rule in matches[1:]:
            if rule.children[-1].data == 'variable':
                variables = rule.children[-1].children[1:]
                for variable in variables:
                    replacer = ReplaceVariables(variable)
                    new_rule = Tree('rule', deepcopy(rule.children[:-1]))
                    new_rules.append(replacer.transform(new_rule))
            else:
                new_rules.append(rule)
        return Tree('rules', new_rules)


class TransformAbstractSyntax(Transformer):
    """
    Transformer to remove "zooming" syntax.

    Divided to three special cases (declared below).
    Based on replacing subtrees in parent trees.
    """
    def __init__(self, complex_defns):
        super(Transformer, self).__init__()
        self.complex_defns = complex_defns

    def cmplx_name(self, matches):
        return deepcopy(self.complex_defns[str(matches[0])])

    def abstract_sequence(self, matches):
        return matches[0]

    def atomic_structure_complex(self, matches):
        """
        atomic:structure:complex
        """
        structure = self.insert_atomic_to_struct(matches[0], matches[1])
        sequence = self.insert_struct_to_complex(structure, matches[2])
        return sequence

    def atomic_complex(self, matches):
        """
        atomic:complex
        """
        sequence = self.insert_atomic_to_complex(matches[0], matches[1])
        return sequence

    def structure_complex(self, matches):
        """
        structure:complex
        """
        sequence = self.insert_struct_to_complex(matches[0], matches[1])
        return sequence

    def insert_atomic_to_struct(self, atomic, struct):
        """
        Adds or replaces atomic subtree in struct tree.
        """
        if len(struct.children) == 2:
            struct.children[1].children.append(atomic)
        else:
            struct.children.append(Tree('composition', [atomic]))
        return struct

    def insert_struct_to_complex(self, struct, complex):
        """
        Adds or replaces struct subtree in complex tree.
        """
        for i in range(len(complex.children)):
            if self.get_name(struct) == self.get_name(complex.children[i].children[0]):
                complex.children[i] = Tree('agent', [struct])
                break
        return complex

    def insert_atomic_to_complex(self, atomic, complex):
        """
        Adds or replaces atomic subtree in complex tree.
        """
        for i in range(len(complex.children)):
            if self.get_name(atomic) == self.get_name(complex.children[i].children[0]):
                complex.children[i] = Tree('agent', [atomic])
                break
        return complex

    def get_name(self, agent):
        return str(agent.children[0].children[0])


class TreeToComplex(Transformer):
    """
    Creates actual Complexes in rates of the rules - there it is safe,
    order is not important. Does not apply to the rest of the rule!
    """
    def state(self, matches):
        return "".join(map(str, matches))

    def atomic(self, matches):
        name, state = str(matches[0].children[0]), matches[1]
        return AtomicAgent(name, state)

    def structure(self, matches):
        name = str(matches[0].children[0])
        if len(matches) > 1:
            composition = set(matches[1].children)
            return StructureAgent(name, composition)
        else:
            return StructureAgent(name, set())

    def rate_complex(self, matches):
        sequence = []
        for item in matches[0].children:
            sequence.append(item.children[0])
        compartment = matches[2]
        return Tree("agent", [Complex(sequence, compartment)])

    def compartment(self, matches):
        return str(matches[0])


class TreeToObjects(Transformer):
    def __init__(self):
        super(Transformer, self).__init__()
        self.params = set()
    """
    A transformer which is called on a tree in a bottom-up manner and transforms all subtrees/tokens it encounters.
    Note the defined methods have the same name as elements in the grammar above.

    Creates the actual Model object after all the above transformers were applied.
    """
    def const(self, matches):
        return float(matches[0])

    def def_param(self, matches):
        return str(matches[0])

    def number(self, matches):
        return float(matches[0])

    def side(self, matches):
        helper = SideHelper()
        stochio = 1
        for item in matches:
            if type(item) in [int, float]:
                stochio = int(item)
            else:
                agents = item.children[0]
                compartment = item.children[2]
                for i in range(stochio):
                    start = helper.counter
                    for agent in agents.children:
                        helper.seq.append(deepcopy(agent.children[0]))
                        helper.comp.append(compartment)
                        helper.counter += 1
                    helper.complexes.append((start, helper.counter - 1))
        return helper

    def rule(self, matches):
        if len(matches) > 3:
            lhs, arrow, rhs, rate = matches
        else:
            lhs, arrow, rhs = matches
            rate = None
        agents = tuple(lhs.seq + rhs.seq)
        mid = lhs.counter
        compartments = lhs.comp + rhs.comp
        complexes = lhs.complexes + list(
            map(lambda item: (item[0] + lhs.counter, item[1] + lhs.counter), rhs.complexes))
        pairs = [(i, i + lhs.counter) for i in range(min(lhs.counter, rhs.counter))]
        if lhs.counter > rhs.counter:
            pairs += [(i, None) for i in range(rhs.counter, lhs.counter)]
        elif lhs.counter < rhs.counter:
            pairs += [(None, i + lhs.counter) for i in range(lhs.counter, rhs.counter)]

        return Rule(agents, mid, compartments, complexes, pairs, Rate(rate) if rate else None)

    def rules(self, matches):
        return matches[1:]

    def definitions(self, matches):
        result = dict()
        for definition in matches[1:]:
            pair = definition.children
            result[pair[0]] = pair[1]
        return result

    def init(self, matches):
        return matches

    def inits(self, matches):
        result = collections.Counter()
        for init in matches[1:]:
            if len(init) > 1:
                result[init[1].children[0]] = int(init[0])
            else:
                result[init[0].children[0]] = 1
        return result

    def param(self, matches):
        self.params.add(str(matches[0]))
        return Tree("param", matches)

    def model(self, matches):
        params = self.params - set(matches[2].keys())
        return Core.Model.Model(set(matches[0]), matches[1], matches[2], params)


class Parser:
    def __init__(self, start):
        grammar = "start: " + start + GRAMMAR + COMPLEX_GRAMMAR + EXTENDED_GRAMMAR
        self.parser = Lark(grammar, parser='lalr',
                           propagate_positions=False,
                           maybe_placeholders=False
                           )

        self.terminals = dict((v, k) for k, v in _TERMINAL_NAMES.items())
        self.terminals.update({"COM": "//",
                               "ARROW": "=>",
                               "POW": "**",
                               "DOUBLE_COLON": "::",
                               "RULES_START": "#! rules",
                               "INITS_START": "#! inits",
                               "DEFNS_START": "#! definitions",
                               "CNAME": "name",
                               "NAME": "agent_name",
                               "VAR": "?"
                               })
        self.terminals.pop("$END", None)

    def replace(self, expected: set) -> set:
        """
        Method used to replace expected tokens by their human-readable representations defined in self.terminals

        :param expected: given set of expected tokens
        :return: transformed tokens
        """
        return set([self.terminals.get(item, item.lower()) for item in expected])

    def parse(self, expression: str) -> Result:
        """
        Main method for parsing, first syntax_check is called which checks syntax and if it is
        correct, a parsed Tree is returned.

        Then the tree is transformed using several Transformers in self.transform method.

        :param expression: given string expression
        :return: Result containing parsed object or error specification
        """
        result = self.syntax_check(expression)
        if result.success:
            return self.transform(result.data)
        else:
            return result

    def transform(self, tree: Tree) -> Result:
        """
        Apply several transformers to construct BCSL object from given tree.

        :param tree: given parsed Tree
        :return: Result containing constructed BCSL object
        """
        try:
            complexer = ExtractComplexNames()
            tree = complexer.transform(tree)
            de_abstracter = TransformAbstractSyntax(complexer.complex_defns)
            tree = de_abstracter.transform(tree)
            tree = TreeToComplex().transform(tree)
            tree = TreeToObjects().transform(tree)

            return Result(True, tree.children[0])
        except Exception as u:
            return Result(False, {"error": str(u)})

    def syntax_check(self, expression: str) -> Result:
        """
        Main method for parsing, calls Lark.parse method and creates Result containing parsed
         object (according to designed 'start' in grammar) or dict with specified error in case
         the given expression cannot be parsed.

        :param expression: given string expression
        :return: Result containing parsed object or error specification
        """
        try:
            tree = self.parser.parse(expression)
        except UnexpectedCharacters as u:
            return Result(False, {"unexpected": expression[u.pos_in_stream],
                                  "expected": self.replace(u.allowed),
                                  "line": u.line, "column": u.column})
        except UnexpectedToken as u:
            return Result(False, {"unexpected": str(u.token),
                                  "expected": self.replace(u.expected),
                                  "line": u.line, "column": u.column})
        return Result(True, tree)