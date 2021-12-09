import sys, os
import argparse

# this add to path eBCSgen home dir, so it can be called from anywhere
sys.path.append(os.path.split(sys.path[0])[0])

from Analysis.PCTL import PCTL
from Parsing.ParseBCSL import load_TS_from_json
import Parsing.ParsePCTLformula

from Errors.FormulaParsingError import FormulaParsingError
from Errors.InvalidInputError import InvalidInputError

"""
usage: PCTLParameterSynthesis.py [-h] --transition_file TRANSITION_FILE 
                                      --output OUTPUT 
                                      --formula FORMULA
                                      [--region REGION] 
                                      [--local_storm]                        

Parameter synthesis

required arguments:
  --transition_file TRANSITION_FILE
  --output OUTPUT
  --formula FORMULA

optional arguments:
  --region REGION
  --local_storm
"""

args_parser = argparse.ArgumentParser(description='Parameter synthesis')

args_parser._action_groups.pop()
required = args_parser.add_argument_group('required arguments')
optional = args_parser.add_argument_group('optional arguments')

required.add_argument('--transition_file', required=True)
required.add_argument('--output', type=str, required=True)
required.add_argument('--formula', type=str, required=True)
optional.add_argument('--local_storm', nargs="?", const=True)
optional.add_argument('--region', type=str)

args = args_parser.parse_args()

if args.region:
    region = args.region.replace("=", "<=")
else:
    region = None

if args.local_storm:
    local_storm = True
else:
    local_storm = False

ts = load_TS_from_json(args.transition_file)
# TODO for presence of rates

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

formula = Parsing.ParsePCTLformula.PCTLparser().parse(args.formula)
if formula.success:
    result = PCTL().parameter_synthesis(ts, formula, region, local_storm)
    f = open(args.output, "w")
    f.write(result.decode("utf-8"))
    f.close()
else:
    raise FormulaParsingError(formula.data, args.formula)
