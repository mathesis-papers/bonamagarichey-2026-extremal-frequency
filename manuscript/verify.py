import argparse
from fractions import Fraction
from itertools import product
import json
from pathlib import Path


def automaton_counts(forbidden, maximum):
    size = len(forbidden)
    transitions = {}
    for state in range(size):
        for letter in "01":
            extended = forbidden[:state] + letter
            if extended.endswith(forbidden):
                transitions[state, letter] = None
            else:
                transitions[state, letter] = max(
                    length
                    for length in range(size)
                    if extended.endswith(forbidden[:length])
                )
    states = [(0, 0)] * size
    states[0] = (1, 0)
    result = [(1, 0)]
    for length in range(1, maximum + 1):
        next_states = [(0, 0)] * size
        for state, (count, ones) in enumerate(states):
            for letter in "01":
                target = transitions[state, letter]
                if target is not None:
                    old_count, old_ones = next_states[target]
                    next_states[target] = (
                        old_count + count,
                        old_ones + ones + count * int(letter),
                    )
        states = next_states
        result.append((sum(count for count, ones in states),
                       sum(ones for count, ones in states)))
    return result


def brute_counts(forbidden, length):
    words = ("".join(letters) for letters in product("01", repeat=length))
    count = 0
    ones = 0
    for word in words:
        if forbidden not in word:
            count += 1
            ones += word.count("1")
    return count, ones


def renewal_counts(block_maximum, maximum):
    inverse = [(1, 0)]
    for length in range(1, maximum + 1):
        terms = inverse[max(0, length - block_maximum):length]
        inverse.append((sum(count for count, ones in terms),
                        sum(count + ones for count, ones in terms)))
    constant_word = []
    edge_word = []
    for length in range(maximum + 1):
        terms = inverse[max(0, length - block_maximum + 1):length + 1]
        constant_word.append((sum(count for count, ones in terms),
                              sum(ones for count, ones in terms)))
        terms = inverse[:length + 1]
        edge_word.append((sum(count for count, ones in terms),
                          sum(ones for count, ones in terms)))
    return constant_word, edge_word


def root_interval(block_maximum, iterations=80):
    lower, upper = Fraction(0), Fraction(1)
    for step in range(iterations):
        middle = (lower + upper) / 2
        value = sum(middle ** exponent for exponent in range(1, block_maximum + 1))
        if value < 1:
            lower = middle
        else:
            upper = middle
    assert sum(lower ** exponent for exponent in range(1, block_maximum + 1)) < 1
    assert sum(upper ** exponent for exponent in range(1, block_maximum + 1)) >= 1
    denominator_lower = sum(exponent * lower ** exponent
                            for exponent in range(1, block_maximum + 1))
    denominator_upper = sum(exponent * upper ** exponent
                            for exponent in range(1, block_maximum + 1))
    return {
        "m": block_maximum,
        "root_lower": str(lower),
        "root_upper": str(upper),
        "frequency_lower": str(1 / denominator_upper),
        "frequency_upper": str(1 / denominator_lower),
    }


def alternating_counts(maximum):
    counts = []
    moments = []
    for length in range(maximum + 1):
        count = int(length == 0) + int(length == 2)
        moment = int(length == 2)
        if length >= 1:
            count += 2 * counts[length - 1]
            moment += 2 * moments[length - 1] + counts[length - 1]
        if length >= 2:
            count -= counts[length - 2]
            moment -= moments[length - 2] + counts[length - 2]
        if length >= 3:
            count += counts[length - 3]
            moment += moments[length - 3] + 2 * counts[length - 3]
        counts.append(count)
        moments.append(moment)
    return list(zip(counts, moments))


def alternating_interval(iterations=80):
    lower, upper = Fraction(1, 2), Fraction(1)
    polynomial = lambda value: 1 - 2 * value + value**2 - value**3
    for step in range(iterations):
        middle = (lower + upper) / 2
        if polynomial(middle) > 0:
            lower = middle
        else:
            upper = middle
    assert polynomial(lower) > 0 and polynomial(upper) < 0
    numerator_lower = 1 - upper + 2 * lower**2
    numerator_upper = 1 - lower + 2 * upper**2
    denominator_lower = 2 - 2 * upper + 3 * lower**2
    denominator_upper = 2 - 2 * lower + 3 * upper**2
    assert denominator_lower > 0
    frequency_lower = numerator_lower / denominator_upper
    frequency_upper = numerator_upper / denominator_lower
    assert Fraction(1, 2) < frequency_lower < frequency_upper < Fraction(2, 3)
    return {
        "word": "010",
        "root_polynomial": "1 - 2*t + t**2 - t**3",
        "root_lower": str(lower),
        "root_upper": str(upper),
        "frequency_lower": str(frequency_lower),
        "frequency_upper": str(frequency_upper),
    }


def alphabet_checks():
    compared = 0
    for alphabet_size in range(2, 6):
        for forbidden in range(alphabet_size):
            available = [symbol for symbol in range(alphabet_size) if symbol != forbidden]
            for length in range(1, 8):
                count = 0
                target_count = 0
                for word in product(available, repeat=length):
                    count += 1
                    target_count += word.count(0)
                assert count == (alphabet_size - 1)**length
                expected = 0 if forbidden == 0 else length * (alphabet_size - 1)**(length - 1)
                assert target_count == expected
                compared += 1
    return compared


def main():
    parser = argparse.ArgumentParser(description="Exact forbidden-word counting checks")
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    compared = 0
    for size in range(1, 5):
        for letters in product("01", repeat=size):
            forbidden = "".join(letters)
            counts = automaton_counts(forbidden, 12)
            for length in range(13):
                assert counts[length] == brute_counts(forbidden, length)
                compared += 1
    for length in range(1, 257):
        assert automaton_counts("0", length)[length] == (1, length)
        assert automaton_counts("1", length)[length] == (1, 0)
        expected = (length + 1, length * (length + 1) // 2)
        assert automaton_counts("10", length)[length] == expected
        assert automaton_counts("01", length)[length] == expected
    renewal_compared = 0
    for block_maximum in range(1, 9):
        constant_word, edge_word = renewal_counts(block_maximum, 100)
        assert constant_word == automaton_counts("0" * block_maximum, 100)
        assert edge_word == automaton_counts("1" + "0" * block_maximum, 100)
        assert edge_word == automaton_counts("0" * block_maximum + "1", 100)
        renewal_compared += 3 * 101
    counts_00 = automaton_counts("00", 100)
    counts_11 = automaton_counts("11", 100)
    for length, ((count_00, ones_00), (count_11, ones_11)) in enumerate(zip(counts_00, counts_11)):
        assert count_00 == count_11
        assert ones_00 + ones_11 == length * count_00
    intervals = [root_interval(block_maximum) for block_maximum in range(2, 9)]
    assert Fraction(intervals[0]["frequency_lower"]) > Fraction(1, 2)
    for earlier, later in zip(intervals, intervals[1:]):
        assert Fraction(earlier["frequency_lower"]) > Fraction(later["frequency_upper"])
    alternating = alternating_counts(256)
    assert alternating == automaton_counts("010", 256)
    complementary = automaton_counts("101", 256)
    for length, ((count, moment), (other_count, other_moment)) in enumerate(zip(alternating, complementary)):
        assert count == other_count and moment + other_moment == length * count
    alternating_certificate = alternating_interval()
    assert Fraction(alternating_certificate["frequency_upper"]) < Fraction(intervals[0]["frequency_lower"])
    three_word_values = {
        "000": (Fraction(intervals[1]["frequency_lower"]), Fraction(intervals[1]["frequency_upper"])),
        "001": (Fraction(intervals[0]["frequency_lower"]), Fraction(intervals[0]["frequency_upper"])),
        "010": (Fraction(alternating_certificate["frequency_lower"]), Fraction(alternating_certificate["frequency_upper"])),
        "100": (Fraction(intervals[0]["frequency_lower"]), Fraction(intervals[0]["frequency_upper"])),
    }
    for forbidden, (lower, upper) in list(three_word_values.items()):
        complement = "".join("1" if letter == "0" else "0" for letter in forbidden)
        three_word_values[complement] = (1 - upper, 1 - lower)
    winners = ["001", "100"]
    assert len(three_word_values) == 8
    for forbidden, (lower, upper) in three_word_values.items():
        if forbidden not in winners:
            assert upper < three_word_values["001"][0]
    result = {
        "status": "pass",
        "arithmetic": "integer counts and first moments; exact rational bisection",
        "brute_force": {
            "forbidden_lengths": [1, 2, 3, 4],
            "ambient_lengths": [0, 12],
            "count_moment_pairs_compared": compared,
        },
        "boundary_identities": {"ambient_lengths": [1, 256], "words": ["0", "1", "01", "10"]},
        "generating_functions": {
            "m_range": [1, 8],
            "ambient_lengths": [0, 100],
            "count_moment_pairs_compared": renewal_compared,
        },
        "complement_identity": {"words": ["00", "11"], "ambient_lengths": [0, 100]},
        "algebraic_intervals": intervals,
        "monotone_family_intervals": {"m_range": [2, 8], "strictly_decreasing": True},
        "alternating_generating_function": {
            "words": ["010", "101"], "ambient_lengths": [0, 256],
            "count_moment_pairs_compared": 514,
            "certificate": alternating_certificate,
        },
        "length_three_classification": {
            "maximizers": winners, "minimizers": ["011", "110"],
            "frequency_intervals": {word: [str(lower), str(upper)] for word, (lower, upper) in sorted(three_word_values.items())},
        },
        "alphabet_singletons": {
            "alphabet_sizes": [2, 5], "ambient_lengths": [1, 7],
            "count_moment_pairs_compared": alphabet_checks(),
        },
        "coverage": "Finite checks of the counting identities. Infinite-limit statements have the proofs in note.tex.",
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.output:
        arguments.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
