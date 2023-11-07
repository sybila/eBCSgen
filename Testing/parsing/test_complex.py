import Testing.parsing.objects_testing as objects
from eBCSgen.Parsing.ParseBCSL import Parser


parser = Parser("rate_complex")


def test_parser():
    ret = parser.parse("B(T{s})::cell")
    assert ret.success
    assert ret.data.children[0] == objects.c1

    ret = parser.parse("B(T{s}).D().K(T{s},S{s},S{_})::cell")
    assert ret.success
    assert ret.data.children[0] == objects.c2

    ret = parser.parse("B(T{s}).K(T{s}, S{s}, S{_}).D(S{_},T{p})::cyt")
    assert ret.success
    assert ret.data.children[0] == objects.c3

    ret = parser.parse("B(T{s}).T{s}::cyt")
    assert ret.success
    assert ret.data.children[0] == objects.c4

    ret = parser.parse("D().D().D().B(T{_}).B(T{_}).B(T{_})::cell")
    assert ret.success
    assert ret.data.children[0] == objects.c5

    ret = parser.parse("K().K().T{p}::cyt")
    assert ret.success
    assert ret.data.children[0] == objects.c6

    ret = parser.parse("T{u}.T{_}::cell")
    assert ret.success
    assert ret.data.children[0] == objects.c7
