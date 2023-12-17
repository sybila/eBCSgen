from eBCSgen.Core.Atomic import AtomicAgent
from eBCSgen.Core.Structure import StructureAgent
from eBCSgen.Core.Complex import Complex
from eBCSgen.Core.Side import Side

# atomic
a1 = AtomicAgent("T", "s")
a2 = AtomicAgent("S", "a")
a3 = AtomicAgent("S", "s")
a4 = AtomicAgent("T", "_")
a5 = AtomicAgent("S", "_")
a6 = AtomicAgent("T", "p")
a7 = AtomicAgent("T", "u")

# structure
s1 = StructureAgent("B", {a1})
s2 = StructureAgent("D", set())
s3 = StructureAgent("K", {a1, a3, a5})
s4 = StructureAgent("B", {a4})
s5 = StructureAgent("D", {a5, a6})
s6 = StructureAgent("K", set())
s7 = StructureAgent("K", {a2, a4})

# complex
c1 = Complex([s1], "cell")
c2 = Complex([s1, s2, s3], "cell")
c3 = Complex([s1, s3, s5], "cyt")
c4 = Complex([s1, a1], "cyt")
c5 = Complex([s2] * 3 + [s4] * 3, "cell")
c6 = Complex([s6] * 2 + [a6], "cyt")
c7 = Complex([a7, a4], "cell")

# side
side1 = Side([c1])
side2 = Side([c4, c5])
side3 = Side([c1, c2, c2])
side4 = Side([c7, c6, c5])
side5 = Side([])
