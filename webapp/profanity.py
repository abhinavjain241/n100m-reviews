from fuzzywuzzy import fuzz, process
from config import HINDI_DICTIONARY_PATH, ENG_DICTIONARY_PATH, COMMON_WORD_DICTIONARY

THRESHOLD_DEFAULT = 50
LANGUAGE_DEFAULT = "hi"

profane_dict = {"hi": HINDI_DICTIONARY_PATH, "en": ENG_DICTIONARY_PATH}
profane_words = {}

common_word_set = set()

for lang, filename in profane_dict.items():
    with open(filename) as file:
        profane_words[lang] = [line.rstrip('\n') for line in file]

with open(COMMON_WORD_DICTIONARY) as file:
    for line in file:
        common_word_set.add(line.rstrip('\n'))


def get_profanity_score(text,
                        thresh=THRESHOLD_DEFAULT,
                        lang=LANGUAGE_DEFAULT):
    profane_list = []
    if lang == 'en' and text in common_word_set:
        return profane_list

    return process.extractOne(text, profane_words[lang], scorer=fuzz.ratio, score_cutoff=thresh)
