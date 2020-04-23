class StormNotAvailable(Exception):
    def __str__(self):
        return 'Internal error : Storm model checker is not available.'
