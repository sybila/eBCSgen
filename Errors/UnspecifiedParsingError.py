class UnspecifiedParsingError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'Unspecified error while parsing the model:\n\n {} \n\n'\
               'Please check the model for any ambiguous expressions and typos.'.format(self.message)
