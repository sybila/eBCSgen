import argparse

from eBCSgen.Errors.ModelParsingError import ModelParsingError
from eBCSgen.Errors.UnspecifiedParsingError import UnspecifiedParsingError
from eBCSgen.Parsing.ParseBCSL import Parser

import numpy as np

def generate_ts():
    args_parser = argparse.ArgumentParser(description='Transition system generating')

    args_parser._action_groups.pop()
    required = args_parser.add_argument_group('required arguments')
    optional = args_parser.add_argument_group('optional arguments')

    required.add_argument('--model', type=str, required=True)
    required.add_argument('--output', type=str, required=True)
    required.add_argument('--direct', required=True)

    optional.add_argument('--max_time', type=float, default=np.inf)
    optional.add_argument('--max_size', type=float, default=np.inf)
    optional.add_argument('--bound', type=int, default=None)

    args = args_parser.parse_args()

    model_parser = Parser("model")
    model_str = open(args.model, "r").read()

    model = model_parser.parse(model_str)
    if model.success:
        if eval(args.direct):
            ts = model.data.generate_direct_transition_system(args.max_time,
                                                            args.max_size,
                                                            args.bound)
            ts.change_to_vector_backend()
        else:
            vm = model.data.to_vector_model(args.bound)
            ts = vm.generate_transition_system(None, args.max_time, args.max_size)
        ts.save_to_json(args.output, model.data.params)
    else:
        if "error" in model.data:
            raise UnspecifiedParsingError(model.data["error"])
        raise ModelParsingError(model.data, model_str)

if __name__ == '__main__':
    generate_ts()
