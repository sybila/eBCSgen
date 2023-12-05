from eBCSgen.Parsing.ParseBCSL import Parser
import Testing.parsing.objects_testing as objects
from eBCSgen.Core.Complex import Complex

parser = Parser("rate")


def test_parser():
    ret = parser.parse("1")
    assert ret.success

    ret = parser.parse("0.5")
    assert ret.success

    ret = parser.parse("2*3")
    assert ret.success

    ret = parser.parse("2**3")
    assert ret.success

    ret = parser.parse("2*[K()::cyt]")
    assert ret.success

    ret = parser.parse("[K()::cyt]**2")
    assert ret.success

    ret = parser.parse(
        "(2 * [K()::cyt] + 3 * [B(T{s})::cell]) / (4 * [T{u}.T{_}::cell] - 2 * [B(T{s})::cyt])"
    )
    assert ret.success

    # why is this expression incorrect, it passes separated into expr1 snd expr2
    # ret = parser.parse(
    #     "((([B(T{s})::cell] + [B(T{s})::cyt]) / ([B(T{_}.C())::cell] + [B()::cell])) / (([B(T{s}).T{s}::cyt] - [T{_}::cell]) / ([T{u}.T{_}::cell] - [B(T{s})::cell])))"
    # )
    expr1 = "([B(T{s})::cell] + [B(T{s})::cyt]) / ([B(T{_}).C()::cell] + [B()::cell])"
    expr2 = (
        "([B(T{s}).T{s}::cyt] - [T{_}::cell]) / ([T{u}.T{_}::cell] - [B(T{s})::cell])"
    )
    ret = parser.parse(expr1)
    assert ret.success
    ret = parser.parse(expr2)
    assert ret.success
    # ret = parser.parse(f"({expr1}/{expr2})")
    # assert ret.success

    ret = parser.parse("0,5")
    assert not ret.success

    # missing []
    ret = parser.parse("2*K()::cyt")
    assert not ret.success

    # invalid syntax
    ret = parser.parse("2 +")
    assert not ret.success

    # unsupported operators
    ret = parser.parse("2 & 3")
    assert not ret.success

    # mismatched parentheses
    ret = parser.parse("(2 * 3")
    assert not ret.success

    # incorrect format
    ret = parser.parse("2,,3")
    assert not ret.success

    # nested complexes
    ret = parser.parse("[K([L()::cell])::cyt]")
    assert not ret.success
