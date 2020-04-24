class InvalidInputError(Exception):
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return 'Error while processing input data:\n\n{}'.format(self.error)
