from src.dataframe.sample import take_sample
from unit_tests.conftest import build_dataframe


def test_pass_when_returns_sample_for_infinite_population_with_default_error_margin_of_3_percent():
    df = build_dataframe(10000)

    sample, description = take_sample(df)

    assert sample.index.is_monotonic_increasing

    assert len(sample) == 1067  # 1067 is the sample size for 95% confidence 3% margin of error
    assert "the following report has been produced using a sample" in description


def test_pass_when_returns_original_dataframe_when_smaller_than_sample_size():
    df = build_dataframe(100)

    sample, description = take_sample(df, margin_of_error_percent=0.01)

    assert len(sample) == 100
    assert description == None
