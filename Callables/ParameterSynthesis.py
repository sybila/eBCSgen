import sys, os
import argparse

# this add to path eBCSgen home dir, so it can be called from anywhere
sys.path.append(os.path.split(sys.path[0])[0])

from Parsing.ParseBCSL import Parser
import Parsing.ParsePCTLformula
from Errors.ModelParsingError import ModelParsingError
from Errors.FormulaParsingError import FormulaParsingError

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

"""

args_parser = argparse.ArgumentParser(description='Parameter synthesis')
args_parser.add_argument('--model', type=str, required=True)
args_parser.add_argument('--output', type=str, required=True)
args_parser.add_argument('--bound', type=int, default=None)
args_parser.add_argument('--formula', type=str, required=True)
args_parser.add_argument('--region', type=str)

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

if model.success:
    formula = Parsing.ParsePCTLformula.PCTLparser().parse(args.formula)
    if formula.success:
        result = model.data.PCTL_synthesis(formula, region, bound)
        f = open(args.output, "w")
        f.write(result.decode("utf-8"))
        f.close()
    else:
        raise FormulaParsingError(formula.data, args.formula)
else:
    raise ModelParsingError(model.data, model_str)
