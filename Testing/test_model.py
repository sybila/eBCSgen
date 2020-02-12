import unittest
import collections

from Objects.Rate import Rate
from Objects.Structure import StructureAgent
from Objects.Atomic import AtomicAgent
from Objects.Complex import Complex
from Objects.Rule import Rule
from Objects.Side import Side
from Objects.Reaction import Reaction
from Parsing.ParseModel import Parser


class TestModel(unittest.TestCase):
    def setUp(self):
        self.model = """
        #! rules
        X()::rep => @ k1*[X()::rep]
        Y()::rep => @ k2*[Y()::rep]
        Z()::rep => @ k1*[Z()::rep]
         => X()::rep @ 1/(1+([Z()::rep])^4)
         => Y()::rep @ 1/(1+([X()::rep])^4)
         => Z()::rep @ 1/(1+([Y()::rep])^4)
        
        #! inits
        2 X()::rep
        Y()::rep
        
        #! definitions
        k1 = 0.05
        k2 = 0.12
        """

        self.model_parser = Parser("model")

    def test_parser(self):
        self.model_parser.parse(self.model)
