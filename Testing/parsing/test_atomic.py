import Testing.objects_testing as objects


def test_parser():
    assert objects.atomic_parser.parse("T{s}").data == objects.a1
    assert objects.atomic_parser.parse("S{a}").data == objects.a2
    assert objects.atomic_parser.parse("S{s}").data == objects.a3
    assert objects.atomic_parser.parse("T{_}").data == objects.a4
    assert objects.atomic_parser.parse("S{_}").data == objects.a5
    assert objects.atomic_parser.parse("T{p}").data == objects.a6
    assert objects.atomic_parser.parse("T{u}").data == objects.a7

    assert not objects.atomic_parser.parse("T{s").success
    assert not objects.atomic_parser.parse("T{}").success
    assert not objects.atomic_parser.parse("Ts}").success
    assert not objects.atomic_parser.parse("{s}").success
    assert not objects.atomic_parser.parse("x").success
    assert not objects.atomic_parser.parse("").success
