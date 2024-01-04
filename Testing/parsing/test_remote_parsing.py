import unittest
import requests

from Testing.models.get_model_str import get_model_str
import Testing.objects_testing as objects


class TestModel(unittest.TestCase):
    def setUp(self):
        self.url = 'http://biodivine-vm.fi.muni.cz/BCSLparser/'

        self.model_wrong_1 = get_model_str("model_wrong1")

        self.model_with_complexes = get_model_str("model_with_complexes.txt")

    def test_remote_request(self):
        try:
            response = requests.get(self.url + 'ping')
            self.assertTrue(response.status_code == 200)
        except requests.exceptions.ConnectionError:
            raise AssertionError("API not available")

    def test_remote_parsing_model(self):
        try:
            # correct one
            result_local = objects.model_parser.syntax_check(self.model_with_complexes)

            headers = {'value-type': 'application/json'}

            response = requests.post(self.url + 'parse',
                                     json={'start': 'model', 'expression': self.model_with_complexes},
                                     headers=headers)
            result_remote = eval(response.text.replace("true", "True"))

            self.assertEqual(result_remote['success'], result_local.success)

            # wrong one
            result_local = objects.model_parser.syntax_check(self.model_wrong_1)

            response = requests.post(self.url + 'parse',
                                     json={'start': 'model', 'expression': self.model_wrong_1},
                                     headers=headers)
            result_remote = eval(response.text.replace("false", "False"))

            self.assertEqual(result_remote['success'], result_local.success)
            self.assertEqual([result_remote["line"], result_remote["column"],
                              result_remote["unexpected"], sorted(result_remote["expected"])],
                             [result_local.data["line"], result_local.data["column"],
                              result_local.data["unexpected"], sorted(result_local.data["expected"])])
        except requests.exceptions.ConnectionError:
            raise AssertionError("API not available")
