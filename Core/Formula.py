from Core.Rate import tree_to_string
from lark import Transformer


class Formula:
    """
    Class to represent Formula.
    """
    def __init__(self, success, data):
        self.success = success
        self.data = data

    def __str__(self):
        return "".join(tree_to_string(self.data))