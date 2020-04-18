class ComplexParsingError(Exception):
    def __init__(self, error, complex):
        self.error = error
        self.complex = complex

    def __str__(self):
        position = self.error['column'] - 1
        return 'Error while parsing the complex agent:\n\n{}\n{}\n\n'.format(self.complex," "*position + "^") +\
               'Unexpected "' + self.error['unexpected'] + \
               '", expected one of: \"' + "\", \"".join(self.error['expected']) + '\"'
