from lark import Transformer, Tree

from eBCSgen.Errors.ComplexOutOfScope import ComplexOutOfScope
from eBCSgen.Core.Rate import tree_to_string


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

    def replace_complexes(self, labels: dict) -> 'Formula':
        """
        Replaces Complexes with PRISM name given by ordering.

        :return: new Formula with replaced Complexes
        """
        replacetor = ComplexReplacetor(labels)
        data = replacetor.transform(self.data)
        return Formula(True, data)

    def get_APs(self) -> list:
        """
        Extracts all AtomicPropositions from the Tree.

        :return: list of Atomic Propositions
        """
        extractor = APextractor()
        extractor.transform(self.data)
        return extractor.APs

    def replace_APs(self, replacements: dict, extra_quotes=True) -> 'Formula':
        """
        Replaces APs according to given dictionary.
        This is used for explicit file format for PRISM.

        :param replacements: dictionary of type AtomicProposition -> str
        :param extra_quotes: wrap AP labels in quotes
        :return: new Formula with replaced APS
        """
        replacetor = APreplacetor(replacements, extra_quotes)
        data = replacetor.transform(self.data)
        return Formula(True, data)

    def create_complex_labels(self, ordering: tuple):
        """
        Creates label for each unique Complex from Formula.
        This covers two cases - ground and abstract Complexes.
        For the abstract ones, a PRISM formula needs to be constructed
        as a sum of all compatible complexes.

        :param ordering: given complex ordering of TS
        :return: unique label for each Complex and list of PRISM formulas for abstract Complexes
        """
        labels = dict()
        prism_formulas = list()
        for complex in self.get_complexes():
            if complex in ordering:
                labels[complex] = complex.to_PRISM_code(ordering.index(complex))
            else:
                indices = complex.identify_compatible(ordering)
                if not indices:
                    raise ComplexOutOfScope(complex)
                id = "ABSTRACT_VAR_" + "".join(list(map(str, indices)))
                labels[complex] = id
                prism_formulas.append(id + " = " + "+".join(["VAR_{}".format(i) for i in indices]) +
                                      "; // " + str(complex))
        return labels, prism_formulas


class AtomicProposition:
    def __init__(self, complex, sign, number):
        self.complex = complex
        self.sign = sign
        self.number = number

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.complex) + self.sign + str(self.number)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other: 'AtomicProposition'):
        return self.complex == other.complex and self.sign == other.sign and self.number == other.number


class APextractor(Transformer):
    def __init__(self):
        super(Transformer, self).__init__()
        self.APs = []

    def ap(self, proposition):
        self.APs.append(proposition[0])


class APreplacetor(Transformer):
    def __init__(self, replacements, extra_quotes):
        super(Transformer, self).__init__()
        self.replacements = replacements
        self.extra_quotes = extra_quotes

    def ap(self, proposition):
        quotes = '"' if self.extra_quotes else ''
        return Tree("ap", [quotes + self.replacements[proposition[0]] + quotes])


class ComplexReplacetor(Transformer):
    def __init__(self, labels):
        super(Transformer, self).__init__()
        self.labels = labels

    def ap(self, proposition):
        ap = proposition[0]
        ap.complex = self.labels[ap.complex]
        return Tree("ap", [ap])
