import sys

class FormulaParsingError(Exception):
    def __init__(self, error, formula):
        self.error = error
        self.formula = formula
        sys.tracebacklimit = 0

    def __str__(self):
        position = self.error['column'] - 1
        return 'Error while parsing the formula:\n\n{}\n{}\n\n'.format(self.formula," "*position + "^") + \
               'Unexpected "' + self.error['unexpected'] + \
               '", expected one of: \"' + "\", \"".join(self.error['expected']) + '\"'
