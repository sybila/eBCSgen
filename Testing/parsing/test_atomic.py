from eBCSgen.Parsing.ParseBCSL import Parser
import Testing.parsing.objects_testing as objects


parser = Parser("atomic")


def test_parser():
    assert parser.parse("T{s}").data == objects.a1
    assert parser.parse("S{a}").data == objects.a2
    assert parser.parse("S{s}").data == objects.a3
    assert parser.parse("T{_}").data == objects.a4
    assert parser.parse("S{_}").data == objects.a5
    assert parser.parse("T{p}").data == objects.a6
    assert parser.parse("T{u}").data == objects.a7
