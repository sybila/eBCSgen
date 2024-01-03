import pytest

from eBCSgen.Core.Rule import Rule
from eBCSgen.Core.Rate import Rate

import Testing.objects_testing as objects

#  rules

sequence_1 = (objects.s34, objects.s35, objects.s36, objects.s37)
mid_1 = 2
compartments_1 = ["cyt"] * 4
complexes_1 = [(0, 1), (2, 2), (3, 3)]
pairs_1 = [(0, 2), (1, 3)]
rate_1 = Rate("3.0*[K()::cyt]/2.0*v_1")

r1 = Rule(sequence_1, mid_1, compartments_1, complexes_1, pairs_1, rate_1)

sequence_2 = (objects.s34, objects.s35, objects.s36, objects.s37, objects.s38)
mid_2 = 2
compartments_2 = ["cyt"] * 4 + ["cell"]
complexes_2 = [(0, 1), (2, 2), (3, 3), (4, 4)]
pairs_2 = [(0, 2), (1, 3), (None, 4)]
rate_2 = Rate("3.0*[K()::cyt]/2.0*v_1")

r2 = Rule(sequence_2, mid_2, compartments_2, complexes_2, pairs_2, rate_2)

sequence_3 = (objects.s39, objects.s35, objects.s38, objects.s40, objects.s37)
mid_3 = 3
compartments_3 = ["cyt"] * 2 + ["cell"] + ["cyt"] * 2
complexes_3 = [(0, 1), (2, 2), (3, 3), (4, 4)]
pairs_3 = [(0, 3), (1, 4), (2, None)]
rate_3 = Rate("3.0*[K(T{3+})::cyt]/2.0*v_1")

r3 = Rule(sequence_3, mid_3, compartments_3, complexes_3, pairs_3, rate_3)

# special cases

sequence_4 = (objects.s1_s,)
mid_4 = 1
compartments_4 = ["rep"]
complexes_4 = [(0, 0)]
pairs_4 = [(0, None)]
rate_4 = Rate("k1*[X()::rep]")

r4 = Rule(sequence_4, mid_4, compartments_4, complexes_4, pairs_4, rate_4)

sequence_5 = (objects.s2_s,)
mid_5 = 0
compartments_5 = ["rep"]
complexes_5 = [(0, 0)]
pairs_5 = [(None, 0)]
rate_5 = Rate("1.0/(1.0+([X()::rep])**4.0)")

r5 = Rule(sequence_5, mid_5, compartments_5, complexes_5, pairs_5, rate_5)

rule_no_rate = Rule(sequence_1, mid_1, compartments_1, complexes_1, pairs_1, None)


def test_parser():
    rule_expr = "K(S{u}).B()::cyt => K(S{p})::cyt + B()::cyt + D(B{_})::cell @ 3*[K()::cyt]/2*v_1"
    assert objects.rule_parser.parse(rule_expr).data[1] == r2

    rule_expr = "K(B{-}).B()::cyt + D(B{_})::cell => K(B{+})::cyt + B()::cyt @ 3*[K(T{3+})::cyt]/2*v_1"
    assert objects.rule_parser.parse(rule_expr).data[1] == r3

    rule_expr = "X()::rep => @ k1*[X()::rep]"
    assert objects.rule_parser.parse(rule_expr).data[1] == r4

    rule_expr = "=> Y()::rep @ 1/(1+([X()::rep])**4)"
    assert objects.rule_parser.parse(rule_expr).data[1] == r5

    rule_expr = "K(S{u}).B()::cyt => K(S{p})::cyt + B()::cyt"
    assert objects.rule_parser.parse(rule_expr).data[1] == rule_no_rate
