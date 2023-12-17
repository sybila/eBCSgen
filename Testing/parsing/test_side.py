from eBCSgen.Parsing.ParseBCSL import Parser
import Testing.parsing.objects_testing as objects

parser = Parser("side")


def test_parser():
    ret = parser.parse("B(T{s})::cell")
    assert ret.success
    assert ret.data.to_side() == objects.side1

    ret = parser.parse("B(T{s}).T{s}::cyt + D().D().D().B(T{_}).B(T{_}).B(T{_})::cell")
    assert ret.success
    assert ret.data.to_side() == objects.side2

    ret = parser.parse(
        "B(T{s})::cell + B(T{s}).D().K(T{s},S{s},S{_})::cell + B(T{s}).D().K(T{s},S{s},S{_})::cell"
    )
    assert ret.success
    assert ret.data.to_side() == objects.side3

    ret = parser.parse("B(T{s})::cell + 2 B(T{s}).D().K(T{s},S{s},S{_})::cell")
    assert ret.success
    assert ret.data.to_side() == objects.side3

    ret = parser.parse(
        "T{u}.T{_}::cell + K().K().T{p}::cyt + D().D().D().B(T{_}).B(T{_}).B(T{_})::cell"
    )
    assert ret.success
    assert ret.data.to_side() == objects.side4

    ret = parser.parse("")
    assert ret.success
    assert ret.data.to_side() == objects.side5

    ret = parser.parse("(T{s})::cell")
    assert not ret.success

    ret = parser.parse("BT{s})::cell")
    assert not ret.success

    ret = parser.parse("B(T{s}::cell")
    assert not ret.success

    ret = parser.parse("B(T{s})::")
    assert not ret.success

    ret = parser.parse("B(T{s}")
    assert not ret.success
