import numpy as np
import collections

from eBCSgen.Core.Atomic import AtomicAgent
from eBCSgen.Core.Rule import Rule
from eBCSgen.Core.Structure import StructureAgent
from eBCSgen.Core.Complex import Complex
from eBCSgen.Core.Side import Side
from eBCSgen.Core.Rate import Rate
from eBCSgen.TS.State import Vector, State, Memory
from eBCSgen.Core.Reaction import Reaction

from eBCSgen.Parsing.ParseBCSL import Parser

rate_parser = Parser("rate")
atomic_parser = Parser("atomic")
structure_parser = Parser("structure")
complex_parser = Parser("complex")
state_parser = Parser("state")
side_parser = Parser("side")
rate_complex_parser = Parser("rate_complex")
rule_parser = Parser("rule")
rules_parser = Parser("rules")
model_parser = Parser("model")

# atomic
a1 = AtomicAgent("T", "s")
a2 = AtomicAgent("S", "a")
a3 = AtomicAgent("S", "s")
a4 = AtomicAgent("T", "_")
a5 = AtomicAgent("S", "_")
a6 = AtomicAgent("T", "p")
a7 = AtomicAgent("T", "u")

a8 = AtomicAgent("T", "s")
a9 = AtomicAgent("T", "i")
a10 = AtomicAgent("S", "i")
a11 = AtomicAgent("U", "a")
a12 = AtomicAgent("U", "_")
a13 = AtomicAgent("U", "b")
a14 = AtomicAgent("T", "a")

a15 = AtomicAgent("S", "u")
a16 = AtomicAgent("S", "p")
a17 = AtomicAgent("B", "_")
a18 = AtomicAgent("B", "-")
a19 = AtomicAgent("B", "+")

a20 = AtomicAgent("B", "a")

a4_p = AtomicAgent("C", "p")
a4_u = AtomicAgent("C", "u")

u2_c1_p = AtomicAgent("U", "p")
u2_c1_u = AtomicAgent("U", "u")


# structure
s1 = StructureAgent("B", {a1})
s2 = StructureAgent("D", set())
s3 = StructureAgent("K", {a1, a3, a5})
s4 = StructureAgent("B", {a4})
s5 = StructureAgent("D", {a5, a6})
s6 = StructureAgent("K", set())
s7 = StructureAgent("K", {a2, a4})

s8 = StructureAgent("X", {a1})
s9 = StructureAgent("A", {a10, a11})
s10 = StructureAgent("X", {a4})
s11 = StructureAgent("A", {a10, a12})
s12 = StructureAgent("A", {a5, a11})
s13 = StructureAgent("A", set())
s14 = StructureAgent("A", {a10, a13})

s15 = StructureAgent("strA", {a1, a2})
s16 = StructureAgent("strA", {a2, a4})
s18 = StructureAgent("strD", set())
s19 = StructureAgent("strA", {a2, a1})
s20 = StructureAgent("strA", {a1})
s21 = StructureAgent("strA", {a6})
s23 = StructureAgent("strA", {a6, a2})
s24 = StructureAgent("strA", {a1, a10})
s25 = StructureAgent("strA", {a6, a10})
s26 = StructureAgent("strA", set())

s27 = StructureAgent("X", {a2})
s28 = StructureAgent("X", {a10})
s29 = StructureAgent("K", {a14})
s30 = StructureAgent("K", {a9})
s31 = StructureAgent("X", set())

s32 = StructureAgent("S", set())

s34 = StructureAgent("K", {a15})
s35 = StructureAgent("B", set())
s36 = StructureAgent("K", {a16})
s37 = StructureAgent("B", set())
s38 = StructureAgent("D", {a17})
s39 = StructureAgent("K", {a18})
s40 = StructureAgent("K", {a19})

s41 = StructureAgent("Y", set())
s42 = StructureAgent("Z", set())
s43 = StructureAgent("W", set())
s44 = StructureAgent("D", {a4})
s45 = StructureAgent("B", {a14, a16})

s46 = StructureAgent("K", {a16, a9})
s47 = StructureAgent("K", {a15, a9})

s6_c1_p = StructureAgent("D", {a4_p})
s6_c1_u = StructureAgent("D", {a4_u})

s2_c1_p = StructureAgent("B", {u2_c1_p})
s2_c1_u = StructureAgent("B", {u2_c1_u})

s1_c1_a = StructureAgent("K", {a15, a14})

s3_c1_a = StructureAgent("K", {a16, a14})

# complex
c1 = Complex([s1], "cell")
c2 = Complex([s1, s2, s3], "cell")
c3 = Complex([s1, s3, s5], "cyt")
c4 = Complex([s1, a1], "cyt")
c5 = Complex([s2] * 3 + [s4] * 3, "cell")
c6 = Complex([s6] * 2 + [a6], "cyt")
c7 = Complex([a7, a4], "cell")

c8 = Complex([s8, s9, s9], "cyt")
c9 = Complex([s10, s11, s12], "cyt")
c10 = Complex([s9, s9, s8], "cyt")
c11 = Complex([s9, s9, s8], "cell")

c12 = Complex([s9, s11, a1], "cell")
c13 = Complex([s13, s13, a4], "cell")

large_c1 = Complex([s11] * 6 + [s10] * 5, "cell")
large_c2 = Complex([s12] * 7 + [s10] * 6, "cell")

c14 = Complex([s6], "cyt")  # K()::cyt
c15 = Complex([s29], "cyt")  # K(T{a})::cyt
c16 = Complex([s30], "cyt")  # K(T{i})::cyt
c17 = Complex([s30, s27], "cyt")  # K(T{i}).X(S{a})::cyt
c18 = Complex([s30, s28], "cyt")  # K(T{i}).X(S{i})::cyt
c19 = Complex([s29, s27], "cyt")  # K(T{a}).X(S{a})::cyt
c20 = Complex([s29, s28], "cyt")  # K(T{a}).X(S{i})::cyt

c21 = Complex([s32], "rep")
c22 = Complex([s2], "rep")

c23 = Complex([s34, s35], "cyt")
c24 = Complex([s36], "cyt")
c25 = Complex([s35], "cyt")
c26 = Complex([s38], "cell")

c27 = Complex([s31], "rep")
c28 = Complex([s41], "rep")
c29 = Complex([s42], "rep")
c30 = Complex([s43], "rep")

c1_c1 = Complex([s2_c1_u], "cyt")  # B(U{u})::cyt
c1_c2 = Complex([s2_c1_p], "cyt")  # B(U{p})::cyt
c1_c3 = Complex([s1_c1_a], "cyt")  # K(S{u},T{a})::cyt
c1_c5 = Complex([s3_c1_a, s2_c1_u], "cyt")  # K(S{p},T{a}).B(U{u})::c
c1_c6 = Complex([s46, s2_c1_u], "cyt")  # K(S{p},T{i}).B(U{u})::c
c1_c7 = Complex([s46, s2_c1_p], "cyt")  # K(S{p},T{i}).B(U{p})::c
c1_c8 = Complex([s3_c1_a, s2_c1_p], "cyt")  # K(S{p},T{a}).B(U{p})::c
c1_c9 = Complex([s6_c1_p], "cyt")  # D(C{p})::cyt
c1_c10 = Complex([s6_c1_u], "cyt")  # D(C{u})::cyt
sequence_no_change = (s1_c1_a, s2_c1_u, s3_c1_a, s2_c1_u, s6_c1_p)

counter_c1 = Complex(collections.Counter({s35: 2}), "cyt")
counter_c2 = Complex(collections.Counter({s36: 1}), "cyt")
counter_c3 = Complex(collections.Counter({s35: 1}), "cyt")
counter_c4 = Complex(collections.Counter({s44: 1}), "cell")
counter_c5 = Complex(collections.Counter({s37: 1}), "cell")
counter_c6 = Complex(collections.Counter({s45: 1}), "cell")

cx1 = Complex([a20], "cyt")
cx2 = Complex([s46], "cyt")
cx3 = Complex([s47], "cyt")  # K(S{u},T{i})::cyt
cx4 = Complex([s46, a20], "cyt")
cx5 = Complex([s47, a20], "cyt")

# side
side1 = Side([c1])
side2 = Side([c4, c5])
side3 = Side([c1, c2, c2])
side4 = Side([c7, c6, c5])
side5 = Side([])

lhs = Side([c23])
rhs = Side([c24, c25, c26])

side6 = Side([counter_c1, counter_c2, counter_c4])
side7 = Side([counter_c2, counter_c3, counter_c4])
side8 = Side([counter_c3, counter_c4, counter_c2])
side9 = Side([counter_c6, counter_c1])
side10 = Side([counter_c5, counter_c1])
side11 = Side([counter_c5, counter_c1, counter_c2])
side12 = Side([counter_c6, counter_c1, counter_c3, counter_c4])

# states
state1 = State(Vector(np.array([2, 3])), Memory(0))
state2 = State(Vector(np.array([2, 0, 3, 1, 6, 2])), Memory(0))
state3 = State(Vector(np.array((0, 0))), Memory(0))
state4 = State(Vector(np.array((1, 0))), Memory(0))
state5 = State(Vector(np.array((2, 0))), Memory(0))
state6 = State(Vector(np.array((3, 0))), Memory(0))
state7 = State(Vector(np.array((4, 0))), Memory(0))
state8 = State(Vector(np.array((5, 0))), Memory(0))
state9 = State(Vector(np.array((6, 0))), Memory(0))
state10 = State(Vector(np.array((7, 1))), Memory(0))
state11 = State(Vector(np.array((7, 2))), Memory(0))
state12 = State(Vector(np.array((7, 3))), Memory(0))
state13 = State(Vector(np.array((7, 4))), Memory(0))
state14 = State(Vector(np.array((7, 5))), Memory(0))
state15 = State(Vector(np.array((7, 6))), Memory(0))

# rules

sequence_1 = (s31,)
mid_1 = 1
compartments_1 = ["rep"]
complexes_1 = [(0, 0)]
pairs_1 = [(0, None)]
rate_1 = Rate("k1*[X()::rep]")

r1 = Rule(sequence_1, mid_1, compartments_1, complexes_1, pairs_1, rate_1)

sequence_2 = (s42, s31)
mid_2 = 1
compartments_2 = ["rep"] * 2
complexes_2 = [(0, 0), (1, 1)]
pairs_2 = [(0, 1)]

r2 = Rule(sequence_2, mid_2, compartments_2, complexes_2, pairs_2, None)

sequence_3 = (s41,)
mid_3 = 0
compartments_3 = ["rep"]
complexes_3 = [(0, 0)]
pairs_3 = [(None, 0)]
rate_3 = Rate("1.0/(1.0+([X()::rep])**4.0)")

r3 = Rule(sequence_3, mid_3, compartments_3, complexes_3, pairs_3, rate_3)

sequence_4 = (s34, s35, s36, s37)
reversed_sequence_4 = (s36, s37, s34, s35)
mid_4 = 2
compartments_4 = ["cyt"] * 4
complexes_4 = [(0, 1), (2, 2), (3, 3)]
reversed_complexes_4 = [(0, 0), (1, 1), (2, 3)]
pairs_4 = [(0, 2), (1, 3)]
rate_4 = Rate("3.0*[K()::cyt]/2.0*v_1")
reversed_rate_4 = Rate("2.0*[K()::cyt]/3.0*v_1")

r4 = Rule(sequence_4, mid_4, compartments_4, complexes_4, pairs_4, rate_4)
reversed_r4a = Rule(
    reversed_sequence_4, mid_4, compartments_4, reversed_complexes_4, pairs_4, rate_4
)
reversed_r4b = Rule(
    reversed_sequence_4,
    mid_4,
    compartments_4,
    reversed_complexes_4,
    pairs_4,
    reversed_rate_4,
)
sequence_one_side_bidirectional = (s36, s37)
mid_one_side_bidirectional_a = 2
mid_one_side_bidirectional_b = 0
compartments_one_side_bidirectional = ["cyt"] * 2
complexes_one_side_bidirectional = [(0, 0), (1, 1)]
pairs_one_side_bidirectional_a = [(0, None), (1, None)]
pairs_one_side_bidirectional_b = [(None, 0), (None, 1)]
one_side_bidirectional_a = Rule(
    sequence_one_side_bidirectional,
    mid_one_side_bidirectional_a,
    compartments_one_side_bidirectional,
    complexes_one_side_bidirectional,
    pairs_one_side_bidirectional_a,
    rate_4,
)
one_side_bidirectional_b = Rule(
    sequence_one_side_bidirectional,
    mid_one_side_bidirectional_b,
    compartments_one_side_bidirectional,
    complexes_one_side_bidirectional,
    pairs_one_side_bidirectional_b,
    rate_4,
)
one_side_bidirectional_b_reversed_rate = Rule(
    sequence_one_side_bidirectional,
    mid_one_side_bidirectional_b,
    compartments_one_side_bidirectional,
    complexes_one_side_bidirectional,
    pairs_one_side_bidirectional_b,
    reversed_rate_4,
)
one_side_bidirectional_a_no_rate = Rule(
    sequence_one_side_bidirectional,
    mid_one_side_bidirectional_a,
    compartments_one_side_bidirectional,
    complexes_one_side_bidirectional,
    pairs_one_side_bidirectional_a,
    None,
)
one_side_bidirectional_b_no_rate = Rule(
    sequence_one_side_bidirectional,
    mid_one_side_bidirectional_b,
    compartments_one_side_bidirectional,
    complexes_one_side_bidirectional,
    pairs_one_side_bidirectional_b,
    None,
)


sequence_5 = (s34, s35, s36, s37, s38)
mid_5 = 2
compartments_5 = ["cyt"] * 4 + ["cell"]
complexes_5 = [(0, 1), (2, 2), (3, 3), (4, 4)]
pairs_5 = [(0, 2), (1, 3), (None, 4)]
rate_5 = Rate("3.0*[K()::cyt]/2.0*v_1")

r5 = Rule(sequence_5, mid_5, compartments_5, complexes_5, pairs_5, rate_5)

sequence_6 = (s39, s35, s38, s40, s37)
mid_6 = 3
compartments_6 = ["cyt"] * 2 + ["cell"] + ["cyt"] * 2
complexes_6 = [(0, 1), (2, 2), (3, 3), (4, 4)]
pairs_6 = [(0, 3), (1, 4), (2, None)]
rate_6 = Rate("3.0*[K(T{3+})::cyt]/2.0*v_1")

r6 = Rule(sequence_6, mid_6, compartments_6, complexes_6, pairs_6, rate_6)
rule_no_rate = Rule(sequence_4, mid_4, compartments_4, complexes_4, pairs_4, None)
reversed_no_rate = Rule(
    reversed_sequence_4, mid_4, compartments_4, reversed_complexes_4, pairs_4, None
)

sequence_c1 = (s34, s35, s36, s37, s2)
mid_c1 = 2
compartments_c1 = ["cyt"] * 5
complexes_c1 = [(0, 0), (1, 1), (2, 3), (4, 4)]
pairs_c1 = [(0, 2), (1, 3), (None, 4)]
rate_c1 = Rate("3*[K()::cyt]/2*v_1")

rule_c1 = Rule(sequence_c1, mid_c1, compartments_c1, complexes_c1, pairs_c1, rate_c1)

rule_no_change = Rule(
    sequence_no_change, mid_c1, compartments_c1, complexes_c1, pairs_c1, rate_c1
)

# reactions

reaction1 = Reaction(lhs, rhs, rate_5)

reaction_c1_1 = Reaction(
    Side([c1_c1, c1_c3]),
    Side([c1_c5, c1_c9]),
    rate_c1,
)
reaction_c1_2 = Reaction(
    Side([c1_c1, c1_c3]),
    Side([c1_c5, c1_c10]),
    rate_c1,
)
reaction_c1_3 = Reaction(
    Side([c1_c2, cx3]),
    Side([c1_c7, c1_c10]),
    rate_c1,
)
reaction_c1_4 = Reaction(
    Side([c1_c1, cx3]),
    Side([c1_c6, c1_c9]),
    rate_c1,
)
reaction_c1_5 = Reaction(
    Side([c1_c2, c1_c3]),
    Side([c1_c8, c1_c9]),
    rate_c1,
)
reaction_c1_6 = Reaction(
    Side([c1_c2, c1_c3]),
    Side([c1_c8, c1_c10]),
    rate_c1,
)
reaction_c1_7 = Reaction(
    Side([c1_c1, cx3]),
    Side([c1_c6, c1_c10]),
    rate_c1,
)
reaction_c1_8 = Reaction(
    Side([c1_c2, cx3]),
    Side([c1_c7, c1_c9]),
    rate_c1,
)

reactions_c1 = {
    reaction_c1_1,
    reaction_c1_2,
    reaction_c1_3,
    reaction_c1_4,
    reaction_c1_5,
    reaction_c1_6,
    reaction_c1_7,
    reaction_c1_8,
}
