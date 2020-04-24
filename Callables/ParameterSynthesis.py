import sys, os
import argparse

# this add to path eBCSgen home dir, so it can be called from anywhere
sys.path.append(os.path.split(sys.path[0])[0])

from Parsing.ParseBCSL import Parser
import Parsing.ParsePCTLformula

from Errors.FormulaParsingError import FormulaParsingError
from Errors.ModelParsingError import ModelParsingError
from Errors.UnspecifiedParsingError import UnspecifiedParsingError
from Errors.InvalidInputError import InvalidInputError

"""
usage: ParameterSynthesis.py [-h] --model MODEL --output OUTPUT
                             [--bound BOUND] --formula FORMULA --region REGION

Parameter synthesis

arguments:
  --model MODEL
  --output OUTPUT
  --formula FORMULA

optional arguments:
  -h, --help         show this help message and exit
  --bound BOUND
  --region REGION
  --local_storm

"""

args_parser = argparse.ArgumentParser(description='Parameter synthesis')
args_parser.add_argument('--model', type=str, required=True)
args_parser.add_argument('--output', type=str, required=True)
args_parser.add_argument('--bound', type=int, default=None)
args_parser.add_argument('--formula', type=str, required=True)
args_parser.add_argument('--region', type=str)
args_parser.add_argument('--local_storm', nargs="?", const=True)

args = args_parser.parse_args()

model_parser = Parser("model")
model_str = open(args.model, "r").read()
model = model_parser.parse(model_str)

if args.bound:
    bound = int(args.bound)
else:
    bound = None

if args.region:
    region = args.region.replace("=", "<=")
else:
    region = None

if args.local_storm:
    local_storm = True
else:
    local_storm = False

if model.success:
    if len(model.data.params) == 0:
        raise InvalidInputError("Provided model is not parametrised - parameter synthesis cannot be executed.")

    if "?" not in args.formula:
        if not region:
            params = set()
        else:
            params = {param.split("<=")[1] for param in region.split(",")}

        undefined = model.data.params - params
        if undefined:
            raise InvalidInputError("Intervals undefined for parameters: {}.".format(", ".join(undefined)))

    formula = Parsing.ParsePCTLformula.PCTLparser().parse(args.formula)
    if formula.success:
        result = model.data.PCTL_synthesis(formula, region, bound, local_storm)
        f = open(args.output, "w")
        f.write(result.decode("utf-8"))
        f.close()
    else:
        raise FormulaParsingError(formula.data, args.formula)
else:
    if "error" in model.data:
        raise UnspecifiedParsingError(model.data["error"])
    raise ModelParsingError(model.data, model_str)
