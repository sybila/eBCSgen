class ModelParsingError(Exception):
    def __init__(self, error, model):
        self.error = error
        self.model = model

    def __str__(self):
        line = self.model.split("\n")[self.error['line'] - 1]
        position = self.error['column'] - 1
        return 'Error while parsing the model on line {}:\n\n{}\n{}\n\n'.format(self.error['line'],
                                                                                line," "*position + "^") +\
               'Unexpected "' + self.error['unexpected'] + \
               '", expected one of: \"' + "\", \"".join(self.error['expected']) + '\"'
