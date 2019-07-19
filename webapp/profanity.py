from fuzzywuzzy import fuzz
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
    profane_map = {}
    for word in text.split(" "):
        # profane_map = {}
        if lang == 'en' and word in common_word_set:
            continue
        for profane_word in profane_words[lang]:
            match = fuzz.ratio(word, profane_word)
            # match = fuzz.token_set_ratio(text, profane_word)
            if match > thresh:
                # profane_map[profane_word] = match
                profane_map[word] = (profane_word, match)

    return profane_map

# if __name__ == '__main__':
#     print(get_profanity_score("review goes here", 70, "en"))
    # print(common_word_set)
