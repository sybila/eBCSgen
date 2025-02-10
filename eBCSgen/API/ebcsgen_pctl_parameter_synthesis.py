import argparse

from eBCSgen.Analysis.PCTL import PCTL
from eBCSgen.Errors.FormulaParsingError import FormulaParsingError
from eBCSgen.Errors.InvalidInputError import InvalidInputError
from eBCSgen.Parsing.ParseBCSL import load_TS_from_json
from eBCSgen.Parsing.ParsePCTLformula import PCTLparser

class FakeFile:
    def __init__(self, content):
        self.content = content.decode("utf-8")

    def read(self):
        return self.content

def pctl_parameter_synthesis():
    args_parser = argparse.ArgumentParser(description='Parameter synthesis')

    args_parser._action_groups.pop()
    required = args_parser.add_argument_group('required arguments')
    optional = args_parser.add_argument_group('optional arguments')

    required.add_argument('--transition_file', required=True)
    required.add_argument('--output', type=str, required=True)
    required.add_argument('--formula', type=str, required=True)
    optional.add_argument('--region', type=str)

    args = args_parser.parse_args()

    if args.region:
        region = args.region.replace("=", "<=")
    else:
        region = None

    ts = load_TS_from_json(args.transition_file)

    if len(ts.params) == 0:
        raise InvalidInputError("Provided model is not parametrised - parameter synthesis cannot be executed.")

    if "?" not in args.formula:
        if not region:
            params = set()
        else:
            params = {param.split("<=")[1] for param in region.split(",")}

        undefined = set(ts.params) - params
        if undefined:
            raise InvalidInputError("Intervals undefined for parameters: {}.".format(", ".join(undefined)))

    formula = PCTLparser().parse(args.formula)
    if formula.success:
        result = PCTL.parameter_synthesis(ts, formula, region)
        if "?" not in args.formula:
            result = FakeFile(result)
            df = PCTL.process_output(result)
            df.to_csv(args.output, index=False)
        else:
            with open(args.output, "w") as f:
                f.write(result.decode("utf-8"))
    else:
        raise FormulaParsingError(formula.data, args.formula)

if __name__ == '__main__':
    pctl_parameter_synthesis()
