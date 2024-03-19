from src.conditional import is_digit_and_alpha


def test_pass_when_detects_one_digit_and_one_alpha_in_str():
    assert is_digit_and_alpha("1a")
    assert is_digit_and_alpha("a1")

    assert not is_digit_and_alpha("1")
    assert not is_digit_and_alpha("a")
    assert not is_digit_and_alpha("")
    assert not is_digit_and_alpha("!,/")
