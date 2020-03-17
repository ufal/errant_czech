from difflib import SequenceMatcher
from pathlib import Path

import unidecode
from nltk.stem import LancasterStemmer

from . import merger
from .rosen_chyby import compare_words


# Load Hunspell word list
def load_word_list(path):
    with open(path) as word_list:
        return set([word.strip() for word in word_list])


# Classifier resources
base_dir = Path(__file__).resolve().parent
# Spacy
nlp = None
# Lancaster Stemmer
stemmer = LancasterStemmer()
# GB English word list (inc -ise and -ize)
spell = load_word_list(base_dir / "resources" / "morfflex-cz.2016-03-10.utf8.conll09.tab_uniq")
# Rare POS tags that make uninformative error categories
rare_pos = {"SYM", "X"}

inflected_tags = {"ADJ", "AUX", "PRON", "PROPN", "NOUN", "VERB", "NUM", "ADV"}

# Special auxiliaries in contractions.
aux_conts = {"ca": "can", "sha": "shall", "wo": "will"}
# Some dep labels that map to pos tags.
dep_map = {
    "acomp": "ADJ",
    "amod": "ADJ",
    "advmod": "ADV",
    "det": "DET",
    "prep": "PREP",
    "prt": "PART",
    "punct": "PUNCT"}


# Input: An Edit object
# Output: The same Edit object with an updated error type
def classify(edit, orig, cor):
    # Nothing to nothing is a detected but not corrected edit
    if not edit.o_toks and not edit.c_toks:
        edit.type = "UNK"
    # Missing
    elif not edit.o_toks and edit.c_toks:
        op = "M:"
        cat = get_one_sided_type(edit.c_toks)
        edit.type = op + cat
    # Unnecessary
    elif edit.o_toks and not edit.c_toks:
        op = "U:"
        cat = get_one_sided_type(edit.o_toks)
        edit.type = op + cat
    # Replacement and special cases
    else:
        # Same to same is a detected but not corrected edit
        if edit.o_str == edit.c_str:
            edit.type = "UNK"
        # Special: Ignore case change at the end of multi token edits
        # E.g. [Doctor -> The doctor], [, since -> . Since]
        # Classify the edit as if the last token wasn't there
        elif edit.o_toks[-1].lower == edit.c_toks[-1].lower and \
                (len(edit.o_toks) > 1 or len(edit.c_toks) > 1):
            # Store a copy of the full orig and cor toks
            all_o_toks = edit.o_toks[:]
            all_c_toks = edit.c_toks[:]
            # Truncate the instance toks for classification
            edit.o_toks = edit.o_toks[:-1]
            edit.c_toks = edit.c_toks[:-1]
            # Classify the truncated edit
            edit = classify(edit, orig, cor)
            # Restore the full orig and cor toks
            edit.o_toks = all_o_toks
            edit.c_toks = all_c_toks
        # Replacement
        else:
            op = "R:"
            cat = get_two_sided_type(edit.o_toks, edit.c_toks, orig, cor)
            print(cat)
            edit.type = op + cat
    return edit


# Input: Spacy tokens
# Output: A list of token, pos and dep tag strings
def get_edit_info(toks):
    str = []
    pos = []
    dep = []
    for tok in toks:
        str.append(tok.text)
        pos.append(tok.pos_)
        dep.append(tok.dep_)
    return str, pos, dep


# Input: Spacy tokens
# Output: An error type string based on input tokens from orig or cor
# When one side of the edit is null, we can only use the other side
def get_one_sided_type(toks):
    # Extract strings, pos tags and parse info from the toks
    str_list, pos_list, dep_list = get_edit_info(toks)

    print("one", toks, str_list, pos_list, dep_list)

    # byt vsechny mozne formy

    err_type = set()
    for tok in toks:
        if tok.lower_ == 'se' or tok.lower_ == 'si':
            err_type.add(':SE')

        if tok.lemma_.lower() == 'být':
            err_type.add(':BE')

    err_type = "".join(list(err_type))

    # POS-based tags. Ignores rare, uninformative categories
    if len(set(pos_list)) == 1 and pos_list[0] not in rare_pos:
        return pos_list[0] + err_type
    # More POS-based tags using special dependency labels
    if len(set(dep_list)) == 1 and dep_list[0] in dep_map.keys():
        return dep_map[dep_list[0]] + err_type
    # has gone => VERB, bych šel => VERB
    if set(pos_list) == {"AUX", "VERB"}:
        return "VERB" + err_type
    # Tricky cases
    else:
        return "OTHER" + err_type


# Input 1: Spacy orig tokens
# Input 2: Spacy cor tokens
# Output: An error type string based on orig AND cor
def get_two_sided_type(o_toks, c_toks, orig_toks, cor_toks):
    # Extract strings, pos tags and parse info from the toks as lists
    orig_str, orig_pos, orig_dep = get_edit_info(o_toks)
    cor_str, cor_pos, cor_dep = get_edit_info(c_toks)

    print("two", orig_str, orig_pos, orig_dep, "|", cor_str, cor_pos, cor_dep)

    # Diacritics
    if unidecode.unidecode(" ".join(orig_str)) == unidecode.unidecode(" ".join(cor_str)):
        return "DIACR"
    # Orthography; i.e. whitespace and/or case errors.
    if only_orth_change(orig_str, cor_str):
        orth_type = ''

        if "".join(orig_str) == "".join(cor_str):
            orth_type = ":WSPACE"
        elif " ".join(orig_str).lower() == " ".join(cor_str).lower():
            orth_type = ":CASING"
        return "ORTH" + orth_type
    # Word Order; only matches exact reordering.
    if exact_reordering(orig_str, cor_str):
        return "WO"
    # Word order with minor spelling errors
    if merger.is_transposition_compatible(orig_str, cor_str):
        return "WO:SPELL"

    # Other local changes (applicable only when there is a single word in source and target)
    if len(orig_str) == len(cor_str):
        rosen_err_types = compare_words(orig_str[0], cor_str[0])
        # filter out all unspecs
        rosen_err_types = [x for x in rosen_err_types.split('|') if 'unspec' not in x.lower()]

        # if there are multiple char-error types identified, remove all formSingCh from them
        if len(rosen_err_types) > 1:
            rosen_err_types = [x for x in rosen_err_types if 'formSingCh' not in x]

        if not rosen_err_types or len(rosen_err_types) != 1:
            rosen_err_types = ""
        else:
            rosen_err_types = ":{}".format(rosen_err_types[0])

    # 1:1 replacements (very common)
    if len(orig_str) == len(cor_str) == 1:

        # SPELLING AND INFLECTION
        # note that :INFL is for words that are inflected forms but contain a spelling error (thus original word is not in dictionary)
        # and :FORM is for inflected forms where the original word is a valid Czech word
        # in Czech we refer to inflection as to "ohýbání (ohebná slova)" and they can come from either "skloňování" or "časování"
        # as "časování" is applicable only to verbs and "skloňování" to rest of inflected_tags, we do not distinguish them any further

        # errors in VERB-ENDINGS (verb ends with i or y depending on the subject)
        if same_lemma(o_toks[0], c_toks[0]):
            if orig_pos == cor_pos and orig_pos[0] in inflected_tags:
                # psali x psaly
                if cor_pos[0] == 'VERB':
                    # if the only change is the last letter i vs y
                    if o_toks[0].text[:-1] == c_toks[0].text[:-1] and o_toks[0].text[-1].lower() in "iy" \
                            and c_toks[0].text[-1].lower() in "iy":
                        if 'nsubj' in [tok.dep_ for tok in cor_toks]:
                            return "VERB:FORM:vyjadreny_podmet_IY"
                        else:
                            return "VERB:FORM:nevyjadreny_podmet_IY"
                    # else:
                    #     if 'nsubj' in [tok.dep_ for tok in cor_toks]:
                    #         return "VERB:FORM:vyjadreny_podmer"
                    #     else:
                    #         return "VERB:FORM:nevyjadreny_podmer"
                return orig_pos[0] + ":FORM" + rosen_err_types
            # Unknown morphology; i.e. we cannot be more specific.
            else:
                return "MORPH" + rosen_err_types

        # SPELLING
        # Only check alphabetical strings on the original side
        # Spelling errors take precedence over POS errors; this rule is ordered
        if orig_str[0].isalpha():
            # Check a GB English dict for both orig and lower case.
            # E.g. "cat" is in the dict, but "Cat" is not.
            if orig_str[0] not in spell and orig_str[0].lower() not in spell and orig_str[0].isalpha():
                if same_lemma(o_toks[0], c_toks[0]):
                    if orig_pos == cor_pos and orig_pos[0] in inflected_tags:
                        return orig_pos[0] + ":INFL" + rosen_err_types
                    # Unknown morphology; i.e. we cannot be more specific.
                    else:
                        return "MORPH" + rosen_err_types

                # Use string similarity to detect true spelling errors.
                # TODO nechceme to udelat ala matching (tj. upravney weighted levensthein)
                char_ratio = SequenceMatcher(None, orig_str[0], cor_str[0]).ratio()
                # Ratio > 0.5 means both side share at least half the same chars.
                # WARNING: THIS IS AN APPROXIMATION.
                if char_ratio > 0.5:
                    return "SPELL" + rosen_err_types
                # If ratio is <= 0.5, the error is more complex e.g. tolk -> say
                else:
                    # If POS is the same, this takes precedence over spelling.
                    if orig_pos == cor_pos and \
                                    orig_pos[0] not in rare_pos:
                        return orig_pos[0]
                    # Tricky cases.
                    else:
                        return "OTHER" + rosen_err_types

        # INFLECTION
        if same_lemma(o_toks[0], c_toks[0]):
            if orig_pos == cor_pos and orig_pos[0] in inflected_tags:
                return orig_pos[0] + ":FORM" + rosen_err_types
            # Unknown morphology; i.e. we cannot be more specific.
            else:
                return "MORPH" + rosen_err_types

        # Derivational morphology.
        # just in case that lemmatizer "failed"
        if stemmer.stem(orig_str[0]) == stemmer.stem(cor_str[0]) and orig_pos[0] in inflected_tags and cor_pos[0] in inflected_tags:
            return "MORPH" + rosen_err_types

        # 3. GENERAL
        # POS-based tags. Some of these are context sensitive mispellings.
        if orig_pos == cor_pos and orig_pos[0] not in rare_pos:
            return orig_pos[0] + rosen_err_types
        # Some dep labels map to POS-based tags.
        if orig_dep == cor_dep and orig_dep[0] in dep_map.keys():
            return dep_map[orig_dep[0]] + rosen_err_types
        # Can use dep labels to resolve DET + PRON combinations.
        if set(orig_pos + cor_pos) == {"DET", "PRON"}:
            # DET cannot be a subject or object.
            if cor_dep[0] in {"nsubj", "nsubjpass", "dobj", "pobj"}:
                return "PRON" + rosen_err_types
            # "poss" indicates possessive determiner
            if cor_dep[0] == "poss":
                return "DET" + rosen_err_types
        # Tricky cases.
        else:
            return "OTHER" + rosen_err_types

    # Multi-token replacements (uncommon)
    # All same POS
    if len(set(orig_pos + cor_pos)) == 1:
        if orig_pos[0] not in rare_pos:
            return orig_pos[0]
    # All same special dep labels.
    if len(set(orig_dep + cor_dep)) == 1 and \
                    orig_dep[0] in dep_map.keys():
        return dep_map[orig_dep[0]]
    # Infinitives, gerunds, phrasal verbs.
    # by kopal (AUX VERB)
    # TODO on plaval (PRON VERB) -> on se koupal (PRON PRON VERB) - pridat se rucne

    # aux sel jsem (AUX) domu, bych (AUX)
    if set(orig_pos + cor_pos) == {"AUX", "VERB"}:
        # Final verbs with the same lemma are form; e.g. to eat -> eating
        if same_lemma(o_toks[-1], c_toks[-1]):
            return "VERB:FORM"
        # Remaining edits are often verb; e.g. to eat -> consuming, look at -> see
        else:
            return "VERB"
    # Tricky cases.
    else:
        return "OTHER"


# Input 1: A list of original token strings
# Input 2: A list of corrected token strings
# Output: Boolean; the difference between orig and cor is only whitespace or case
def only_orth_change(o_str, c_str):
    o_join = "".join(o_str).lower()
    c_join = "".join(c_str).lower()
    if o_join == c_join:
        return True
    return False


# Input 1: A list of original token strings
# Input 2: A list of corrected token strings
# Output: Boolean; the tokens are exactly the same but in a different order
def exact_reordering(o_str, c_str):
    # Sorting lets us keep duplicates.
    o_set = sorted([tok.lower() for tok in o_str])
    c_set = sorted([tok.lower() for tok in c_str])
    if o_set == c_set:
        return True
    return False


# Input 1: A spacy orig token
# Input 2: A spacy cor token
# Output: Boolean; the tokens have the same lemma
# Spacy only finds lemma for its predicted POS tag. Sometimes these are wrong,
# so we also consider alternative POS tags to improve chance of a match.
def same_lemma(o_tok, c_tok):
    if o_tok.lemma == c_tok.lemma:
        return True

    return False