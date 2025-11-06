# Using the python-Levenshtein library is much faster than
# a pure python implementation, which is good for responsiveness.
from Levenshtein import distance as lev_distance


def get_levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculates the Levenshtein distance between two strings.
    A wrapper for the library function.
    """
    return lev_distance(s1, s2)


def strings_are_similar(s1: str, s2: str, max_distance: int = 2) -> bool:
    """
    Checks if two strings are similar within a given Levenshtein distance.
    Case-insensitive.
    """
    s1_clean = s1.strip().lower()
    s2_clean = s2.strip().lower()

    # Also check for direct substring, as "warnsdorff's rule" vs "warnsdorff"
    if s1_clean in s2_clean or s2_clean in s1_clean:
        return True

    return get_levenshtein_distance(s1_clean, s2_clean) <= max_distance
