# -*- coding: utf-8 -*-

import itertools
from itertools import combinations, groupby
from re import sub
from string import punctuation

import numpy as np
import spacy.parts_of_speech as POS
from weighted_levenshtein import lev
from typing import List

from errant.edit import Edit


def get_substitution_matrix():
    # difflib.SequenceMatcher does not support weighting
    # weighted_levensthein does but does not support diacritics
    # -> map all characters with diacritics to ASCII non-used 1-31
    # -> also use chr(127) (~del) for all other non-ascii characters (foreign local)
    non_ascii_chars = ["á", "č", "ď", "é", "ě", "í", "ň", "ó", "ř", "š", "ť", "ú", "ů", "ý", "ž"]
    non_ascii_chars += [c.upper() for c in non_ascii_chars]

    diacritization_stripping_map = {
        "á": "a",
        "č": "c",
        "ď": "d",
        "é": "e",
        "ě": "e",
        "í": "i",
        "ň": "n",
        "ó": "o",
        "ř": "r",
        "š": "s",
        "ť": "t",
        "ú": "u",
        "ů": "u",
        "ý": "y",
        "ž": "z"
    }
    diacritization_stripping_map.update({c.upper(): u.upper() for c, u in diacritization_stripping_map.items()})

    map = {}
    for i in range(128):
        if i < 1 or i > 30:
            map[i] = chr(i)
        else:
            map[i] = non_ascii_chars[i - 1]

    substitute_costs = np.ones((128, 128), dtype=np.float64)

    for i in range(128):
        for j in range(128):
            if i == j:
                substitute_costs[i, j] = 0
            # lower are same
            elif map[i].lower() == map[j].lower():
                substitute_costs[i, j] = 0.1
            # when diacritics is stripped and they are same
            elif (map[i] in diacritization_stripping_map and diacritization_stripping_map[map[i]] == map[j]) or (
                            map[j] in diacritization_stripping_map and diacritization_stripping_map[map[j]] == map[i]):
                substitute_costs[i, j] = 0.2
            # case of é instead of ě, ů and ú
            elif map[i] in diacritization_stripping_map and map[j] in diacritization_stripping_map and (
                        diacritization_stripping_map[map[i]] == diacritization_stripping_map[map[j]]):
                substitute_costs[i, j] = 0.3
            elif (map[i] in {"i", "í", "y", "ý"} and map[j] in {"i", "í", "y", "ý"}):
                substitute_costs[i, j] = 0.3
            else:
                substitute_costs[i, j] = 1
    return substitute_costs, diacritization_stripping_map, non_ascii_chars


# Merger resources
open_pos = {POS.ADJ, POS.ADV, POS.NOUN, POS.VERB}
substitute_costs, diacritization_stripping_map, non_ascii_chars = get_substitution_matrix()


# Input: An Alignment object
# Output: A list of Edit objects
def get_rule_edits(alignment):
    edits = []
    # Split alignment into groups of M, T and rest. (T has a number after it)
    for op, group in groupby(alignment.align_seq,
                             lambda x: x[0][0] if x[0][0] in {"M", "T"} else False):
        group = list(group)
        # Ignore M
        if op == "M":
            continue
        # T is always split
        elif op == "T":
            for seq in group:
                edits.append(Edit(alignment.orig, alignment.cor, seq[1:]))
        # Process D, I and S subsequence
        else:
            processed = process_seq(group, alignment)
            # Turn the processed sequence into edits
            for seq in processed:
                edits.append(Edit(alignment.orig, alignment.cor, seq[1:]))
    return edits


# Input 1: A sequence of adjacent D, I and/or S alignments
# Input 2: An Alignment object
# Output: A sequence of merged/split alignments
def process_seq(seq, alignment):
    # Return single alignments
    if len(seq) <= 1: return seq
    # Get the ops for the whole sequence
    ops = [op[0] for op in seq]
    # Merge all D xor I ops. (95% of human multi-token edits contain S).
    if set(ops) == {"D"} or set(ops) == {"I"}: return merge_edits(seq)

    content = False  # True if edit includes a content word
    # Get indices of all start-end combinations in the seq: 012 = 01, 02, 12
    combos = list(combinations(range(0, len(seq)), 2))
    # Sort them starting with largest spans first
    combos.sort(key=lambda x: x[1] - x[0], reverse=True)
    # Loop through combos
    for start, end in combos:
        # Ignore ranges that do NOT contain a substitution.
        if "S" not in ops[start:end + 1]: continue
        # Get the tokens in orig and cor. They will now never be empty.
        o = alignment.orig[seq[start][1]:seq[end][2]]
        c = alignment.cor[seq[start][3]:seq[end][4]]
        # Case changes
        if o[-1].lower == c[-1].lower:
            # Merge first token I or D: [Cat -> The big cat]
            if start == 0 and ((len(o) == 1 and c[0].text[0].isupper()) or \
                    (len(c) == 1 and o[0].text[0].isupper())):
                return merge_edits(seq[start:end + 1]) + \
                       process_seq(seq[end + 1:], alignment)
            # Merge with previous punctuation: [, we -> . We], [we -> . We]
            if (len(o) > 1 and is_punct(o[-2])) or \
                    (len(c) > 1 and is_punct(c[-2])):
                return process_seq(seq[:end - 1], alignment) + \
                       merge_edits(seq[end - 1:end + 1]) + \
                       process_seq(seq[end + 1:], alignment)
        # Merge whitespace/hyphens: [acat -> a cat], [sub - way -> subway]
        s_str = sub("['-]", "", "".join([tok.lower_ for tok in o]))
        t_str = sub("['-]", "", "".join([tok.lower_ for tok in c]))
        if s_str == t_str:
            return process_seq(seq[:start], alignment) + \
                   merge_edits(seq[start:end + 1]) + \
                   process_seq(seq[end + 1:], alignment)
        # Merge same POS or infinitive/phrasal verbs:
        # [to eat -> eating], [watch -> look at]
        pos_set = set([tok.pos for tok in o] + [tok.pos for tok in c])
        # print(pos_set, s_str, t_str)
        if (len(pos_set) == 1 and len(o) != len(c)) or \
                        pos_set == {POS.PART, POS.VERB}:
            print('pos')
            return process_seq(seq[:start], alignment) + \
                   merge_edits(seq[start:end + 1]) + \
                   process_seq(seq[end + 1:], alignment)
        # Split rules take effect when we get to smallest chunks
        if end - start < 2:
            # Split adjacent substitutions
            if len(o) == len(c) == 2:
                return process_seq(seq[:start + 1], alignment) + \
                       process_seq(seq[start + 1:], alignment)
            # Split similar substitutions at sequence boundaries
            if (ops[start] == "S" and char_cost(o[0], c[0]) < 0.25) or \
                    (ops[end] == "S" and char_cost(o[-1], c[-1]) < 0.25):
                return process_seq(seq[:start + 1], alignment) + \
                       process_seq(seq[start + 1:], alignment)
            # Split final determiners
            if end == len(seq) - 1 and ((ops[-1] in {"D", "S"} and \
                                                     o[-1].pos == POS.DET) or (ops[-1] in {"I", "S"} and \
                                                                                           c[-1].pos == POS.DET)):
                print(o, c)
                return process_seq(seq[:-1], alignment) + [seq[-1]]
        # Set content word flag
        if not pos_set.isdisjoint(open_pos):
            content = True
    # Merge sequences that contain content words
    if content:
        return merge_edits(seq)
    else:
        return seq


# Check whether token is punctuation
def is_punct(token):
    return token.pos == POS.PUNCT or token.text in punctuation


def is_transposition_compatible(source_tokens:List[str], corrected_tokens:List[str]):
    if len(source_tokens) != len(corrected_tokens):
        return False

    transpose_len = len(source_tokens)
    if transpose_len > 5:
        # if length of the potential transposition is too big, check only for exact lower-cased reordering (i.e. no spelling allowed)
        return sorted([s.lower() for s in source_tokens]) == sorted([c.lower() for c in corrected_tokens])

    # construct all possible valid permutations (permutation is not valid when the first token maps to first token or the last token maps to last token)
    permutations = [perm for perm in itertools.permutations(range(transpose_len)) if perm[0] != 0 and perm[transpose_len - 1] != transpose_len - 1]

    # compute char_costs of transforming each source token into each target token
    char_costs = np.zeros((transpose_len, transpose_len), dtype=np.float32)
    for i, source_token in enumerate(source_tokens):
        for j, corrected_token in enumerate(corrected_tokens):
            char_costs[i,j] = char_cost(source_token, corrected_token)

    for perm in permutations:
        if all([char_costs[i,p] < 0.25 for i,p in enumerate(perm)]):
            return True

    return False

# Calculate the cost of character alignment; i.e. char similarity
def char_cost(a, b):
    def to_ascii(text):
        res = ""
        for t in text:
            if ord(t) < 128:
                res += t
            elif t in non_ascii_chars:  # if t is a character with diacritics
                res += chr(non_ascii_chars.index(t) + 1)
            else:
                res += chr(127)  # Unknown (non-ascii nor czech letter with diacritics)

        return res

    lemma_cost = 0
    # TODO napad se stemmerem (lidech x lidi je podobne, ale tezke bez stemmeru)
    return 2 * lev(to_ascii(str(a)), to_ascii(str(b)), substitute_costs=substitute_costs) / (len(str(a)) + len(str(b)))


# Merge the input alignment sequence to a single edit span
def merge_edits(seq):
    if seq:
        return [("X", seq[0][1], seq[-1][2], seq[0][3], seq[-1][4])]
    else:
        return seq
