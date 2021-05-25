# this is a refactored version of original Perl script by Alexandr Rosen
# see http://utkl.ff.cuni.cz/~rosen/public/SeznamAutoChybR0R1.html for information on error types
import math
import re


def list_to_dict(l):
    # l = [1,2,3,4] -> {1:2, 3:4} # even items are keys, odd items are values
    return dict(zip(l[::2], l[1::2]))


# Deklarace "lingvistických" proměnných / hashů
pair_voiced_voiceless = list_to_dict(
    ["b", "p", "B", "P", "d", "t", "D", "T", "ď", "ť", "Ď", "Ť", "g", "k", "G", "K", "z", "s", "Z", "S", "ž", "š", "Ž", "Š", "v", "f", "V",
     "F", "h", "ch", "H", "Ch"])
pair_voiceless_voiced = list_to_dict(
    ["p", "b", "P", "B", "t", "d", "T", "D", "ť", "ď", "Ť", "Ď", "k", "g", "K", "G", "s", "z", "S", "Z", "š", "ž", "Š", "Ž", "f", "v", "F",
     "V", "ch", "h", "Ch", "H", "CH", "H"])

list_vocals = ["a", "á", "e", "ě", "é", "i", "é", "o", "ó", "u", "ú", "ů", "y", "ý", "A", "Á", "E", "Ě", "É", "I", "Í", "O", "Ó", "U", "Ů",
               "Ú", "Y", "Ý"]
list_consonnants = ["b", "B", "c", "C", "č", "Č", "d", "D", "ď", "Ď", "f", "F", "g", "G", "h", "H", "ch", "Ch", "j", "J", "k", "K", "l",
                    "L", "m", "M", "n", "N", "ň", "Ň", "p", "P", "q", "Q", "r", "R", "ř", "Ř", "s", "S", "š", "Š", "t", "Ť", "v", "V", "w",
                    "W", "x", "X", "z", "Z", "ž", "Ž"]
list_voiced = ["b", "B", "d", "D", "ď", "Ď", "g", "G", "v", "V", "z", "Z", "ž", "Ž", "h", "H"]
list_voiceless = ["p", "P", "t", "T", "ť", "Ť", "k", "K", "s", "S", "š", "Š", "c", "C", "č", "Č", "f", "F", "ch", "Ch"]

pair_shackem_bezhacku = list_to_dict(
    ["č", "c", "Č", "C", "ď", "d", "Ď", "D", "ě", "e", "Ě", "E", "ľ", "l", "Ľ", "L", "ň", "n", "Ň", "N", "ř", "r", "Ř", "R", "š", "s", "Š",
     "S", "ť", "t", "Ť", "T", "ž", "z", "Ž", "Z"])
pair_bezhacku_shackem = list_to_dict(
    ["c", "č", "C", "Č", "d", "ď", "D", "Ď", "e", "ě", "E", "Ě", "l", "ľ", "L", "Ľ", "n", "ň", "N", "Ň", "r", "ř", "R", "Ř", "s", "š", "S",
     "Š", "t", "ť", "T", "Ť", "z", "ž", "Z", "Ž"])
pair_detene = list_to_dict(
    ["ďe", "dě", "ťe", "tě", "ňe", "ně", "ďi", "di", "ťi", "ti", "ňi", "ni", "ďí", "dí", "ťí", "tí", "ňí", "ní", "Ďe", "Dě", "Ťe", "Tě",
     "Ňe", "Ně", "Ďi", "Di", "Ťi", "Ti", "Ňi", "Ni", "Ďí", "Dí", "Ťí", "Tí", "Ňí", "Ní"])
pair_palat = list_to_dict(
    ["ke", "ce", "he", "ze", "ge", "ze", "che", "še", "kě", "ce", "hě", "ze", "gě", "ze", "chě", "še", "ki", "ci", "hi", "zi", "gi", "zi",
     "chi", "ši", "kí", "cí", "hí", "zí", "gí", "zí", "chí", "ší"])
pair_long_short_vowel = list_to_dict(
    ["á", "a", "Á", "A", "é", "e", "É", "E", "í", "i", "Í", "I", "ó", "o", "Ó", "O", "ů", "u", "Ů", "U", "ú", "u", "Ú", "U", "ý", "y", "Ý",
     "Y"])
pair_lc_uc = list_to_dict(
    ["a", "A", "á", "Á", "b", "B", "c", "C", "č", "Č", "d", "D", "ď", "Ď", "e", "E", "é", "É", "f", "F", "g", "G", "h", "H", "ch", "Ch",
     "i", "I", "í", "Í", "j", "J", "k", "K", "l", "L", "m", "M", "n", "N", "ň", "Ň", "o", "O", "ó", "Ó", "p", "P", "q", "Q", "r", "R", "ř",
     "Ř", "s", "S", "š", "Š", "t", "T", "ť", "Ť", "u", "U", "ú", "Ú", "ů", "Ů", "v", "V", "w", "W", "x", "X", "y", "Y", "ý", "Ý", "z", "Z",
     "ž", "Ž"])

list_of_prefixes = ["arci", "bez", "beze", "dia", "do", "ex", "infra", "mezi", "místo", "na", "ná", "nad", "nade", "ne", "nej", "o", "ob",
                    "obe", "od", "ode", "pa", "para", "po", "pod", "pode", "popo", "pra", "proti", "proto", "pře", "před", "přede", "přes",
                    "přese", "při", "pří", "pseudo", "roz", "roze", "s", "se", "sou", "spolu", "u", "ú", "v", "ve", "vele", "vy", "vý",
                    "vz", "vze", "z", "za", "zá", "ze"]
list_of_prep_forms = ["během", "bez", "beze", "blízko", "dík", "díky", "dle", "do", "doprostřed", "dovnitř", "k", "ke", "kol", "kolem",
                      "kontra", "krom", "kromě", "ku", "kvůli", "mezi", "mimo", "místo", "na", "nad", "nade", "namísto", "napospas",
                      "naproti", "napříč", "navzdory", "nedaleko", "o", "ob", "od", "ode", "ohledně", "okolo", "oproti", "po", "poblíž",
                      "pod", "pode", "podél", "podle", "pomocí", "prostřednictvím", "proti", "před", "přede", "přes", "přese", "při", "s",
                      "se", "skrz", "skrze", "u", "uprostřed", "uvnitř", "v", "včetně", "ve", "vedle", "versus", "vně", "vod", "vstříc",
                      "vůči", "vyjma", "vzdor", "z", "za", "ze", "zevnitř", "zkraje", "zpod", "zpoza"]


# / Konec deklarace lingv. proměnných

# *******************************************************************
# Podprogram pro srovnání dvou (neidentických) znaků, vč. "ch" (jeden znak), popř. dvojice znaků (2x2).
def compare_single_characters(w_char, a_char, w1_char, a1_char):
    report_error_type = 'Unspec'
    report_error_char = False

    # print(w_char, a_char, w1_char, a1_char)

    if (re.search(r'(^[ďňťgkhĎŤŇGKHZCČŠzcčš])|(^[Cc]h$)', w_char) and re.search(r'^[eěií]$', w1_char)):
        w_pair = w_char + w1_char
        a_pair = a_char + a1_char
        # Ďe / Dě
        if ((w_pair in pair_detene) and (pair_detene[w_pair] == a_pair)):
            report_error_type = 'formDtn'
            report_error_char = 'DD'

        # Palatalizace (chě/še che/še)
        elif (w_pair in pair_palat) and (pair_palat[w_pair] == a_pair):
            report_error_type = 'formPalat0'
            report_error_char = 'PP'
        # Palatalizace (??? ze/ge ???)
        elif (a_pair in pair_palat) and (pair_palat[a_pair] == w_pair):
            report_error_type = 'formPalat1'
            report_error_char = 'PP'

    if not report_error_char:
        # Znělost (znělá R0 / neznělá R1)
        if ((w_char in pair_voiced_voiceless) and (pair_voiced_voiceless[w_char] == a_char)) or ((a_char == 'CH') and (w_char == 'H')):
            report_error_char = 'Z'
            if w1_char in list_voiced:
                report_error_type = 'formVoiced1'  # Po chybně znělém znaku následuje znělý (spodoba znělosti).
            elif a1_char == '$':
                report_error_type = 'formVoicedFin1'  # Chybně znělá hláska na konci slova.
            else:
                report_error_type = 'formVoiced'

        # Znělost (neznělá R0 / znělá R1)
        elif ((w_char in pair_voiceless_voiced and pair_voiceless_voiced[w_char] == a_char)) or ((w_char == 'CH') and (a_char == 'H')):
            report_error_char = 'K'
            if w1_char in list_voiceless:  # Po chybně neznělém znaku následuje neznělý (spodoba znělosti).
                report_error_type = 'formVoiced0'
            elif w1_char == '$':
                report_error_type = 'formVoicedFin0'  # Chybně neznělá hláska na konci slova.
            else:
                report_error_type = 'formVoiced'

        # Diakritika - háček: (háček navíc)
        elif (w_char in pair_shackem_bezhacku) and (pair_shackem_bezhacku[w_char] == a_char):
            report_error_char = 'K'
            report_error_type = 'formCaron1'

        # Diakritika - háček: (háček chybí)
        elif (a_char in pair_shackem_bezhacku) and (pair_shackem_bezhacku[a_char] == w_char):
            report_error_char = 'K'
            report_error_type = 'formCaron0'

        # Diakritika - kvantita: (délka navíc)
        elif (w_char in pair_long_short_vowel) and (pair_long_short_vowel[w_char] == a_char):
            report_error_char = 'I'
            report_error_type = 'formQuant1'

        # Diakritika - kvantita: (délka chybí)
        elif (a_char in pair_long_short_vowel) and (pair_long_short_vowel[a_char] == w_char):
            report_error_char = 'I'
            report_error_type = 'formQuant0'

        # Velká/malá písmena: (zbytečné velké písmeno)
        elif (a_char in pair_lc_uc) and pair_lc_uc[a_char] == w_char:
            report_error_char = 'V'
            report_error_type = 'formCap1'

        # Velká/malá písmena: (chybí velké písmeno)
        elif (w_char in pair_lc_uc) and pair_lc_uc[w_char] == a_char:
            report_error_char = 'V'
            report_error_type = 'formCap0'

        # K / C mimo palatalizaci (ta je výše)
        elif (w_char.lower() == "k") and (a_char.lower() == "c"):
            report_error_char = 'k'
            report_error_type = 'formCK1'
        elif (w_char.lower() == "c") and (a_char.lower() == "k"):
            report_error_char = 'k'
            report_error_type = 'formCK0'
        # G / H
        elif (w_char.lower() == "h") and (a_char.lower() == "g"):
            report_error_char = 'g'
            report_error_type = 'formGH1'
        elif (w_char.lower() == "g") and (a_char.lower() == "h"):
            report_error_char = 'g'
            report_error_type = 'formGH0'
        # J / Y
        elif (w_char.lower() == "j") and (a_char.lower() == "y"):
            # TODO nema tady byt taky y???
            report_error_char = 'k'
            report_error_type = 'formYJ1'
        elif (w_char.lower() == "y") and (a_char.lower() == "j"):
            report_error_char = 'y'
            report_error_type = 'formYJ0'
        # ú/ů
        elif ((w_char.lower() == "ú") and (a_char.lower() == "ů")) or ((w_char.lower() == "ů") and (a_char.lower() == "ú")):
            report_error_char = 'U'
            report_error_type = 'formDiaU'
            if (w_char in ["Ú", "Ů"]) and (a_char in ["ú", "ů"]):
                report_error_type += '+formCap1'
            elif (a_char in ["Ú", "Ů"]) and (w_char in ["ú", "ů"]):
                report_error_type += '+formCap0'

        elif ((w_char.lower() == "ě") and (a_char.lower() == "é")) or ((w_char.lower() == "é") and (a_char.lower() == "ě")):
            report_error_char = 'E'
            report_error_type = 'formDiaE'
            if (w_char in ["Ě", "É"]) and (a_char in ["ě", "é"]):
                report_error_type += '+formCap1'
            elif (a_char in ["Ě", "É"]) and (w_char in ["ě", "é"]):
                report_error_type += '+formCap0'

        # i/y
        elif ((w_char.lower() == "i") and (a_char.lower() == "y")) or ((w_char.lower() == "í") and (a_char.lower() == "ý")):
            report_error_char = 'Y'
            report_error_type = 'formY0'

        # y/i
        elif ((w_char.lower() == "y") and (a_char.lower() == "i")) or ((w_char.lower() == "ý") and (a_char.lower() == "í")):
            report_error_char = 'Y'
            report_error_type = 'formY1'

        # ý/i,í/y...
        elif ((w_char in ["y", "ý", "Y", "Ý"]) and (a_char in ["i", "í", "I", "Í"])) or (
                    (w_char in ["i", "í", "I", "Í"]) and (a_char in ["y", "ý", "Y", "Ý"])):
            report_error_char = 'Y'
            if w_char in ["y", "ý", "Y", "Ý"]:
                report_error_type = 'formY1'
            else:
                report_error_type = 'formY0'
            if w_char in ['í', 'ý', 'Í', 'Ý']:
                report_error_type += '+formQuant1'
            else:
                report_error_type += '+formQuant0'

        if (report_error_char == 'Y') and (((w_char in ['I', 'Í', 'Y', 'Ý']) and (a_char in ['y', 'ý', 'i', 'í'])) or (
                    (a_char in ['I', 'Í', 'Y', 'Ý']) and (w_char in ['y', 'ý', 'i', 'í']))):
            if w_char in ['I', 'Í', 'Y', 'Ý']:
                report_error_type += '+formCap1'
            else:
                report_error_type += '+formCap0'

        if (not report_error_char) and (w_char != a_char) and (w1_char == a1_char == '$'):
            report_error_char = '1'
            report_error_type = 'formSingCh'

            #    if ($report_error_type ne 'Unspec') { print "Formal error found: $report_error_type\n" }
    return report_error_type, report_error_char


# konec podprogramu pro srovnání dvou znaků
# *******************************************************************

# Načte slova do stringových polí, zachová nerozdělené "ch"
def split_string_to_array_keep_ch(ww):
    if not re.search(r'[Cc][Hh]', ww):
        w_string = [x for x in ww]
    else:
        w_string = ww.replace("ch", "Ẅ").replace("Ch", "Ǘ").replace("CH", "Û").replace("cH", "ǘ")
        new_w_string = []
        for w_s in w_string:
            c = ""
            if w_s == 'Ẅ':
                c = "ch"
            elif w_s == "Ǘ":
                c = "Ch"
            elif w_s == "Û":
                c = "CH"
            elif w_s == 'ǘ':
                c = 'cH'
            else:
                c = w_s
            new_w_string.append(c)
        w_string = new_w_string

    return w_string


def compare_words(ww, aa):
    errors = []
    diff_length_error_recorder = 0  # pojistka proti dvojímu reportování chyby, u slov lišících se počtem znaků.

    if (ww == aa):
        return ""

    w_string = split_string_to_array_keep_ch(ww)
    a_string = split_string_to_array_keep_ch(aa)

    # =======================================================================================================
    #	VLASTNÍ KONTROLA CHYB formy v rámci jednoho slova
    # =======================================================================================================
    # Uvažujeme několik možností, další bude možné doplnit, ukáže-li se, že to je vhodné.
    # 1) Stejná délka řetězců:
    # 1A) Rozdíl v jednom znaku, stejná délka (dále lze rozčlenit, interpunkce, znělost atd.).
    # 1B) Rozdíl ve dvou znacích těsně vedle sebe, stejná délka (ňe X ně).
    # 1C) Rozdíl ve dvou znacích (prohozeny), i několik znaků od sebe (autosub X autobus)
    #
    # Tolerujeme více jednotlivých chyb typu 1A
    #
    # 2) Rozdílná délka řetězců
    # 2A) R0 kratší než R1, chybí znaky na začátku slova.
    # 2B) R0 kratší než R1, chybí znaky uprostřed slova.
    # 2C) R0 kratší než R1, chybí znaky na konci slova.
    # 2D) R0 delší než R1, přebývají znaky na začátku slova.
    # 2E) R0 delší než R1, přebývají znaky uprostřed slova.
    # 2F) R0 delší než R1, přebývají znaky na konci slova.

    e_string = [None] * (max(len(w_string), len(a_string)) + 1)
    if len(w_string) == len(a_string):
        # print('Stejne dlouha slova')
        single_char_error = 0
        error_neurceno = 0
        metateze_w, metateze_a = "", ""  # Potenciální metateze: jsou-li dva znaky prohozeny, čekáme, nenajdeme-li je později.
        for id_ch in range(len(w_string)):
            if w_string[id_ch] == a_string[id_ch]:
                e_string[id_ch] = '0'
            elif not e_string[id_ch]:
                w0, w1, a0, a1 = w_string[id_ch], '$', a_string[id_ch], '$'
                if id_ch < len(w_string) - 1:  # Stejná délka řetězců, stačí jedna podmínka.
                    w1, a1 = w_string[id_ch + 1], a_string[id_ch + 1]
                # Porovnání lišících se znaků samostatným podprogramem (pro přehlednost):
                err_name, err_char = compare_single_characters(w0, a0, w1, a1)
                if err_name == 'formSingCh' and w1 == a1 == "$" and w_string[:-1] != a_string[:-1]:
                    pass
                elif err_char:
                    if "+" not in err_name:
                        errors.append(err_name)
                    else:
                        errors.extend(err_name.split("+"))

                    if err_char == 'PP':
                        e_string[id_ch] = 'P'
                        e_string[id_ch + 1] = 'P'
                    elif err_char == 'DD':
                        e_string[id_ch] = 'D'
                        e_string[id_ch + 1] = 'D'
                    else:
                        e_string[id_ch] = err_char

                # Lokální metateze. "jesm"
                elif (id_ch < len(w_string) - 1) and (w_string[id_ch] == a_string[id_ch + 1]) and (w_string[id_ch + 1] == a_string[id_ch]) \
                        and ((id_ch + 1 == len(w_string) or (
                                    (id_ch < len(w_string) - 2) and (w_string[id_ch + 2] == a_string[id_ch + 2]))) and \
                                     ((id_ch == 0) or (w_string[id_ch - 1] == a_string[id_ch - 1]))):
                    e_string[id_ch] = 'M'
                    e_string[id_ch + 1] = 'M'
                    errors.append('formMeta')

                elif metateze_w and metateze_a and (metateze_w == a_string[id_ch]) and (metateze_a == w_string[id_ch]) \
                        and ((id_ch == len(w_string)) or (
                                    (id_ch < len(w_string) - 1) and (w_string[id_ch + 1] == a_string[id_ch + 1]))) and (
                            (id_ch > 0) and (w_string[id_ch - 1] == a_string[id_ch - 1])):
                    e_string[id_ch] = 'M'
                    errors.append('formMeta')
                    error_neurceno = 0
                    single_char_error = 0

                elif ((id_ch + 1 < len(w_string)) and (w_string[id_ch + 1] == a_string[id_ch + 1]) and (
                            (id_ch == 0) or (w_string[id_ch - 1] == a_string[id_ch - 1]))):
                    metateze_w, metateze_a = w_string[id_ch], a_string[id_ch]
                    error_neurceno = 1
                    if single_char_error == 0:
                        single_char_error = 1
                    else:
                        single_char_error = -1

            if not e_string[id_ch]:
                # Třídění zbývajících, dosud neidentifikovaných chyb: na konci slova, na zač. slova, jinde.
                sufx = 0
                prfx = 0
                prfx_form = "X*****X"
                if (id_ch > 0) and (error_neurceno == 0):
                    # Pokud se od určitého znaku ve slově do konce slova žádný neshoduje, typ suffix.
                    sufx = 1
                    for id_ch_2 in range(id_ch, len(w_string)):
                        if a_string[id_ch_2] == w_string[id_ch_2]:
                            sufx = 0
                            break

                if (id_ch == 0) and (w_string[-1] == a_string[-1]):
                    # Pokud se od konce slova do určitého všechny znaky shodují, potom žádný neshoduje, typ prefix.
                    switch_eq_ne = -1
                    prfx = 1
                    for id_ch_2 in range(0, len(w_string) - 1):
                        if (w_string[-1 - id_ch_2] != a_string[-1 - id_ch_2]):
                            switch_eq_ne = id_ch_2
                            break

                    if switch_eq_ne > -1:
                        for id_ch_3 in range(switch_eq_ne, len(w_string) - 1):
                            if (w_string[-1 - id_ch_3] == a_string[-1 - id_ch_3]):
                                prfx = 0
                                prfx_form = "X*****X"
                                break
                            else:
                                prfx_form = a_string[-1 - id_ch_3] + prfx_form
                if prfx == 1:
                    if prfx_form in list_of_prefixes:
                        errors.append('formPre')
                        error_neurceno = 0
                    else:
                        errors.append('formHead')
                        error_neurceno = 0
                    break
                elif sufx == 1:
                    errors.append('formTail')
                    error_neurceno = 0
                    break
        if error_neurceno == 1:
            if single_char_error == 1:
                errors.append('formSingCh')
            else:
                errors.append('formUnspec')
    # OK: end of len(w_string) == len(a_string)

    # Nestejně dlouhá slova, ale alespoň nějaká shoda na začátku nebo na konci slova.
    elif ((len(w_string) > 0) and (len(a_string) > 0) and (len(w_string) != len(a_string)) and \
                  ((a_string[0] == w_string[0]) or (len(w_string) > 1 and len(a_string) > 1 and a_string[1] == w_string[1]) or \
                           ((len(a_string) > 2) and len(w_string) > 1 and (a_string[1] == w_string[0]) and (a_string[2] == w_string[1])) or \
                           ((len(w_string) > 2) and len(a_string) > 1 and (a_string[0] == w_string[1]) and (a_string[1] == w_string[2])) or \
                           (a_string[-1] == w_string[-1]) or (len(a_string) > 1 and len(w_string) > 1 and a_string[-2] == w_string[-2]))):

        if ((a_string[0] == w_string[0]) or \
                    ((len(a_string) > 2) and (len(w_string) > 2) and (a_string[1] == w_string[1]) and (a_string[2] == w_string[2])) or \
                            ((len(a_string) > 2) and len(w_string) > 1) and (a_string[1] == w_string[0]) and (
                                a_string[2] == w_string[1])) or \
                ((len(w_string) > 2) and len(a_string) > 1 and (a_string[0] == w_string[1]) and (a_string[1] == w_string[2])):
            # Kontrola od začátku slovních tvarů.
            a_shift = 0
            for id_ch in range(0, max(len(a_string), len(w_string))):
                id_cha = id_ch + a_shift
                while id_ch > len(w_string) - 1:
                    w_string.append('$')
                while id_cha > len(a_string) - 1:
                    a_string.append('$')

                if w_string[id_ch] == a_string[id_cha]:
                    e_string[id_ch] = '0'
                elif not e_string[id_ch]:  # OK
                    w0, w1, a0, a1 = w_string[id_ch], '$', a_string[id_cha], '$'
                    if id_ch < len(w_string) - 1:
                        w1 = w_string[id_ch + 1]
                    if id_cha < len(a_string) - 1:
                        a1 = a_string[id_cha + 1]

                    err_name, err_char = compare_single_characters(w0, a0, w1, a1)

                    if err_name == 'formSingCh' and (w1 == "$" or a1 == "$") and (w_string[:-1] != a_string or a_string[:-1] != w_string):
                        pass

                    elif err_char:
                        if '+' not in err_name:
                            errors.append(err_name)
                        else:
                            errors.extend(err_name.split('+'))

                        if err_char == 'PP':
                            e_string[id_ch] = 'P'
                            e_string[id_ch + 1] = 'P'
                        elif err_char == 'DD':
                            e_string[id_ch] = 'D'
                            e_string[id_ch + 1] = 'D'
                        else:
                            e_string[id_ch] = err_char

                # end OK
                if not e_string[id_ch]:  # OK
                    # Kontrola, zda nemůže jít o chybu ve dvojici znaků proti jednomu znaku (je/ě):
                    if (id_ch < len(w_string) - 1) and (id_cha < len(a_string) - 1):
                        w_pair = w_string[id_ch] + w_string[id_ch + 1]
                        if not a_string[id_cha + 1]:
                            a_string += '$'  # TODO tohle by se nemelo stat
                        a_pair = a_string[id_cha] + a_string[id_cha + 1]

                        # Je/ě
                        if re.search(r'^[Jj][EĚeě]$', w_pair) and (a_string[id_cha].lower() == "ě"):
                            errors.append('formJe1')
                            e_string[id_ch] = 'J'
                            e_string[id_ch + 1] = 'J'
                            a_shift -= 1
                            diff_length_error_recorder = 1
                        elif re.search(r'^[Jj][EĚeě]$', a_pair) and (w_string[id_ch].lower() == "ě"):
                            errors.append('formJe0')
                            e_string[id_ch] = 'J'
                            a_shift += 1
                            diff_length_error_recorder = 1

                        # Mně/mě
                        if (id_ch > 0) and (id_cha > 0) and (w_string[id_ch - 1] in ["M", "m"]) and \
                                ((re.search(r'^[NnňŇ][EĚeě]', w_pair) and (a_string[id_cha].lower() == "ě")) or \
                                         ((re.search(r'^[NnňŇ][EĚeě]', a_pair) and (w_string[id_ch].lower() == "ě")))):
                            w_trio = w_string[id_ch - 1] + w_pair
                            a_trio = a_string[id_cha - 1] + a_pair
                            a_pair = a_string[id_cha - 1] + a_string[id_cha]
                            w_pair = w_string[id_ch - 1] + w_string[id_ch]

                            if re.search(r'^[Mm](ně)|(ňe)|(ňě)|(ŇE)|(NĚ)$', w_trio) and re.search(r'^[Mm][Ěě]$', a_pair):
                                errors.append('formMne1')
                                e_string[id_ch - 1] = 'M'
                                e_string[id_ch] = 'M'
                                e_string[id_ch + 1] = 'M'
                                a_shift -= 1
                                diff_length_error_recorder = 1
                            elif re.search(r'^[Mm](ně)|(ňe)|(ňě)|(ŇE)|(NĚ)$', a_trio) and re.search(r'^[Mm][Ěě]$', w_pair):
                                errors.append('formMne0')
                                e_string[id_ch - 1] = 'M'
                                e_string[id_ch] = 'M'
                                a_shift += 1
                                diff_length_error_recorder = 1

                        # Vkladné "J" (Anglije pieme)
                        if (id_ch > 0) and (id_cha > 0) and (w_string[id_ch - 1].lower() == "i") and (
                                    a_string[id_cha - 1].lower() == "i") and \
                                (((w_string[id_ch].lower() == "j") and (w_string[id_ch + 1] in list_vocals) and (
                                            w_string[id_ch + 1] == a_string[id_cha])) or \
                                         ((a_string[id_cha].lower() == "j") and (a_string[id_cha + 1] in list_vocals) and (
                                                     w_string[id_ch] == a_string[id_cha + 1]))):

                            if w_string[id_ch].lower() == "j":
                                e_string[id_ch] = 'j'
                                errors.append('formEpentJ1')
                                a_shift -= 1
                                diff_length_error_recorder = 1
                            else:
                                e_string[id_ch] = 'j'
                                errors.append('formEpentJ0')
                                a_shift += 1
                                diff_length_error_recorder = 1

                        # Protetické "J" (sou jse)
                        if (not e_string[id_ch]) and (id_ch == 0) and (((w_string[0].lower() == "j") and (a_string[0].lower() != "j") and \
                                                                                ((w_string[1] == a_string[0]) or (
                                                                                            a_string[0].lower() == w_string[
                                                                                            1].lower())) and (
                                    a_string[0] in list_consonnants)) or \
                                                                               ((a_string[0].lower() == "j") and (
                                                                                           w_string[0].lower() != "j") and \
                                                                                        ((w_string[0] == a_string[1]) or (
                                                                                                    w_string[0].lower() == a_string[
                                                                                                    1].lower())) and (
                                                                                           a_string[1] in list_consonnants))):
                            if (w_string[0].lower() == "j"):
                                errors.append('formProtJ1')
                                e_string[id_ch + 1] = 'J'
                                a_shift -= 1
                            else:
                                errors.append('formProtJ0')
                                a_shift += 1

                            diff_length_error_recorder = 1
                            e_string[id_ch] = 'J'

                        # Protetické "V" (oják vokurka)
                        if (not e_string[id_ch]) and (id_ch == 0) and (((w_string[0].lower() == "v") and (a_string[0].lower() != "v") and \
                                                                                ((w_string[1] == a_string[0]) or (
                                                                                            a_string[0].lower() == w_string[
                                                                                            1].lower())) and (
                                    a_string[0].lower() == "o")) or \
                                                                               ((a_string[0].lower() == "v") and (
                                                                                           w_string[0].lower() != "v") and (
                                                                                           (w_string[0] == a_string[1]) or \
                                                                                               (w_string[0].lower() == a_string[
                                                                                                   1].lower())) and (
                                                                                           a_string[1].lower() == "o"))):
                            if (w_string[0].lower() == "j"):
                                errors.append('formProtV1')
                                e_string[id_ch + 1] = 'V'
                                a_shift -= 1
                            else:
                                errors.append('formProtV0')
                                a_shift += 1

                            diff_length_error_recorder = 1
                            e_string[id_ch] = 'V'

                        # Epentetické "e" (navíc): jen mezi konsonanty!
                        if (not e_string[id_ch]) and (w_string[id_ch] == 'e') and (id_ch > 0) and (
                                    a_string[id_cha - 1] == w_string[id_ch - 1]) and \
                                (a_string[id_cha] == w_string[id_ch + 1]) and (w_string[id_ch - 1] in list_consonnants) and (
                                    w_string[id_ch + 1] in list_consonnants):
                            errors.append('formEpentE1')
                            e_string[id_ch] = 'E'
                            a_shift -= 1
                            diff_length_error_recorder = 1

                        # Epentetické "e" (chybí): jen mezi konsonanty!
                        elif (not e_string[id_ch]) and (a_string[id_cha] == 'e') and (id_cha > 0) and (
                                    a_string[id_cha - 1] == w_string[id_ch - 1]) and \
                                (a_string[id_cha + 1] == w_string[id_ch]) and (w_string[id_ch - 1] in list_consonnants) and (
                                    w_string[id_ch] in list_consonnants):
                            errors.append('formEpentE0')
                            e_string[id_ch] = 'E'
                            a_shift += 1
                            diff_length_error_recorder = 1

                        # Zdvojená hláska (kamený)
                        if (id_ch > 0) and (id_cha > 0) and (w_string[id_ch].lower() != a_string[id_cha].lower()) and \
                                (w_string[id_ch - 1].lower() == a_string[id_cha - 1].lower()) and (
                                    ((w_string[id_ch - 1].lower() == w_string[id_ch].lower()) and \
                                             (w_string[id_ch + 1].lower() == a_string[id_cha].lower())) or (
                                            (a_string[id_cha - 1].lower() == a_string[id_cha].lower()) and \
                                                (w_string[id_ch].lower() == a_string[id_cha + 1].lower()))):
                            if (w_string[id_ch - 1].lower() == w_string[id_ch].lower()):
                                e_string[id_ch] = 'g'
                                errors.append('formGemin1')
                                a_shift -= 1
                                diff_length_error_recorder = 1
                            else:
                                e_string[id_ch] = 'g'
                                errors.append('formGemin0')
                                a_shift += 1
                                diff_length_error_recorder = 1

                        # Ve zbytku případů ověření, zda nejde jen o jeden chybně přebývající/chybějící znak.
                        if (not e_string[id_ch]) and (len(w_string) == len(a_string) + 1 - a_shift) and (id_ch < len(w_string)) and \
                                (w_string[id_ch + 1] == a_string[id_cha]):
                            remainder_equal = 1
                            for test_rest in range(id_ch + 1, len(w_string)):
                                test_resta = test_rest + a_shift - 1
                                if ((test_resta > len(a_string) - 1) or (a_string[test_resta] != w_string[test_rest])):
                                    remainder_equal = 0
                                    break
                            if (remainder_equal == 1):
                                errors.append('formRedunChar')
                                diff_length_error_recorder = 1
                                break
                        elif ((not e_string[id_ch]) and (len(w_string) == len(a_string) - 1 - a_shift) and (id_ch < len(w_string)) and \
                                      (a_string[id_cha + 1] == w_string[id_ch])):
                            remainder_equal = 1
                            for test_rest in range(id_ch, len(w_string)):
                                test_resta = test_rest + a_shift + 1
                                if ((test_resta > len(a_string) - 1) or (a_string[test_resta] != w_string[test_rest])):
                                    remainder_equal = 0
                                    break
                            if (remainder_equal == 1):
                                errors.append('formMissChar')
                                diff_length_error_recorder = 1
                                break
                                # OK: not defined e_string[id_ch]
                                # OK: for my id_ch
                                # OK: line 444
                                # OK: line 438
    # Řešení zbytku, neoznačeného, žádná konkrétní chyba neidentifikována, ale chyba tu je...
    if len(errors) == 0:

        if (a_string[0] == w_string[0]) or \
                ((len(a_string) > 2) and (len(w_string) > 2) and (a_string[1] == w_string[1]) and (a_string[2] == w_string[2])) or \
                ((len(a_string) > 2) and (len(w_string) > 1) and (a_string[1] == w_string[0]) and (a_string[2] == w_string[1])) or \
                ((len(w_string) > 2) and (len(a_string) > 1) and (a_string[0] == w_string[1]) and (a_string[1] == w_string[2])):
            # Kontrola od začátku slovních tvarů.
            a_shift = 0
            for id_ch in range(0, max(len(w_string), len(a_string))):
                id_cha = id_ch + a_shift
                while id_ch > len(w_string) - 1:
                    w_string.append('$')
                while id_cha > len(a_string) - 1:
                    a_string.append('$')

                if w_string[id_ch] == a_string[id_cha]:
                    e_string[id_ch] = '0'
                elif not e_string[id_ch]:  # OK
                    w0, w1, a0, a1 = w_string[id_ch], '$', a_string[id_cha], '$'
                    if id_ch < len(w_string) - 1:
                        w1 = w_string[id_ch + 1]
                    if id_cha < len(a_string) - 1:
                        a1 = a_string[id_cha + 1]

                    err_name, err_char = compare_single_characters(w0, a0, w1, a1)
                    if err_name == 'formSingCh' and (w1 == "$" or a1 == "$") and (w_string[:-1] != a_string or a_string[:-1] != w_string):
                        pass

                    elif err_char:
                        if not '+' in err_name:
                            errors.append(err_name)
                        else:
                            errors.extend(err_name.split('+'))

                        if err_char == 'PP':
                            e_string[id_ch] = 'P'
                            e_string[id_ch + 1] = 'P'
                        elif err_char == 'DD':
                            e_string[id_ch] = 'D'
                            e_string[id_ch + 1] = 'D'
                        else:
                            e_string[id_ch] = err_char

                # OK
                if not e_string[id_ch]:  # OK
                    # Kontrola, zda nemůže jít o chybu ve dvojici znaků proti jednomu znaku (je/ě):
                    if (id_ch < len(w_string)) and (id_cha < len(a_string) - 1):
                        if id_ch == len(w_string) - 1:
                            w_pair = w_string[id_ch] + '$'
                        else:
                            w_pair = w_string[id_ch] + w_string[id_ch + 1]
                        if not a_string[id_cha + 1]:
                            a_string[id_cha + 1] = '$'
                        a_pair = a_string[id_cha] + a_string[id_cha + 1]

                        # Je/ě
                        if re.search(r'^[Jj][EĚeě]$', w_pair) and (a_string[id_cha].lower() == "ě"):
                            errors.append('formJe1')
                            e_string[id_ch] = 'J'
                            e_string[id_ch + 1] = 'J'
                            a_shift -= 1
                            diff_length_error_recorder = 1
                        elif re.search(r'^[Jj][EĚeě]$', a_pair) and (w_string[id_ch].lower() == "ě"):
                            errors.append('formJe0')
                            e_string[id_ch] = 'J'
                            a_shift += 1
                            diff_length_error_recorder = 1

                        # Mně/mě
                        if (id_ch > 0) and (id_cha > 0) and (w_string[id_ch - 1].lower() == "m") and \
                                ((re.search(r'^[NnňŇ][EĚeě]$', w_pair) and (a_string[id_cha].lower() == "ě")) or \
                                         (re.search(r'^[NnňŇ][EĚeě]$', a_pair) and (w_string[id_ch].lower() == "ě"))):

                            w_trio = w_string[id_ch - 1] + w_pair
                            a_trio = a_string[id_cha - 1] + a_pair
                            a_pair = a_string[id_cha - 1] + a_string[id_cha]
                            w_pair = w_string[id_ch - 1] + w_string[id_ch]
                            if re.search(r'^[Mm](ně)|(ňe)|(ňě)|(ŇE)|(NĚ)$', w_trio) and re.search(r'^[Mm][Ěě]$', a_pair):
                                errors.append('formMne1')
                                e_string[id_ch - 1] = 'M'
                                e_string[id_ch] = 'M'
                                e_string[id_ch + 1] = 'M'
                                a_shift -= 1
                                diff_length_error_recorder = 1
                            elif re.search(r'^[Mm](ně)|(ňe)|(ňě)|(ŇE)|(NĚ)$', a_trio) and re.search(r'^[Mm][Ěě]$', w_pair):
                                errors.append('formMne0')
                                e_string[id_ch - 1] = 'M'
                                e_string[id_ch] = 'M'
                                a_shift += 1
                                diff_length_error_recorder = 1
                        # Vkladné "J" (Anglije pieme)
                        if (id_ch > 0) and (id_cha > 0) and (w_string[id_ch - 1].lower() == "i") and (
                                    a_string[id_cha - 1].lower() == "i") and \
                                (((w_string[id_ch].lower() == "j") and (w_string[id_ch + 1] in list_vocals) and (
                                            w_string[id_ch + 1] == a_string[id_cha])) or
                                     ((a_string[id_cha].lower() == "j") and (a_string[id_cha + 1] in list_vocals) and (
                                                 w_string[id_ch] == a_string[id_cha + 1]))):
                            if (w_string[id_ch].lower() == "j"):
                                e_string[id_ch] = 'j'
                                errors.append('formEpentJ1')
                                a_shift -= 1
                                diff_length_error_recorder = 1
                            else:
                                e_string[id_ch] = 'j'
                                errors.append('formEpentJ0')
                                a_shift += 1
                                diff_length_error_recorder = 1

                        # Protetické "J" (sou jse)
                        if (not e_string[id_ch]) and (id_ch == 0) and (((w_string[0].lower() == "j") and (a_string[0].lower() == "j") and \
                                                                                ((w_string[1] == a_string[0]) or (
                                                                                            a_string[0].lower() == w_string[
                                                                                            1].lower())) and (
                                    a_string[0] in list_consonnants)) or \
                                                                               ((a_string[0].lower() == "j") and (
                                                                                           w_string[0].lower() == "j") and (
                                                                                           (w_string[0] == a_string[1]) or \
                                                                                               (w_string[0].lower() == a_string[
                                                                                                   1].lower())) and (
                                                                                           a_string[1] in list_consonnants))):
                            if (w_string[0].lower() == "j"):
                                errors.append('formProtJ1')
                                e_string[id_ch + 1] = 'J'
                                a_shift -= 1
                            else:
                                errors.append('formProtJ0')
                                a_shift += 1

                            diff_length_error_recorder = 1
                            e_string[id_ch] = 'J'

                        # Protetické "V" (oják vokurka)
                        if (not e_string[id_ch]) and (id_ch == 0) and (((w_string[0].lower() == "v") and (a_string[0].lower() == "v") and \
                                                                                ((w_string[1] == a_string[0]) or (
                                                                                            a_string[0].lower() == w_string[
                                                                                            1].lower())) and (
                                    a_string[0].lower() == "o")) or \
                                                                               ((a_string[0].lower() == "v") and (
                                                                                           w_string[0].lower() != "v") and (
                                                                                           (w_string[0] == a_string[1]) or \
                                                                                               (w_string[0].lower() == a_string[
                                                                                                   1].lower())) and (
                                                                                           a_string[1].lower() == "o"))):
                            if (w_string[0].lower() == "j"):
                                errors.append('formProtV1')
                                e_string[id_ch + 1] = 'V'
                                a_shift -= 1
                            else:
                                errors.append('formProtV0')
                                a_shift += 1

                            diff_length_error_recorder = 1
                            e_string[id_ch] = 'V'

                        # Epentetické "e" (navíc): jen mezi konsonanty!
                        if (not e_string[id_ch]) and (w_string[id_ch] == 'e') and (id_ch > 0) and (id_cha > 0) and (
                                    a_string[id_cha - 1] == w_string[id_ch - 1]) and \
                                (a_string[id_cha] == w_string[id_ch + 1]) and (w_string[id_ch - 1] in list_consonnants) and (
                                    w_string[id_ch + 1] in list_consonnants):
                            errors.append('formEpentE1')
                            e_string[id_ch] = 'E'
                            a_shift -= 1
                            diff_length_error_recorder = 1
                        # Epentetické "e" (chybí): jen mezi konsonanty!
                        elif (not e_string[id_ch]) and (a_string[id_cha] == 'e') and (id_cha > 0) and (
                                    a_string[id_cha - 1] == w_string[id_ch - 1]) and (id_ch < len(w_string) - 1) and \
                                (a_string[id_cha + 1] == w_string[id_ch]) and (w_string[id_ch - 1] in list_consonnants) and (
                                    w_string[id_ch] in list_consonnants):
                            errors.append('formEpentE0')
                            e_string[id_ch] = 'E'
                            a_shift += 1
                            diff_length_error_recorder = 1

                        # Zdvojená hláska (kamený)
                        if (id_ch > 0) and (id_cha > 0) and (id_ch < len(w_string) - 1) and (id_cha < len(a_string) - 1) and (
                            w_string[id_ch].lower() != a_string[id_cha].lower()) and (
                            w_string[id_ch - 1].lower() == a_string[id_cha - 1].lower()) and (((w_string[id_ch - 1].lower() == w_string[
                            id_ch].lower()) and (w_string[id_ch + 1].lower() == a_string[id_cha].lower())) or (
                            (a_string[id_cha - 1].lower() == a_string[id_cha].lower()) and (
                            w_string[id_ch].lower() == a_string[id_cha + 1].lower()))):

                            if w_string[id_ch - 1].lower() == w_string[id_ch].lower():
                                e_string[id_ch] = 'g'
                                errors.append('formGemin1')
                                a_shift -= 1
                                diff_length_error_recorder = 1
                            else:
                                e_string[id_ch] = 'g'
                                errors.append('formGemin0')
                                a_shift += 1
                                diff_length_error_recorder = 1

                        # Ve zbytku případů ověření, zda nejde jen o jeden chybně přebývající/chybějící znak.
                        if ((not e_string[id_ch]) and (len(w_string) == len(a_string) + 1 - a_shift) and (id_ch < len(w_string) - 1) and \
                                    (w_string[id_ch + 1] == a_string[id_cha])):
                            remainder_equal = 1
                            for test_rest in range(id_ch + 1, len(w_string)):
                                test_resta = test_rest + a_shift - 1
                                if (not a_string[test_resta] or (a_string[test_resta] != w_string[test_rest])):
                                    remainder_equal = 0
                                    break

                            if remainder_equal == 1:
                                errors.append('formRedunChar')
                                diff_length_error_recorder = 1
                                break
                        elif ((not e_string[id_ch]) and (len(w_string) == len(a_string) - 1 - a_shift) and (id_ch < len(w_string) - 1) and \
                                      (a_string[id_cha + 1] == w_string[id_ch])):
                            remainder_equal = 1
                            for test_rest in range(id_ch, len(w_string)):
                                test_resta = test_rest + a_shift + 1
                                if ((not a_string[test_resta]) or (a_string[test_resta] != w_string[test_rest])):
                                    remainder_equal = 0
                                    break
                            if (remainder_equal == 1):
                                errors.append('formMissChar')
                                diff_length_error_recorder = 1
                                break

        w_string = list("".join(w_string).rstrip('$'))
        a_string = list("".join(a_string).rstrip('$'))

        this_condifition_satistified = False
        this_condifition_satistified_ind = 0
        if (diff_length_error_recorder == 0) and (len(w_string) > 0) and (len(w_string) < len(a_string)):
            this_condifition_satistified = True
        elif (diff_length_error_recorder == 0) and (len(a_string) > 0) and (len(a_string) < len(w_string)):
            tmp = a_string
            a_string = w_string
            w_string = tmp
            this_condifition_satistified = True
            this_condifition_satistified_ind = 1
        if this_condifition_satistified:
            allowed_tail_tolerence = math.ceil(len(w_string) * 0.6)
            if w_string[:allowed_tail_tolerence] == a_string[:allowed_tail_tolerence]:
                errors.append('formTail{}'.format(this_condifition_satistified_ind))
            elif w_string[-allowed_tail_tolerence:] == a_string[-allowed_tail_tolerence:]:

                tail_same_ind_w = len(w_string) - 1
                tail_same_ind_a = len(a_string) - 1
                while tail_same_ind_w >= 0 and tail_same_ind_a >= 0 and w_string[tail_same_ind_w] == a_string[tail_same_ind_a]:
                    tail_same_ind_w -= 1
                    tail_same_ind_a -= 1

                prefix_string = ''.join(a_string[:tail_same_ind_a + 1])
                if prefix_string in list_of_prefixes:
                    errors.append('formPre{}'.format(this_condifition_satistified_ind))
                else:
                    errors.append('formHead{}'.format(this_condifition_satistified_ind))

    er_rep = ""
    for er in errors:
        if er_rep == "":
            er_rep = er
        elif er_rep == 'formUnspec':
            er_rep = er
        elif er in er_rep:
            pass
        elif er != 'formUnspec':
            er_rep += "|" + er
    return er_rep


if __name__ == "__main__":
    # simple tests
    assert compare_words("evropě", "Evropě") == "formCap0"
    assert compare_words("Staré", "staré") == "formCap1"
    assert compare_words("vecí", "věcí") == "formCaron0"
    assert compare_words("břečel", "brečel") == "formCaron1"
    assert compare_words("usmévavé", "usměvavé") == "formDiaE"
    assert compare_words("nemúžeš", "nemůžeš") == "formDiaU"
    assert compare_words("ňikdo", "nikdo") == "formDtn"
    assert compare_words("vzpominám", "vzpomínám") == "formQuant0"
    assert compare_words("ktérá", "která") == "formQuant1"
    assert compare_words("stratíme", "ztratíme") == "formVoiced0"
    assert compare_words("zbalit", "sbalit") == "formVoiced1"
    assert compare_words("Kdyš", "Když") == "formVoicedFin0"
    assert compare_words("přez", "přes") == "formVoicedFin1"
    assert compare_words("pěžky", "pěšky") == "formVoiced"
    assert compare_words("pražskích", "pražských") == "formY0"
    assert compare_words("hlavným", "hlavním") == "formY1"
    assert compare_words("yaké", "jaké") == "formYJ0"
    assert compare_words("Atlantic", "Atlantik") == "formCK0"
    assert compare_words("Amerikě", "Americe") == "formPalat0"
    assert compare_words("najdnou", "najednou") == "formEpentE0"
    assert compare_words("rozeběhl", "rozběhl") == "formEpentE1"
    assert compare_words("napie", "napije") == "formEpentJ0"
    assert compare_words("dijamant", "diamant") == "formEpentJ1"
    assert compare_words("polostrově", "poloostrově") == "formGemin0"
    assert compare_words("essej", "esej") == "formGemin1"
    assert compare_words("uběhlo", "ubjehlo") == "formJe0"
    assert compare_words("vjeděl", "věděl") == "formJe1"
    assert compare_words("zapoměla", "zapomněla") == "formMne0"
    assert compare_words("mněla", "měla") == "formMne1"
    assert compare_words("sem", "jsem") == "formProtJ0"
    assert compare_words("jse", "se") == "formProtJ1"
    assert compare_words("dobrodružtsví", "dobrodružství") == "formMeta"
    assert compare_words("protže", "protože") == "formMissChar"
    assert compare_words("opratrně", "opatrně") == "formRedunChar"
    assert compare_words("otevřila", "otevřela") == "formSingCh"
    assert compare_words("poletěla", "letěla") == "formPre1"
    assert compare_words("rustala", "zůstala") == "formHead"
    assert compare_words("nádhernou", "nádherná") == "formTail1"
    assert compare_words("provudkyně", "průvodkyně") == "formUnspec"

    print("All tests succesfully run :)")
