import collections
import pytest

from eBCSgen.Parsing.ParseBCSL import Parser
from eBCSgen.Core.Model import Model
from eBCSgen.Core.Rate import Rate
from eBCSgen.Core.Structure import StructureAgent
from eBCSgen.Core.Complex import Complex
from eBCSgen.Core.Rule import Rule

s1 = StructureAgent("X", set())
s2 = StructureAgent("Y", set())
s3 = StructureAgent("Z", set())

c1 = Complex([s1], "rep")
c2 = Complex([s2], "rep")
c3 = Complex([s3], "rep")

#  rules

sequence_1 = (s1,)
mid_1 = 1
compartments_1 = ["rep"]
complexes_1 = [(0, 0)]
pairs_1 = [(0, None)]
rate_1 = Rate("k1*[X()::rep]")

r1 = Rule(sequence_1, mid_1, compartments_1, complexes_1, pairs_1, rate_1)

sequence_2 = (s3, s1)
mid_2 = 1
compartments_2 = ["rep"] * 2
complexes_2 = [(0, 0), (1, 1)]
pairs_2 = [(0, 1)]

r2 = Rule(sequence_2, mid_2, compartments_2, complexes_2, pairs_2, None)

sequence_3 = (s2,)
mid_3 = 0
compartments_3 = ["rep"]
complexes_3 = [(0, 0)]
pairs_3 = [(None, 0)]
rate_3 = Rate("1.0/(1.0+([X()::rep])**4.0)")

r3 = Rule(sequence_3, mid_3, compartments_3, complexes_3, pairs_3, rate_3)

# inits

inits = collections.Counter({c1: 2, c2: 1})

# defs

defs = {'k1': 0.05, 'k2': 0.12}

model = Model({r1, r2, r3}, inits, defs, set())
# model

model_parser = Parser("model")

model_str_1 = """
        #! rules
        X()::rep => @ k1*[X()::rep]
        Z()::rep => X()::rep
        => Y()::rep @ 1/(1+([X()::rep])**4)

        #! inits
        2 X()::rep
        Y()::rep
        
        #! definitions
        k1 = 0.05
        k2 = 0.12 
        """

model_str_2 = """
        #! rules
        X(K{i})::rep => X(K{p})::rep @ k1*[X()::rep]
        X(T{a})::rep => X(T{o})::rep @ k2*[Z()::rep]
        => Y(P{f})::rep @ 1/(1+([X()::rep])**4)

        #! inits
        2 X(K{c}, T{e}).X(K{c}, T{j})::rep
        Y(P{g}, N{l})::rep

        #! definitions
        k1 = 0.05
        k2 = 0.12
        """

model_with_comments_str = \
    """
    #! rules
    // commenting
    X(K{i})::rep => X(K{p})::rep @ k1*[X()::rep] // also here
    X(T{a})::rep => X(T{o})::rep @ k2*[Z()::rep]
    => Y(P{f})::rep @ 1/(1+([X()::rep])**4) // ** means power (^)

    #! inits
    // here
    2 X(K{c}, T{e}).X(K{c}, T{j})::rep
    Y(P{g}, N{l})::rep // comment just 1 item

    #! definitions
    // and
    k1 = 0.05 // also
    k2 = 0.12
    """

model_wrong_1 = \
    """#! rules
    X(K{i})::rep => X(K{p})::rep @ k1*[X()::rep]
    X(T{a})::rep => X(T{o}):;rep @ k2*[Z()::rep]
    => Y(P{f})::rep @ 1/(1+([X()::rep])**4)

    #! inits
    2 X(K{c}, T{e}).X(K{c}, T{j})::rep
    Y(P{g}, N{l})::rep

    #! definitions
    k1 = 0.05
    k2 = 0.12
    """

model_wrong_2 = \
    """#! rules
    X(K{i})::rep => X(K{p})::rep @ k1*[X()::rep]
    X(T{a})::rep = X(T{o})::rep @ k2*[Z()::rep]
    => Y(P{f})::rep @ 1/(1+([X()::rep])**4)

    #! inits
    2 X(K{c}, T{e}).X(K{c}, T{j})::rep
    Y(P{g}, N{l})::rep

    #! definitions
    k1 = 0.05
    k2 = 0.12
    """

def test_parser():
    assert model_parser.parse(model_str_1).data == model


def test_parser_errors():
    assert not model_parser.parse(model_wrong_1).success

    assert not model_parser.parse(model_wrong_2).success
        

def test_comments():
    model_with_comments = model_parser.parse(model_with_comments_str).data
    model_without_comments = model_parser.parse(model_str_2).data

    assert model_with_comments == model_without_comments