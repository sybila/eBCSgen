import Testing.objects_testing as objects


def test_parser():
    ret = objects.rate_complex_parser.parse("B(T{s})::cell")
    assert ret.success
    assert ret.data.children[0] == objects.c1

    ret = objects.rate_complex_parser.parse("B(T{s}).D().K(T{s},S{s},U{a})::cell")
    assert ret.success
    assert ret.data.children[0] == objects.c2

    ret = objects.rate_complex_parser.parse(
        "B(T{s}).K(T{s}, S{s}, U{a}).D(S{_},T{p})::cyt"
    )
    assert ret.success
    assert ret.data.children[0] == objects.c3

    ret = objects.rate_complex_parser.parse("B(T{s}).T{s}::cyt")
    assert ret.success
    assert ret.data.children[0] == objects.c4

    ret = objects.rate_complex_parser.parse("D().D().D().B(T{_}).B(T{_}).B(T{_})::cell")
    assert ret.success
    assert ret.data.children[0] == objects.c5

    ret = objects.rate_complex_parser.parse("K().K().T{p}::cyt")
    assert ret.success
    assert ret.data.children[0] == objects.c6

    ret = objects.rate_complex_parser.parse("T{u}.T{_}::cell")
    assert ret.success
    assert ret.data.children[0] == objects.c7

    ret = objects.rate_complex_parser.parse("(T{s})::cell")
    assert not ret.success

    ret = objects.rate_complex_parser.parse("()::cell")
    assert not ret.success

    ret = objects.rate_complex_parser.parse("x::cell")
    assert not ret.success

    ret = objects.rate_complex_parser.parse("BT{s})::cell")
    assert not ret.success

    ret = objects.rate_complex_parser.parse("B(T{s}::cell")
    assert not ret.success

    ret = objects.rate_complex_parser.parse("B(T{s}::cell)")
    assert not ret.success

    ret = objects.rate_complex_parser.parse("B(T{})::cell")
    assert not ret.success

    ret = objects.rate_complex_parser.parse("B(T{s}))::cell")
    assert not ret.success

    ret = objects.rate_complex_parser.parse("B(T{s})::")
    assert not ret.success
