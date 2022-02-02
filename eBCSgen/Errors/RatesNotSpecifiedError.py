class RatesNotSpecifiedError(Exception):
    def __str__(self):
        return 'Error while processing input data:\n\nSome rules have unspecified rate functions.'
