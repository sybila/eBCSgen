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
usage: PCTLModelChecking.py [-h] --transition_file TRANSITION_FILE 
                                 --output OUTPUT 
                                 --formula FORMULA 
                                 [--local_storm]

Model checking

required arguments:
  --transition_file TRANSITION_FILE
  --output OUTPUT
  --formula FORMULA

optional arguments:
  --local_storm
"""

args_parser = argparse.ArgumentParser(description='Model checking')

args_parser._action_groups.pop()
required = args_parser.add_argument_group('required arguments')
optional = args_parser.add_argument_group('optional arguments')

required.add_argument('--transition_file', required=True)
required.add_argument('--output', type=str, required=True)
required.add_argument('--formula', type=str, required=True)
optional.add_argument('--local_storm', nargs="?", const=True)

args = args_parser.parse_args()

if args.local_storm:
    local_storm = True
else:
    local_storm = False

ts = load_TS_from_json(args.transition_file)
# TODO for presence of rates

if len(ts.params) != 0:
    raise InvalidInputError("Provided transition system is parametrised - model checking cannot be executed.")

formula = Parsing.ParsePCTLformula.PCTLparser().parse(args.formula)
if formula.success:
    result = PCTL.model_checking(ts, formula, storm_local=local_storm)
    f = open(args.output, "w")
    f.write(result.decode("utf-8"))
    f.close()
else:
    raise FormulaParsingError(formula.data, args.formula)
