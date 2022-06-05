import logging
import json
import os
import traceback
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import setriq
from pydantic import BaseModel

DEFAULT_METRIC_SPEC = os.environ.get("DEFAULT_METRIC_SPEC")


# ----- Helper Functions --------------------------------------------------------------------------------------------- #
def read_json(path: str) -> dict:
    txt = Path(path).read_text()
    obj = json.loads(txt)
    return obj


def init_sub_mat(spec: dict):
    name = spec["id"]
    param = spec.get("param")

    module = getattr(setriq, name)
    if name.startswith("BLOSUM"):
        return module
    return module(**param)


def init_metric(spec: dict):
    name = spec["id"]
    param = spec.get("param", {})
    sub_mat_spec = param.get("substitution_matrix")
    if sub_mat_spec:
        param["substitution_matrix"] = init_sub_mat(sub_mat_spec)

    metric = getattr(setriq, name)(**param)
    return metric


# ----- Error Handling ----------------------------------------------------------------------------------------------- #
def catch_and_log_errors(fn):
    @wraps(fn)
    def _fn(*args, **kwargs):
        try:
            out = fn(*args, **kwargs)
            return out
        except Exception as ex:
            logging.error(f"Error type: {type(ex)}")
            logging.error(f"Error value: {repr(ex)}")
            traceback.print_tb(ex.__traceback__)
            raise ex

    return _fn


# ----- Typing ------------------------------------------------------------------------------------------------------- #
class SubstitutionMatrixSpec(BaseModel):
    id: str
    param: Optional[dict]


class MetricSpec(BaseModel):
    id: str
    param: Optional[Dict[str, Union[Any, SubstitutionMatrixSpec]]]


class Payload(BaseModel):
    sequences: List[str]
    spec: Optional[MetricSpec]


class Response(BaseModel):
    distances: List[float]


# ----- Seldon Service ----------------------------------------------------------------------------------------------- #
class SetriqService:
    def __init__(self):
        self.default_metric = None

    @catch_and_log_errors
    def predict_raw(self, msg: Payload) -> Response:
        payload = dict(msg)
        metric_spec = payload.get("spec")
        if metric_spec:
            metric = init_metric(metric_spec)
        else:
            metric = self.default_metric
        sequences = payload.get("sequences", [])
        distances = metric(sequences)
        response = {"distances": distances}
        return response

    @catch_and_log_errors
    def load(self):
        default_metric_spec = read_json(DEFAULT_METRIC_SPEC)
        self.default_metric = init_metric(default_metric_spec)
