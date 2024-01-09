import Testing.objects_testing as objects


def test_parser():
    assert objects.structure_parser.parse("B(T{s})").data == objects.s1
    assert objects.structure_parser.parse("D()").data == objects.s2
    assert objects.structure_parser.parse("K(T{s}, S{s}, S{_})").data == objects.s3
    assert objects.structure_parser.parse("B(T{_})").data == objects.s4
    assert objects.structure_parser.parse("D(S{_},T{p})").data == objects.s5
    assert objects.structure_parser.parse("K()").data == objects.s6
    assert objects.structure_parser.parse("K(S{a},T{_})").data == objects.s7

    assert not objects.structure_parser.parse("B(T{})").success
    assert not objects.structure_parser.parse("(T{s})").success
    assert not objects.structure_parser.parse("BT{s})").success
    assert not objects.structure_parser.parse("B(T{s}").success
    assert not objects.structure_parser.parse("(B(T{s}))").success
    assert not objects.structure_parser.parse("[B(T{s})]").success
    assert not objects.structure_parser.parse("").success
    assert not objects.structure_parser.parse("B({s})").success
