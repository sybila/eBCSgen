import sys, os
import argparse

# this add to path eBCSgen home dir, so it can be called from anywhere
sys.path.append(os.path.split(sys.path[0])[0])

from Parsing.ParseBCSL import Parser
from Errors.ModelParsingError import ModelParsingError
from Errors.ComplexParsingError import ComplexParsingError

def save_model(model, filename):
    f = open(filename, "w")
    f.write(repr(model))
    f.close()

"""
usage: StaticAnalysis.py [-h] --model MODEL --output OUTPUT --method METHOD
                         [--complex COMPLEX]

Static analysis

arguments
  --model MODEL
  --output OUTPUT
  --method METHOD

optional arguments:
  -h, --help         show this help message and exit
  --complex COMPLEX
"""

args_parser = argparse.ArgumentParser(description='Static analysis')
args_parser.add_argument('--model', type=str, required=True)
args_parser.add_argument('--output', type=str, required=True)
args_parser.add_argument('--method', type=str, required=True)
args_parser.add_argument('--complex')

args = args_parser.parse_args()

model_parser = Parser("model")
model_str = open(args.model, "r").read()
model = model_parser.parse(model_str)

if model.success:
    if args.method == "reduce":
        model.data.reduce_context()
        save_model(model, args.output)
    elif args.method == "eliminate":
        model.data.eliminate_redundant()
        save_model(model, args.output)
    else:
        complex_parser = Parser("rate_complex")
        complex = complex_parser.parse(args.complex)
        if complex.success:
            result = model.data.static_non_reachability(complex.data.children[0])
            f = open(args.output, "w")
            s = "can possibly" if result else "cannot"
            message = "The given agent\n\t{}\n{} be reached in the model.".format(complex.data.children[0], s)
            f.write(message)
            f.close()
        else:
            raise ComplexParsingError(complex.data, args.complex)
else:
    raise ModelParsingError(model.data, model_str)
