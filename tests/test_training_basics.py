import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("sklearn")

from src.training_lab.digits_data import load_splits
from src.training_lab.digits_model import DigitsMLP


def test_model_output_shape() -> None:
    model = DigitsMLP()
    output = model(torch.zeros(4, 64))

    assert output.shape == (4, 10)

def test_splits_have_expected_dimensions() -> None:
    splits = load_splits()

    for x, y in splits.values():
        assert x.shape[1] == 64
        assert len(x) == len(y)
        assert x.min() >= 0
        assert x.max() <= 1