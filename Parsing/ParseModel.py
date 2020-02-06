import collections
from copy import deepcopy
from lark import Lark, Transformer, v_args

from Objects.Atomic import AtomicAgent
from Objects.Complex import Complex
from Objects.Rule import Rule
from Objects.Structure import StructureAgent

class SideHelper:
    def __init__(self):
        self.seq = []
        self.comp = []
        self.complexes = []
        self.counter = 0

    def __str__(self):
        return " | ".join([str(self.seq), str(self.comp), str(self.complexes), str(self.counter)])

    def __repr__(self):
        return str(self)

grammar = r"""
    start: rule

    rule: side "=>" side "@" rate
    side: (const? complex "+")* (const? complex)?
    complex: sequence "::" compartment
    sequence: (agent ".")* agent?
    agent: atomic | structure
    structure: s_name "()" | s_name "(" composition ")"
    composition: (atomic ",")* atomic?
    atomic : a_name "{" state "}" | a_name

    !rate : fun "/" fun | fun
    !fun: const | param | "[" rate_complex "]" | fun "+" fun | fun "*" fun | fun "^" const

    rate_complex: sequence "::" compartment

    state: CNAME | "_"
    a_name: CNAME
    s_name: CNAME
    compartment: CNAME
    param: CNAME

    const: DIGIT

    %import common.LETTER
    %import common.DIGIT
    %import common.CNAME
    %import common.WS
    %ignore WS
"""


class TreeToObjects(Transformer):
    def atomic(self, matches):
        name, state = str(matches[0].children[0]), matches[1]
        if state.children:
            return AtomicAgent(name, str(state.children[0]))
        else:
            return AtomicAgent(name, "_")

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
        compartment = matches[1]
        return Complex(collections.Counter(sequence), compartment)

    def compartment(self, matches):
        return str(matches[0])

    def const(self, matches):
        return int(matches[0])

    def side(self, matches):
        helper = SideHelper()
        stochio = 1
        for item in matches:
            if type(item) == int:
                stochio = item
            else:
                agents = item.children[0]
                compartment = item.children[1]
                for i in range(stochio):
                    start = helper.counter
                    for agent in agents.children:
                        helper.seq.append(agent.children[0])
                        helper.comp.append(compartment)
                        helper.counter += 1
                    helper.complexes.append((start, helper.counter - 1))
        return helper

    def rule(self, matches):
        lhs, rhs, rate = matches
        agents = tuple(lhs.seq + rhs.seq)
        mid = lhs.counter
        compartments = lhs.comp + rhs.comp
        complexes = lhs.complexes + list(map(lambda item: (item[0] + lhs.counter, item[1] + lhs.counter), rhs.complexes))
        pairs = [(i, i +lhs.counter) for i in range(lhs.counter - 1)]
        return Rule(agents, mid, compartments, complexes, pairs, rate)

parser = Lark(grammar, parser='lalr',
              lexer='standard',
              propagate_positions=False,
              maybe_placeholders=False,
              transformer=TreeToObjects()
              )


def test():
    test_atomic = '''
        1 K(S{u3_m}, T{a_p}, S{p})::cyt + B()::cyt => 1 B().K(S{p}).H()::cyt + 2 A{_}::cyt @ 3*[K()::cyt]/2*v_1
    '''

    j = parser.parse(test_atomic)
    print(j.children[0])


if __name__ == '__main__':
    test()
    # with open(sys.argv[1]) as f:
    # print(parse(f.read()))
