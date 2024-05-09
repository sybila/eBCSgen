import Testing.objects_testing as objects


def test_parser():
    ret = objects.rate_parser.parse("1")
    assert ret.success

    ret = objects.rate_parser.parse("0.5")
    assert ret.success

    ret = objects.rate_parser.parse("2*3")
    assert ret.success

    ret = objects.rate_parser.parse("2**3")
    assert ret.success

    ret = objects.rate_parser.parse("2*[K()::cyt]")
    assert ret.success

    ret = objects.rate_parser.parse("[K()::cyt]**2")
    assert ret.success

    ret = objects.rate_parser.parse(
        "(2 * [K()::cyt] + 3 * [B(T{s})::cell]) / (4 * [T{u}.T{_}::cell] - 2 * [B(T{s})::cyt])"
    )
    assert ret.success

    expr1 = "([B(T{s})::cell] + [B(T{s})::cyt]) / ([B(T{_}).C()::cell] + [B()::cell])"
    expr2 = (
        "([B(T{s}).T{s}::cyt] - [T{_}::cell]) / ([T{u}.T{_}::cell] - [B(T{s})::cell])"
    )
    ret = objects.rate_parser.parse(expr1)
    assert ret.success
    ret = objects.rate_parser.parse(expr2)
    assert ret.success

    # currently does not pass
    ret = objects.rate_parser.parse(f"({expr1}/{expr2})")
    assert ret.success

    ret = objects.rate_parser.parse("0,5")
    assert not ret.success

    # missing []
    ret = objects.rate_parser.parse("2*K()::cyt")
    assert not ret.success

    # invalid syntax
    ret = objects.rate_parser.parse("2 +")
    assert not ret.success

    # unsupported operators
    ret = objects.rate_parser.parse("2 & 3")
    assert not ret.success

    # mismatched parentheses
    ret = objects.rate_parser.parse("(2 * 3")
    assert not ret.success

    # incorrect format
    ret = objects.rate_parser.parse("2,,3")
    assert not ret.success

    # nested complexes
    ret = objects.rate_parser.parse("[K([L()::cell])::cyt]")
    assert not ret.success

    # nested parenthesis
    assert objects.rate_parser.parse("(2 * (3 + 4)) / (5 - (6 * 7))").success
    assert objects.rate_parser.parse("((2 + 3) * (4 - 5)) / ((6 * 7) + 8)").success

    # complex mathematical operations
    assert objects.rate_parser.parse("2 * [A()::cyt] + 3 / [B(T{s})::cell]").success
    assert objects.rate_parser.parse("[X()::cyt] ** 2 - (4 * [Y()::cell])").success

    # multiple level nesting
    assert objects.rate_parser.parse("((2 * [A()::cyt]) + (3 / [B(T{s})::cell])) / ((4 * [C()::cell]) - (2 * [D()::cyt]))").success
    assert objects.rate_parser.parse("([X()::cyt] ** 2) / ([Y()::cell] + ([Z()::cyt] * 3))").success
    assert objects.rate_parser.parse("1/([X()::cyt] ** 2) + ([Y()::cell] + ([Z()::cyt] * 3))/(5 + [KaiC()::cyt])").success
    
    # complex rate_agents
    assert objects.rate_parser.parse("[A().B()::cyt] + [C().D()::nuc]").success
    assert objects.rate_parser.parse("[X(Y{a}).Z(W{b})::cell]").success
    assert objects.rate_parser.parse("2 * [A()::cyt] + [B(T{s})::cell] ** 3").success
    assert objects.rate_parser.parse("[X()::cyt] / ([Y{a}::cell] + [Z{b}::cyt])").success

    # invalid syntax
    assert not objects.rate_parser.parse("2 * [A()::cyt] + 3 / [B(T{s})::cell] +").success # extra +
    assert not objects.rate_parser.parse("[A().B()::cyt] + C().D()::nuc]").success # missing [
    assert not objects.rate_parser.parse("[X(Y{a}).Z(W{b})::cell").success # missing ]
    assert not objects.rate_parser.parse("2 * [A()::cyt] + [B(T{s})::cell * 3").success # missing ]
    assert not objects.rate_parser.parse("[X()::cyt] ** 2 - (4 * [Y()::cell]))").success # extra )
    assert not objects.rate_parser.parse("2 & [A()::cyt] + 3 | [B(T{s})::cell]").success # invalid operators
    assert not objects.rate_parser.parse("2 ** [X()::cyt]").success # invalid operation - exponentiation
    assert not objects.rate_parser.parse("2 * K()::cyt").success # missing required brackets for rate agent
    assert not objects.rate_parser.parse("[X()::cyt] ** 2 - 4 * Y()::cell").success # missing required brackets for rate agent
    assert not objects.rate_parser.parse("[X()::cyt] / {Y} + [Z()::cell]").success
    assert not objects.rate_parser.parse("[K([L()::cell])::cyt] + [A(B(C{d})).D(E{e}::cyt)]").success # nested rate agents and incorrect syntax
