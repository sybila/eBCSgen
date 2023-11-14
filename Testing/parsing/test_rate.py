from eBCSgen.Parsing.ParseBCSL import Parser
import Testing.parsing.objects_testing as objects

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

    ret = parser.parse(
        "(([B(T{s})::cell] + [B(T{s})::cyt]) / ([B(T{_}.C())::cell] + [B()::cell])) / (([B(T{s}).T{s}::cyt] - [T{_}::cell]) / ([T{u}.T{_}::cell] - [B(T{s})::cell]))"
    )
    assert ret.success

    ret = parser.parse("0,5")
    assert not ret.success

    ret = parser.parse("2*K()::cyt")
    assert not ret.success

    # is division by zero rational expression?
    ret = parser.parse("1/0")
    assert not ret.success
