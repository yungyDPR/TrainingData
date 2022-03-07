# Function found on https://stackoverflow.com/questions/20973546/check-if-an-input-is-a-valid-roman-numeral
# Written by @praveen
def check_if_roman_numeral(numeral: str):
    """Controls that the input only contains valid roman numerals"""
    numeral = numeral.upper()
    valid_roman_numerals = ["M", "D", "C", "L", "X", "V", "I", "(", ")"]
    valid = True
    for letters in numeral:
        if letters not in valid_roman_numerals:
            valid = False
            break
    return valid
