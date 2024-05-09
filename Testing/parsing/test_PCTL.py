import pytest

from eBCSgen.Parsing.ParsePCTLformula import PCTLparser

parser = PCTLparser()

def test_parse():
    formula = "P =? [F T(P{m})::x >= 2 & T(P{i})::x = 0]"
    assert parser.parse(formula).success
    formula = "P >= 0.5 [G T(P{m})::x = 2 & T(P{i})::x <= 0]"
    assert parser.parse(formula).success
    formula = "P <= 0.5 [T(P{m})::x < 2 U T(P{m})::x > 0]"
    assert parser.parse(formula).success
    formula = "P > 0.5 [F T(P{m})::x < 2 & ( T(P{m})::x = 0 | T()::x >= 7)]"
    assert parser.parse(formula).success
    formula = "P < 0.5 [G (T(P{m})::x = 2 & T(P{m})::x = 0) | (T(P{m})::x <= 2 & T(P{m})::x >= 0) ]"
    assert parser.parse(formula).success