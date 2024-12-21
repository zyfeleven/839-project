import pytest

from sklearn.base import (
    BaseEstimator,
    RegressorMixin,
    TransformerMixin,
)
from sklearn.utils._tags import get_tags


class NoTagsEstimator:
    pass


class ClassifierEstimator:
    # This is to test whether not inheriting from mixins works.
    _estimator_type = "classifier"


class EmptyTransformer(TransformerMixin, BaseEstimator):
    pass


class EmptyRegressor(RegressorMixin, BaseEstimator):
    pass


@pytest.mark.filterwarnings("ignore:.*no __sklearn_tags__ attribute.*:FutureWarning")
@pytest.mark.parametrize(
    "estimator, value",
    [
        [NoTagsEstimator(), False],
        [ClassifierEstimator(), True],
        [EmptyTransformer(), False],
        [EmptyRegressor(), True],
        [BaseEstimator(), False],
    ],
)
def test_requires_y(estimator, value):
    assert get_tags(estimator).target_tags.required == value
