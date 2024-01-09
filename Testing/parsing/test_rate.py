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
