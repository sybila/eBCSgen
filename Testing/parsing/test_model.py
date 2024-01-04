import collections
import pytest

from eBCSgen.Core.Model import Model

from Testing.models.get_model_str import get_model_str
import Testing.objects_testing as objects


# inits

inits = collections.Counter({objects.c27: 2, objects.c28: 1})

# defs

defs = {'k1': 0.05, 'k2': 0.12}

model = Model({objects.r1, objects.r2, objects.r3}, inits, defs, set())
# model


model_str_1 = get_model_str("model1")

model_str_2 = get_model_str("model2")

model_with_comments_str = get_model_str("model_with_comments")

model_wrong_1 = get_model_str("model_wrong1")

model_wrong_2 = get_model_str("model_wrong2")

def test_parser():
    assert objects.model_parser.parse(model_str_1).data == model


def test_parser_errors():
    assert not objects.model_parser.parse(model_wrong_1).success

    assert not objects.model_parser.parse(model_wrong_2).success
        

def test_comments():
    model_with_comments = objects.model_parser.parse(model_with_comments_str).data
    model_without_comments = objects.model_parser.parse(model_str_2).data

    assert model_with_comments == model_without_comments