import unittest
import libsbml
import os

from eBCSgen.Parsing.ParseBCSL import Parser


class TestSBMLexport(unittest.TestCase):
    def setUp(self):
        model_parser = Parser("model")
        self.models_to_test = {}

        if not os.path.exists("Testing/Output/"):
            os.mkdir("Testing/Output/")

        with open("Testing/BCSL_models_for_SBML_export/general.txt", "r") as model_exp:
            self.models_to_test["general"] = model_parser.parse(model_exp.read()).data
        with open("Testing/BCSL_models_for_SBML_export/izomorphic.txt", "r") as model_izo:
            self.models_to_test["izomorphic"] = model_parser.parse(model_izo.read()).data
        with open("Testing/BCSL_models_for_SBML_export/transition.txt", "r") as model_transition:
            self.models_to_test["transition"] = model_parser.parse(model_transition.read()).data

    def test_by_validator(self):
        validator = libsbml.SBMLValidator()
        for model in self.models_to_test:
            validator.clearFailures()
            document = self.models_to_test[model].export_sbml()
            validator.setDocument(document)
            validator.validate()
            self.assertEqual(validator.getNumFailures(), 0)
            libsbml.writeSBMLToFile(document, "Testing/Output/"+model+".xml")
