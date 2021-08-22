import sys, os
import argparse

# this add to path eBCSgen home dir, so it can be called from anywhere
sys.path.append(os.path.split(sys.path[0])[0])

from Analysis.CTL import CTL
from Parsing.ParseBCSL import load_TS_from_json
import Parsing.ParseCTLformula
from Errors.FormulaParsingError import FormulaParsingError
from Errors.InvalidInputError import InvalidInputError

"""
usage: CTLModelChecking.py [-h] --transition_file TRANSITION_FILE 
                                 --output OUTPUT 
                                 --formula FORMULA 

Model checking

required arguments:
  --transition_file TRANSITION_FILE
  --output OUTPUT 
  --formula FORMULA
"""

args_parser = argparse.ArgumentParser(description='Model checking')

args_parser._action_groups.pop()
required = args_parser.add_argument_group('required arguments')

required.add_argument('--transition_file', required=True)
required.add_argument('--output', type=str, required=True)
required.add_argument('--formula', type=str, required=True)

args = args_parser.parse_args()

ts = load_TS_from_json(args.transition_file)


if len(ts.params) != 0:
    raise InvalidInputError("Provided transition system is parametrised - model checking cannot be executed.")

formula = Parsing.ParseCTLformula.CTLparser().parse(args.formula)
if formula.success:
    result, states = CTL.model_checking(ts, formula)
    output = 'Result: {}\nNumber of satisfying states: {}'.format(result, len(states))
    f = open(args.output, "w")
    f.write(output)
    f.close()
else:
    raise FormulaParsingError(formula.data, args.formula)
