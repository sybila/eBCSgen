import unittest
import libsbml

from Parsing.ParseBCSL import Parser


class TestSBMLexport(unittest.TestCase):
    def setUp(self):
        model_parser = Parser("model")
        self.models_to_test = {}
        model_exp = """
            #! rules
            KaiC(S{u},T{u}).KaiC(S{u},T{u})::cyt => KaiC(S{p},T{u}).KaiC(S{p},T{u})::cyt @ (kcat1*[KaiA2()::cyt]*[KaiC(S{u},T{u}).KaiC(S{u},T{u})::cyt])/(Km + [KaiC(S{u},T{u}).KaiC(S{u},T{u})::cyt])
            KaiC(S{p},T{u}).KaiC(S{p},T{u})::cyt => KaiC(S{u},T{u}).KaiC(S{u},T{u})::cyt @ (kcat2*[KaiB4{a}.KaiA2()::cyt]*[KaiC(S{p},T{u}).KaiC(S{p},T{u})::cyt])/(Km + [KaiC(S{p},T{u}).KaiC(S{p},T{u})::cyt])
            KaiC(S{p},T{u}).KaiC(S{p},T{u})::cyt => KaiC(S{p},T{p}).KaiC(S{p},T{p})::cyt @ (kcat3*[KaiA2()::cyt]*[KaiC(S{p},T{u}).KaiC(S{p},T{u})::cyt])/(Km + [KaiC(S{p},T{u}).KaiC(S{p},T{u})::cyt])
            KaiC(S{p},T{p}).KaiC(S{p},T{p})::cyt => KaiC(S{p},T{u}).KaiC(S{p},T{u})::cyt @ (kcat4*[KaiB4{a}.KaiA2()::cyt]*[KaiC(S{p},T{p}).KaiC(S{p},T{p})::cyt])/(Km + [KaiC(S{p},T{p}).KaiC(S{p},T{p})::cyt])
            KaiB4{i}::cyt => KaiB4{a}::cyt @ (kcatb2*[KaiB4{i}::cyt])/(Kmb2 + [KaiB4{i}::cyt])
            KaiB4{a}::cyt => KaiB4{i}::cyt @ (kcatb1*[KaiB4{a}::cyt])/(Kmb1 + [KaiB4{a}::cyt])
            KaiB4{a}::cyt + KaiA2()::cyt => KaiB4{a}.KaiA2()::cyt @ k11*[KaiB4{a}::cyt]*[KaiA2()::cyt]
            KaiC().KaiC()::cyt => 2 KaiC()::cyt @ kdimer*[KaiC().KaiC()::cyt]
            2 KaiC()::cyt => KaiC().KaiC()::cyt @ kdimer*[KaiC()::cyt]*([KaiC()::cyt] - 1)

            #! inits
            2 KaiC(S{u},T{u})::cyt
            2 KaiC(S{u},T{u}).KaiC(S{u},T{u})::cyt
            1 KaiB4{a}::cyt
            1 KaiA2()::cyt

            #! definitions
            kcat2 = 0.539
            kcat4 = 0.89
            Km = 0.602
            kcatb2 = 0.346
            kcatb1 = 0.602
            Kmb2 = 66.75
            Kmb1 = 2.423
            k11 = 0.0008756
            kdimer = 1.77
            """
        model_izo = """
        #! rules
            KaiC(S{u},T{p}).KaiC(S{u},T{u})::cyt => KaiC(S{u},T{u}).KaiC(S{u},T{p})::cyt @ (kcat1*[KaiC(S{u},T{p}).KaiC(S{u},T{u})::cyt])
            KaiC(S{u},T{u}).KaiC(S{u},T{u})::cyt => KaiC(S{u},T{u}).KaiC(S{u},T{u})::cyt @ (kcat2*[KaiC(S{u},T{u}).KaiC(S{u},T{p})::cyt])
        
        #! inits
            2 KaiC(S{u},T{u}).KaiC(S{u},T{u})::cyt
            1 KaiB4{a}::cyt
            1 KaiA2()::cyt 
         
        #! definitions
            kcat2 = 0.539
            kcat4 = 0.89
            Km = 0.602
            kcatb2 = 0.346
            kcatb1 = 0.602
            Kmb2 = 66.75
            Kmb1 = 2.423
            k11 = 0.0008756
            kdimer = 1.77
        
        """
        self.models_to_test["general"] = model_parser.parse(model_exp).data
       # self.models_to_test["izomorphic"] = model_parser.parse(model_izo).data

    def test_by_validator(self):
        validator = libsbml.SBMLValidator()
        for model in self.models_to_test:
            validator.clearFailures()
            document = self.models_to_test[model].export_sbml()
            validator.setDocument(document)
            validator.validate()
            self.assertEquals(validator.getNumFailures(), 0)
            libsbml.writeSBMLToFile(document, "../Translating/Output/"+model+".xml")
