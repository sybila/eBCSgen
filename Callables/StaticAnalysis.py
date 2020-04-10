import sys, os
import argparse
import numpy as np

# this add to path eBCSgen home dir, so it can be called from anywhere
sys.path.append(os.path.split(sys.path[0])[0])

from Parsing.ParseBCSL import Parser, load_TS_from_json

def save_model(model, filename):
    f = open(filename, "w")
    f.write(repr(model))
    f.close()

"""

"""

args_parser = argparse.ArgumentParser(description='Static analysis')
args_parser.add_argument('--model', type=str, required=True)
args_parser.add_argument('--output', type=str, required=True)
args_parser.add_argument('--method', type=str, required=True)
args_parser.add_argument('--complex')

args = args_parser.parse_args()
print(args)

model_parser = Parser("model")
model_str = open(args.model, "r").read()
model = model_parser.parse(model_str).data

if args.method == "reduce":
    model.reduce_context()
    save_model(model, args.output)
elif args.method == "eliminate":
    model.eliminate_redundant()
    save_model(model, args.output)
else:
    complex_parser = Parser("rate_complex")
    complex = complex_parser.parse(args.complex).data.children[0]
    result = model.static_non_reachability(complex)

    f = open(args.output, "w")
    s = "can possibly" if result else "cannot"
    message = "The given agent\n\t{}\n{} be reached in the model.".format(complex, s)
    f.write(message)
    f.close()
