import sys, os
import argparse
import numpy as np

# this add to path eBCSgen home dir, so it can be called from anywhere
sys.path.append(os.path.split(sys.path[0])[0])

from Parsing.ParseBCSL import Parser, load_TS_from_json

"""
usage: GenerateTS.py [-h] --model MODEL --output OUTPUT [--bound BOUND]
                     [--transition_file TRANSITION_FILE] [--max_time MAX_TIME]
                     [--max_size MAX_SIZE]

Transition system generating

arguments
  --model MODEL
  --output OUTPUT

optional arguments:
  -h, --help            show this help message and exit
  --bound BOUND
  --transition_file TRANSITION_FILE
  --max_time MAX_TIME
  --max_size MAX_SIZE

"""

args_parser = argparse.ArgumentParser(description='Transition system generating')
args_parser.add_argument('--model', type=str, required=True)
args_parser.add_argument('--output', type=str, required=True)
args_parser.add_argument('--bound', type=int)
args_parser.add_argument('--transition_file')
args_parser.add_argument('--max_time', type=float, default=np.inf)
args_parser.add_argument('--max_size', type=float, default=np.inf)

args = args_parser.parse_args()

model_parser = Parser("model")
model_str = open(args.model, "r").read()

model = model_parser.parse(model_str).data

# this is different in new version
model.bound = args.bound  # this remove
vm = model.to_vector_model()  # args.bound)

if args.transition_file:
    ts = load_TS_from_json(args.transition_file)
else:
    ts = None

ts = vm.generate_transition_system(ts, args.max_time, args.max_size)
ts.save_to_json(args.output)
