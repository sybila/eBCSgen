class RegulationParsingError(Exception):
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return "Error while parsing the regulation:\n\n{}".format(self.error)
