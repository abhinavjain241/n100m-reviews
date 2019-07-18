from fuzzywuzzy import fuzz

THRESHOLD_DEFAULT = 50

hindi_profane_dict = '../../../datasets/hindi_profane_words.csv'

profane_words_o = (line.strip() for line in open(hindi_profane_dict))
profane_words = []
for w in profane_words_o:
    profane_words.append(w)


def get_profanity_score(text, thresh=THRESHOLD_DEFAULT):
    profane_list = []
    for profane_word in profane_words:
        match = fuzz.token_sort_ratio(text, profane_word)
        if match > thresh:
            profane_list.append({profane_word: match})

    return profane_list

# if __name__ == '__main__':
# print(get_profanity_score(""))
