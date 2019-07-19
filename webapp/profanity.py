from fuzzywuzzy import fuzz

THRESHOLD_DEFAULT = 50
LANGUAGE_DEFAULT = "hi"

profane_dict = {"hi": '../../../datasets/hindi_profane_words.csv', "en": '../../../datasets/english_profane_words.csv'}
profane_words = {}

for lang, filename in profane_dict.items():
    with open(filename) as file:
        profane_words[lang] = [line.rstrip('\n') for line in file]


def get_profanity_score(text,
                        thresh=THRESHOLD_DEFAULT,
                        lang=LANGUAGE_DEFAULT):
    profane_map = {}
    for word in text.split(" "):
    # profane_map = {}
        for profane_word in profane_words[lang]:
            match = fuzz.ratio(word, profane_word)
            # match = fuzz.token_set_ratio(text, profane_word)
            if match > thresh:
                # profane_map[profane_word] = match
                profane_map[word] = (profane_word, match)


    return profane_map

# if __name__ == '__main__':
# print(get_profanity_score(""))
