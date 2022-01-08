# Czech Errant

This folder stores Czech specific classifier and merger.

## Error Types

We adapted the original English error types to the
Czech language. The POS error types are based on the UD POS
tags (Nivre et al., 2020) and may contain an optional :INFL subtype when the original and the
corrected words share a common lemma. The
word-order error type was extended by an optional
:SPELL subtype to allow for capturing word order
errors including words with minor spelling errors.
The original orthography error type ORTH covering both errors in casing and whitespaces is now
subtyped with :WSPACE and :CASING to better
distinguish between the two phenomena. Finally,
we add two error types specific to Czech: DIACR for errors in either missing or redundant di-
acritics and QUOTATION for wrongly used quotation marks. Two original error types remain un-
changed: MORPH, indicating replacement of a token by another with the same lemma but different
POS, and SPELL, indicating incorrect spelling.
For part-of-speech tagging and lemmatization
we rely on UDPipe (https://github.com/ufal/udpipe). 9 The
word list for detecting spelling errors comes from
MorfFlex (https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-1673?show=full).

A complete list of error types including their subtypes:

| Error Type | Subtype | Example |
| ------ | ---- | ---- |
| POS (15) | | tažené → řízené |
|         | :INFL | manželka → manželkou |
| MORPH |  | maj → mají  |
| ORTH | :CASING | usa → USA |
|      | :WSPACE | přes to → přesto |
|SPELL | |  ochtnat → ochutnat |
|WO | | plná jsou → jsou plná |
|   | :SPELL | blískají zeleně → zeleně blýskají |
|QUOTATION | | " → „ |
|DIACR | | tiskarna → tiskárna |
|OTHER | | sem → jsem ho |


## More fine-grained classification

For more linguistically curious minds, we also implemented a classifier with more fine-grained Czech linguistic phenomena. These are in [classifier_detailed.py](classifier_detailed.py).