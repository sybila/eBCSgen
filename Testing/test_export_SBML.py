import unittest
import libsbml

from eBCSgen.Parsing.ParseBCSL import Parser


class TestSBMLexport(unittest.TestCase):
    def setUp(self):
        model_parser = Parser("model")
        self.models_to_test = {}

        with open("BCSL_models_for_SBML_export/general.txt", "r") as model_exp:
            self.models_to_test["general"] = model_parser.parse(model_exp.read()).data
        with open("BCSL_models_for_SBML_export/izomorphic.txt", "r") as model_izo:
            self.models_to_test["general"] = model_parser.parse(model_izo.read()).data
        with open("BCSL_models_for_SBML_export/transition.txt", "r") as model_transition:
            self.models_to_test["general"] = model_parser.parse(model_transition.read()).data

    def test_by_validator(self):
        validator = libsbml.SBMLValidator()
        for model in self.models_to_test:
            validator.clearFailures()
            document = self.models_to_test[model].export_sbml()
            validator.setDocument(document)
            validator.validate()
            self.assertEqual(validator.getNumFailures(), 0)
            libsbml.writeSBMLToFile(document, "../Export/Output/"+model+".xml")
