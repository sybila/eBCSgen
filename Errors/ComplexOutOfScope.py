class ComplexOutOfScope(Exception):
    def __init__(self, complex):
        self.complex = complex

    def __str__(self):
        return 'Error while processing PCTL formula:' \
               '\n\nComplex "{}" out of scope of the model.'.format(self.complex)
