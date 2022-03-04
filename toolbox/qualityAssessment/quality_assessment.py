"""
This script is directly inspired and adapted from a paper written by Pit Schneider
"Rerunning OCR: A Machine Learning Approach to Quality Assessment and Enhancement Prediction"
https://arxiv.org/abs/2110.01661
Original code can be found here: https://github.com/natliblux/nautilusocr/

This scripts aims to get a quality assessment for texts that were automatically transcribed.

Functions from source repository were adapted to better fit sale catalogue's specifities.
"""

import os
import unidecode
import re

HYPHENS = {'-', '⸗', '='}
VOWELS = ['a', 'e', 'i', 'o', 'u', 'y']
COMMON_LATIN_NAMES = ['AVGVSTVS', 'AUGVSTVS', 'LEVTVLVS', 'BRVTVS', 'LENTVLVS', 'DRVSVS', 'POPVLVSQVE', 'DIOCLETIANVS']
COMMON_ABBREVIATIONS = ['g.', 'gr.', 'd.']


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


def get_tokens(text: str):
    """
    Returns a tokens list from a raw text.
    Source code: https://github.com/natliblux/nautilusocr/blob/master/src/epr/features_epr.py
    """
    tokens = list()

    new_token = ''
    for c in text:
        if c == ' ' and len(new_token) > 0:
            tokens.append(new_token)
            new_token = ''
        elif c == '\n' and len(new_token) > 0:
            if new_token[-1] in HYPHENS:
                new_token = new_token[:-1]
            else:
                tokens.append(new_token)
                new_token = ''
        else:
            new_token += c
    if len(new_token) > 0:
        tokens.append(new_token)

    for i, token in enumerate(tokens):
        if not token[-1].isalpha():
            tokens[i] = token[:-1]
        if not token[0].isalpha():
            tokens[i] = token[1:]

    return tokens


def get_garbage_score(tokens: list):
    """
    Compute 'garbage score' from a tokens list.
    Code adapted from https://github.com/natliblux/nautilusocr/blob/master/src/epr/features_epr.py

    Rules were modified to better fit sale catalogues' specifities.
    """
    issues = 0

    if len(tokens) == 0:
        return 0

    for token in tokens:
        # We're looking for token with more than 21 char
        if len(token) > 21:
            # Adding a pattern for multiword expression (city names for example, widely used for French cities)
            if not re.search("[A-z]-[A-z]", token):
                issues += 1
                continue

        vowel_count = 0
        consonant_count = 0
        lower_case_count = 0
        upper_case_count = 0
        special_char_count = 0
        non_outer_special_chars = set()
        alpha = True
        last_char = None
        repetition_streak = 0
        vowel_streak = 0
        consonant_streak = 0
        go_to_next_token = False

        for i in range(0, len(token)):
            go_to_next_token = False
            char = token[i]

            # character normalisation - removing diacritics
            char = unidecode.unidecode(char)

            # collect token info
            if char.isalpha():
                if char.lower() in VOWELS:
                    vowel_count += 1
                    vowel_streak += 1
                    consonant_streak = 0
                else:
                    consonant_count += 1
                    consonant_streak += 1
                    vowel_streak = 0
                if char.isupper():
                    upper_case_count += 1
                else:
                    lower_case_count += 1
            elif char.isalnum():
                alpha = False
                vowel_streak = 0
                consonant_streak = 0
            else:
                special_char_count += 1
                alpha = False
                vowel_streak = 0
                consonant_streak = 0
                if i != 0 and i != len(token) - 1:
                    non_outer_special_chars.add(char)

            # Vowel streak was set at 3.
            # But it does not work for French ('oui', 'euil', 'eue', etc.)
            # Now set to strictly superior to 4, not equal or superior.
            # Warning : Roman numerals and latin words (not that many here)
            if vowel_streak > 4:
                issues += 1
                go_to_next_token = True
                break

            # rule 4
            if consonant_streak >= 6:
                # Adding a rule to check for century Roman numerals (XIXe, etc.)
                if not check_if_roman_numeral(token) and token not in COMMON_LATIN_NAMES:
                    issues += 1
                    go_to_next_token = True
                    break

            if last_char is not None and char == last_char:
                repetition_streak += 1

                # rule 2
                if repetition_streak > 3:
                    issues += 1
                    go_to_next_token = True
                    break
            else:
                repetition_streak = 0
            last_char = char

        if go_to_next_token:
            continue

        if alpha and vowel_count > 0 and consonant_count > 0:
            # rule 5
            if vowel_count * 8 < consonant_count:
                # Adding a rule to check for century Roman numerals (XIXe, etc.)
                if not check_if_roman_numeral(token):
                    issues += 1
                    continue
            # rule 5
            if consonant_count * 8 < vowel_count:
                issues += 1
                continue

        # rule 6
        # Adding a rule to check for century Roman numerals (XIXe, etc.)
        if lower_case_count > 0 and upper_case_count > lower_case_count:
            if token[-1] == 'e':
                if not check_if_roman_numeral(token[:-1]):
                    issues += 1
                    continue

        # rule 7
        # Adding a rule to avoid tokens beginning with "d'" or "l'"
        if upper_case_count > 0 and token[0].islower() and token[len(token) - 1].islower():
            if not token[0:2] == "d'" and not token[0:2] == "l'":
                issues += 1
                continue

        # rule 8
        # Adding a rule to avoid common abbreviations usually found in sales catalogues
        regular_chars = len(token) - special_char_count
        if special_char_count >= regular_chars and regular_chars > 0:
            if token not in COMMON_ABBREVIATIONS:
                issues += 1
                continue

        # rule 9
        if len(non_outer_special_chars) >= 2:
            issues += 1
            continue

    return issues / len(tokens)


file_num = 0
erroneous = 0
token_nb = []

for filename in os.listdir('./rawtxt'):
    file_num += 1
    file = os.path.join('./rawtxt', filename)
    if str(file).endswith('.rawtxt'):
        with open(file, 'r') as fh:
            txt = fh.read()
            clean_txt = txt.replace('\n', '')
            tokens = get_tokens(clean_txt)
            token_nb.append(len(tokens))

            if get_garbage_score(tokens) > 0.10:
                erroneous += 1
                print(f'{filename.split(".")[0]} \t {get_garbage_score(tokens)}')

print(f'min token: {min(token_nb)}')
print(f'max token: {max(token_nb)}')
print(f'Total files: {file_num}')
print(f'Total files with >10% garbage tokens: {erroneous}')
