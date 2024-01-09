import Testing.objects_testing as objects


def test_parser():
    ret = objects.side_parser.parse("B(T{s})::cell")
    assert ret.success
    assert ret.data.to_side() == objects.side1

    ret = objects.side_parser.parse(
        "B(T{s}).T{s}::cyt + D().D().D().B(T{_}).B(T{_}).B(T{_})::cell"
    )
    assert ret.success
    assert ret.data.to_side() == objects.side2

    ret = objects.side_parser.parse(
        "B(T{s})::cell + B(T{s}).D().K(T{s},S{s},S{_})::cell + B(T{s}).D().K(T{s},S{s},S{_})::cell"
    )
    assert ret.success
    assert ret.data.to_side() == objects.side3

    ret = objects.side_parser.parse(
        "B(T{s})::cell + 2 B(T{s}).D().K(T{s},S{s},S{_})::cell"
    )
    assert ret.success
    assert ret.data.to_side() == objects.side3

    ret = objects.side_parser.parse(
        "T{u}.T{_}::cell + K().K().T{p}::cyt + D().D().D().B(T{_}).B(T{_}).B(T{_})::cell"
    )
    assert ret.success
    assert ret.data.to_side() == objects.side4

    ret = objects.side_parser.parse("")
    assert ret.success
    assert ret.data.to_side() == objects.side5

    ret = objects.side_parser.parse("(T{s})::cell")
    assert not ret.success

    ret = objects.side_parser.parse("BT{s})::cell")
    assert not ret.success

    ret = objects.side_parser.parse("B(T{s}::cell")
    assert not ret.success

    ret = objects.side_parser.parse("B(T{s})::")
    assert not ret.success

    ret = objects.side_parser.parse("B(T{s}")
    assert not ret.success
