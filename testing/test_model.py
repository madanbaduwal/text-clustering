# To run this
import os
import sys

import numpy as np
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.features.build_features import create_features_for_one_student
from src.models.predict_model import (
    predicted_in_dummy_features,
    predicted_for_one_student,
    prediction_for_all_students_and_dump_into_mongoserver,
)


# Feature cration test
def test_create_features_for_one_student():

    features, log_features = create_features_for_one_student(
        ("5f7edc51c640e300428209f1", "6061aded16fbc000935bc325"),
    )
    features = features.iloc[:, 3:7].copy()
    features = features.to_numpy()
    assert features == pytest.approx(np.array([[0.962963, 1, 1, 1]]))


# Model prediction test
def test_predicted_in_dummy_features():
    pred_cluster, pred_class = predicted_in_dummy_features([0, 0, 0, 0])
    assert pred_class == "Red"


def test_predicted_in_dummy_features():
    pred_cluster, pred_class = predicted_in_dummy_features([1, 1, 1, 1])
    assert pred_class == "Green"


def test_predicted_for_one_student():

    features, log_features, pred_cluster, pred_class = predicted_for_one_student(
        "5f7edc51c640e300428209f1", "6061aded16fbc000935bc325",
    )
    assert pred_class == "Green"
