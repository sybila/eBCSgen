from lark import Lark, Transformer, v_args

from Objects.Atomic import AtomicAgent
from Objects.Structure import StructureAgent

json_grammar = r"""
    start: rule

    rule: side "=>" side "@" rate
    side: (const? complex "+")* (const? complex)?
    complex: sequence "::" compartment
    sequence: (agent ".")* agent?
    agent: atomic | structure
    structure: s_name "()" | s_name "(" composition ")"
    composition: (atomic ",")* atomic?
    atomic : a_name "{" state "}" | a_name

    rate : fun "/" fun | fun
    fun: const | param | "[" complex "]" | fun "+" fun | fun "*" fun | fun "^" const

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

    # def sequence(self, matches):
    #     print("**********", matches)
    # #     return to_list_2(matches)


json_parser = Lark(json_grammar, parser='lalr',
                   lexer='standard',
                   propagate_positions=False,
                   maybe_placeholders=False,
                   transformer=TreeToObjects()
                   )
parse = json_parser.parse


def test():
    test_atomic = '''
        1 K(S{u3_m}, T{a_p}, S{p})::cyt + 1 B()::cyt => 1 B().K(S{p}).H()::cyt + 2 A{_}::cyt @ 3*[K()::cyt]/2*v_1
    '''

    j = parse(test_atomic)
    print(j.pretty())


if __name__ == '__main__':
    test()
    # with open(sys.argv[1]) as f:
    # print(parse(f.read()))
