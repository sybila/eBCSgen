from Core.Rate import tree_to_string
from lark import Transformer, Tree


class Formula:
    """
    Class to represent Formula.
    """
    def __init__(self, success, data):
        self.success = success
        self.data = data

    def __str__(self):
        return "".join(tree_to_string(self.data))

    def get_complexes(self) -> list:
        """
        Extracts all used Complexes from the Tree.

        :return: list of extracted Complexes
        """
        APs = self.get_APs()
        return list(map(lambda ap: ap.complex, APs))

    def get_APs(self) -> list:
        """
        Extracts all AtomicPropositions from the Tree.

        :return: list of Atomic Propositions
        """
        extractor = ComplexExtractor()
        extractor.transform(self.data)
        return extractor.APs

    def replace_APs(self, replacements: dict) -> 'Formula':
        """
        Replaces APs according to given dictionary.
        This is used for explicit file format for PRISM.

        :param replacements: dictionary of type AtomicProposition -> str
        :return: new Formula with replaced APS
        """
        replacetor = APreplacetor(replacements)
        data = replacetor.transform(self.data)
        return Formula(True, data)


class AtomicProposition:
    def __init__(self, complex, sign, number):
        self.complex = complex
        self.sign = sign
        self.number = number

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[" + str(self.complex) + self.sign + str(self.number) + "]"

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other: 'AtomicProposition'):
        return self.complex == other.complex and self.sign == other.sign and self.number == other.number


class ComplexExtractor(Transformer):
    def __init__(self):
        super(Transformer, self).__init__()
        self.APs = []

    def ap(self, proposition):
        self.APs.append(proposition[0])


class APreplacetor(Transformer):
    def __init__(self, replacements):
        super(Transformer, self).__init__()
        self.replacements = replacements

    def ap(self, proposition):
        return Tree("ap", [self.replacements[proposition[0]]])
