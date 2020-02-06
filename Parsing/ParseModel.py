from lark import Lark, Transformer, v_args

from Objects.Atomic import AtomicAgent

json_grammar = r"""
    start: rule

    rule: side "=>" side "@" rate
    side: side "+" const complex | const complex | "_"
    complex: sequence "::" compartment
    sequence: agent | agent "." sequence
    agent: atomic | structure
    structure: s_name "()" | s_name "(" composition ")"
    composition: atomic | atomic "," composition
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
    def atomic(self, items):
        a_name, state = items[0], items[1]
        print(a_name, state)
        if state.children:
            return AtomicAgent(str(a_name.children[0]), str(state.children[0]))
        else:
            return AtomicAgent(str(a_name.children[0]), "_")

json_parser = Lark(json_grammar, parser='lalr',
                   lexer='standard',
                   propagate_positions=False,
                   maybe_placeholders=False,
                   transformer=TreeToObjects()
                   )
parse = json_parser.parse


def test():
    test_atomic = '''
        1 K(S{u3_m}, T{a_p})::cyt + 1 B()::cyt => 1 B().K(S{p})::cyt + 2 A{_}::cyt @ 3*[K()::cyt]/2*v_1
    '''

    j = parse(test_atomic)
    print(j.pretty())


if __name__ == '__main__':
    test()
    # with open(sys.argv[1]) as f:
    # print(parse(f.read()))
