def is_digit_and_alpha(string: str):
    """Check if the given string contains both digits and letters."""
    return any(char.isdigit() for char in string) and any(char.isalpha() for char in string)
