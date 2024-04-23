import pytest

import Testing.objects_testing as objects


def test_parser():
    observable_expr1 = "abc: A()::cell"
    assert objects.observable_parser.parse(observable_expr1)

    observable_expr2 = "efg: E(F{_})"
    assert objects.observable_parser.parse(observable_expr2)

    observable_expr3 = "hij: $H()::cell"
    assert objects.observable_parser.parse(observable_expr3)

    observable_expr4 = "klm: {matchOnce}K()"
    assert objects.observable_parser.parse(observable_expr4)

    observable_expr5 = "nop: N()::cell > 2"
    assert objects.observable_parser.parse(observable_expr5).success

    observable_expr6 = "qrs: Q().R().S()::cell > 2"
    assert objects.observable_parser.parse(observable_expr6).success

    observable_expr7 = "tuv: T(U{v})"
    assert objects.observable_parser.parse(observable_expr7).success

    observable_expr8 = "wx: 2 W{x}"
    assert objects.observable_parser.parse(observable_expr8).success

    observable_expr9 = "z: Y{z} + Z{y}"
    assert objects.observable_parser.parse(observable_expr9).success

    observable_expr10 = "z: 2 * Y{z} + Z{y}"
    assert objects.observable_parser.parse(observable_expr10).success

    observable_expr10 = "z: (Y{z} + Z{y}) / 2.1 ** 10"
    assert objects.observable_parser.parse(observable_expr10).success

    observable_expr11 = "scaled_A: 1000 * A{i}::cell"
    assert objects.observable_parser.parse(observable_expr11).success

    observable_expr12 = "obs_A_all: A{i}::cell + A{a}::cell"
    assert objects.observable_parser.parse(observable_expr12).success

    observables_expr = (
        "#! observables\n"
        + observable_expr1
        + "\n"
        + observable_expr2
        + "\n"
        + observable_expr3
        + "\n"
        + observable_expr4
        + "\n"
        + observable_expr5
        + "\n"
        + observable_expr6
    )
    assert objects.observables_parser.parse(observables_expr).success

    assert not objects.observable_parser.parse("A()::cell > 2").success
    assert not objects.observable_parser.parse("a: A(::cell").success
    assert not objects.observable_parser.parse("a: b: A():cell > 2").success
    assert not objects.observable_parser.parse("a: 2 > A():cell").success
    assert not objects.observable_parser.parse("a: A()::cell$").success
    assert not objects.observable_parser.parse("a: A{}::cell").success
