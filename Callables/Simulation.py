import sys, os
import argparse

# this add to path eBCSgen home dir, so it can be called from anywhere
sys.path.append(os.path.split(sys.path[0])[0])

from Parsing.ParseBCSL import Parser
from Errors.ModelParsingError import ModelParsingError
from Errors.UnspecifiedParsingError import UnspecifiedParsingError

"""
usage: Simulation.py [-h] --model MODEL --output OUTPUT --deterministic
                     DETERMINISTIC --runs RUNS --max_time MAX_TIME
                     [--volume VOLUME]

Simulation

arguments:
  --model MODEL
  --output OUTPUT
  --deterministic DETERMINISTIC
  --runs RUNS
  --max_time MAX_TIME

optional arguments:
  -h, --help            show this help message and exit
  --volume VOLUME
"""

args_parser = argparse.ArgumentParser(description='Simulation')
args_parser.add_argument('--model', type=str, required=True)
args_parser.add_argument('--output', type=str, required=True)
args_parser.add_argument('--deterministic', required=True)
args_parser.add_argument('--runs', type=int, required=True)
args_parser.add_argument('--max_time', type=float, required=True)
args_parser.add_argument('--volume', type=float)
args_parser.add_argument('--step', type=float)

args = args_parser.parse_args()

model_parser = Parser("model")
model_str = open(args.model, "r").read()

model = model_parser.parse(model_str)

if model.success:
    vm = model.data.to_vector_model()
    if eval(args.deterministic):
        df = vm.deterministic_simulation(args.max_time, args.volume, args.step)
    else:
        df = vm.stochastic_simulation(args.max_time, args.runs)

    df.to_csv(args.output, index=None, header=True)
else:
    if "error" in model.data:
        raise UnspecifiedParsingError(model.data["error"])
    raise ModelParsingError(model.data, model_str)
