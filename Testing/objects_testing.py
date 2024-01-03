import numpy as np

from eBCSgen.Core.Atomic import AtomicAgent
from eBCSgen.Core.Structure import StructureAgent
from eBCSgen.Core.Complex import Complex
from eBCSgen.Core.Side import Side
from eBCSgen.Core.Rate import Rate
from eBCSgen.TS.State import Vector, State, Memory

from eBCSgen.Parsing.ParseBCSL import Parser

rate_parser = Parser("rate")
atomic_parser = Parser("atomic")
structure_parser = Parser("structure")
complex_parser = Parser("complex")
state_parser = Parser("state")
side_parser = Parser("side")
rate_complex_parser = Parser("rate_complex")
rule_parser = Parser("rule")
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
s17 = StructureAgent("strA", {a2, a4})
s18 = StructureAgent("strD", set())
s19 = StructureAgent("strA", {a2, a1})
s20 = StructureAgent("strA", {a1})
s21 = StructureAgent("strA", {a6})
s22 = StructureAgent("strA", {a1, a2})
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
s33 = StructureAgent("D", set())

s34 = StructureAgent("K", {a15})
s35 = StructureAgent("B", set())
s36 = StructureAgent("K", {a16})
s37 = StructureAgent("B", set())
s38 = StructureAgent("D", {a17})
s39 = StructureAgent("K", {a18})
s40 = StructureAgent("K", {a19})

s1_s = StructureAgent("X", set())
s2_s = StructureAgent("Y", set())
s3_s = StructureAgent("Z", set())

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
c22 = Complex([s33], "rep")

c23 = Complex([s34, s35], "cyt")
c24 = Complex([s36], "cyt")
c25 = Complex([s35], "cyt")
c26 = Complex([s38], "cyt")

# side
side1 = Side([c1])
side2 = Side([c4, c5])
side3 = Side([c1, c2, c2])
side4 = Side([c7, c6, c5])
side5 = Side([])

# rates
rate1 = Rate(rate_parser.parse("3.0*[K()::cyt]/2.0*v_1").data)
rate2 = Rate(rate_parser.parse("3.0*[K(T{i}).X()::cyt] + [K()::cyt]").data)
rate3 = Rate(rate_parser.parse("(3.0*[K()::cyt])/(2.0*v_1)").data)

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
