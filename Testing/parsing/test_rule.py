import pytest

from eBCSgen.Core.Rule import Rule
from eBCSgen.Core.Rate import Rate

import Testing.objects_testing as objects

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
