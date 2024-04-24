import pytest

import Testing.objects_testing as objects
from eBCSgen.Core.Rate import Rate


def test_parser():
    rule_expr = "K(S{u}).B()::cyt => K(S{p})::cyt + B()::cyt + D(B{_})::cell @ 3*[K()::cyt]/2*v_1"
    assert objects.rule_parser.parse(rule_expr).data[1] == objects.r5

    rule_expr = "K(B{-}).B()::cyt + D(B{_})::cell => K(B{+})::cyt + B()::cyt @ 3*[K(T{3+})::cyt]/2*v_1"
    assert objects.rule_parser.parse(rule_expr).data[1] == objects.r6

    rule_expr = "X()::rep => @ k1*[X()::rep]"
    assert objects.rule_parser.parse(rule_expr).data[1] == objects.r1

    rule_expr = "=> Y()::rep @ 1/(1+([X()::rep])**4)"
    assert objects.rule_parser.parse(rule_expr).data[1] == objects.r3

    rule_expr = "K(S{u}).B()::cyt => K(S{p})::cyt + B()::cyt"
    assert objects.rule_parser.parse(rule_expr).data[1] == objects.rule_no_rate


def test_bidirectional():
    rule_expr = "#! rules\nK(S{u}).B()::cyt <=> K(S{p})::cyt + B()::cyt"
    parsed = objects.rules_parser.parse(rule_expr)
    assert parsed.success
    assert objects.rule_no_rate in parsed.data["rules"]
    assert objects.reversed_no_rate in parsed.data["rules"]

    rule_expr = "#! rules\nK(S{u}).B()::cyt <=> K(S{p})::cyt + B()::cyt @ 3*[K()::cyt]/2*v_1 | 3*[K()::cyt]/2*v_1"
    parsed = objects.rules_parser.parse(rule_expr)
    assert parsed.success
    assert objects.r4 in parsed.data["rules"]
    assert objects.reversed_r4a in parsed.data["rules"]

    rule_expr = "#! rules\nK(S{u}).B()::cyt <=> K(S{p})::cyt + B()::cyt @ 3*[K()::cyt]/2*v_1 | 2*[K()::cyt]/3*v_1"
    parsed = objects.rules_parser.parse(rule_expr)
    assert parsed.success
    assert objects.r4 in parsed.data["rules"]
    assert objects.reversed_r4b in parsed.data["rules"]

    rule_expr = "#! rules\n <=> K(S{p})::cyt + B()::cyt @ 3*[K()::cyt]/2*v_1 | 3*[K()::cyt]/2*v_1"
    parsed = objects.rules_parser.parse(rule_expr)
    assert parsed.success
    assert objects.one_side_bidirectional_a in parsed.data["rules"]
    assert objects.one_side_bidirectional_b in parsed.data["rules"]

    rule_expr = "#! rules\n K(S{p})::cyt + B()::cyt <=> @ 3*[K()::cyt]/2*v_1 | 3*[K()::cyt]/2*v_1"
    parsed = objects.rules_parser.parse(rule_expr)
    assert parsed.success
    assert objects.one_side_bidirectional_a in parsed.data["rules"]
    assert objects.one_side_bidirectional_b in parsed.data["rules"]

    rule_expr = "#! rules\n K(S{p})::cyt + B()::cyt <=> @ 3*[K()::cyt]/2*v_1 | 2*[K()::cyt]/3*v_1"
    parsed = objects.rules_parser.parse(rule_expr)
    assert parsed.success
    assert objects.one_side_bidirectional_a in parsed.data["rules"]
    assert objects.one_side_bidirectional_b_reversed_rate in parsed.data["rules"]

    rule_expr = "#! rules\n K(S{p})::cyt + B()::cyt <=>"
    parsed = objects.rules_parser.parse(rule_expr)
    assert parsed.success
    assert objects.one_side_bidirectional_a_no_rate in parsed.data["rules"]
    assert objects.one_side_bidirectional_b_no_rate in parsed.data["rules"]

    rule_expr = (
        "#! rules\nK(S{u}).B()::cyt <=> K(S{p})::cyt + B()::cyt @ 3*[K()::cyt]/2*v_1"
    )
    assert not objects.rules_parser.parse(rule_expr).success

    rule_expr = "#! rules\nK(S{u}).B()::cyt => K(S{p})::cyt + B()::cyt @ 3*[K()::cyt]/2*v_1 | 2*[K()::cyt]/3*v_1"
    assert not objects.rules_parser.parse(rule_expr).success


def test_replication():
    rule_expr = "X()::rep =*> X()::rep + X()::rep"
    result = objects.rule_parser.parse(rule_expr)
    assert result.success
    assert result.data[1] == objects.rule_repl1

    rule_expr = "X()::rep =*> X()::rep + X()::rep @ 3*[X()::rep]/2*v_1"
    result = objects.rule_parser.parse(rule_expr)
    assert result.success
    rate_repl1 = Rate("3.0*[X()::rep]/2*v_1")
    assert result.data[1] == objects.rule_repl1_rate

    rule_expr = "X()::rep =*> X()::rep + X()::rep + X()::rep"
    result = objects.rule_parser.parse(rule_expr)
    assert result.success
    assert result.data[1] == objects.rule_repl2

    rule_expr = "X()::rep + Y()::rep =*> X()::rep + X()::rep"
    assert not objects.rule_parser.parse(rule_expr).success

    rule_expr = "X()::rep =*> X()::rep + X()::rep + Y()::rep"
    assert not objects.rule_parser.parse(rule_expr).success
