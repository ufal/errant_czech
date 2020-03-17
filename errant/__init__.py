from importlib import import_module
import spacy
import spacy_udpipe
from errant.annotator import Annotator
import ufal.udpipe

# Load an ERRANT Annotator object for a given language
def load(lang, nlp=None):
    # Make sure the language is supported
    supported = {"en", "cs"}
    if lang not in supported:
        raise Exception("%s is an unsupported or unknown language" % lang)

    # Load spacy
    if lang == 'cs':
        nlp = nlp or spacy_udpipe.load("cs-pdt")

        def tokenize(text):
            sentences = nlp.udpipe._read(
                text, ufal.udpipe.InputFormat.newHorizontalInputFormat())

            for sentence in sentences:
                sentence.setText(" ".join([word.form for word in sentence.words[1:]]))
            return sentences


        nlp.udpipe.tokenize_none = tokenize
        nlp.udpipe.tokenize_do = nlp.udpipe.tokenize

    elif lang == 'en':
        nlp = nlp or spacy.load(lang, disable=["ner"])

    # Load language edit merger
    merger = import_module("errant.%s.merger" % lang)

    # Load language edit classifier
    classifier = import_module("errant.%s.classifier" % lang)
    # The English classifier needs spacy
    if lang == "en": classifier.nlp = nlp
    elif lang == 'cs': classifier.nlp = nlp

    # Return a configured ERRANT annotator
    return Annotator(lang, nlp, merger, classifier)