import collections
import re
import json


def pre_process_text(text):
    clean_text = re.sub(r'\[[^<]+]|((^|\s+)[me|im|you|and|in|yeah|i|ay|aye|at|to|the|a]+(\s+|$))', " ", text.lower())
    raw_text = re.sub(r'[^A-Za-zČčŠšŽžĐđäöüßÄÖÜẞ. ]', '', clean_text)
    return raw_text


def create_n_grams(text, n=3):
    n_grams = [text[i:i + n] for i in range(len(text) - n + 1)]
    ngrams_freq = collections.Counter(n_grams)
    ngrams_map = ngrams_freq.most_common()
    return [i[0] for i in ngrams_map]


def build_model(path):
    # Read lyrics from file
    with open(path, 'r') as file:
        data = file.read().replace('\n', ' ')

    raw_text = pre_process_text(data)
    words_array = raw_text.split()
    unigram = list(ngrams(words_array, n=1))
    bigram = list(ngrams(words_array, n=2))
    trigram = list(ngrams(words_array, n=3))
    fourgram = list(ngrams(words_array, n=4))
    fivegram = list(ngrams(words_array, n=5))

    unigram_freq = collections.Counter(unigram).most_common()
    bigram_freq = collections.Counter(bigram).most_common()
    trigram_freq = collections.Counter(trigram).most_common()
    fourgram_freq = collections.Counter(fourgram).most_common()
    fivegram_freq = collections.Counter(fivegram).most_common()
    profile = {
        'unigrams': dict(unigram_freq[:300]),
        'bigrams': dict(bigram_freq[:300]),
        'trigrams': dict(trigram_freq[:300]),
        'fourgrams': dict(fourgram_freq[:300]),
        'fivegrams': dict(fivegram_freq[:300])
    }
    with open("profile.json", "w") as outfile:
        json.dump(profile, outfile)
        print("Profile created.")
        return


def ngrams(s, n=2, i=0):
    while len(s[i:i+n]) == n:
        ret_val = s[i:i+n]
        yield " ".join(ret_val)
        i += 1


def get_ngrams(path_name="", string=False, input_text=""):
    if not string:
        text = open(path_name).read()
        raw_text = pre_process_text(text)
        bigrams = create_n_grams(raw_text, 2)
        trigrams = create_n_grams(raw_text, 3)
        fourgrams = create_n_grams(raw_text, 4)
        fivegrams = create_n_grams(raw_text, 5)
    else:
        raw_text = pre_process_text(input_text)
        bigrams = create_n_grams(raw_text, 2)
        trigrams = create_n_grams(raw_text, 3)
        fourgrams = create_n_grams(raw_text, 4)
        fivegrams = create_n_grams(raw_text, 5)

    return bigrams, trigrams, fourgrams, fivegrams


def get_diff(ngram, element, idx):
    try:
        index = ngram.index(element)
        return abs(index - idx)
    except ValueError:
        return len(ngram)


def detect_lang(bi, tri, four, five):
    bi_si, tri_si, four_si, five_si = get_ngrams("models/si.txt")
    bi_eng, tri_eng, four_eng, five_eng = get_ngrams("models/eng.txt")
    bi_ger, tri_ger, four_ger, five_ger = get_ngrams("models/ger.txt")
    sim_sum_si = 0
    sim_sum_eng = 0
    sim_sum_ger = 0

    # bigram processing
    for idx, e in enumerate(bi):
        diff_si = get_diff(bi_si, e, idx)
        diff_eng = get_diff(bi_eng, e, idx)
        diff_ger = get_diff(bi_ger, e, idx)
        if diff_si != -1:
            sim_sum_si += diff_si
        if diff_eng != -1:
            sim_sum_eng += diff_eng
        if diff_ger != -1:
            sim_sum_ger += diff_ger

    # trigram processing
    for idx, e in enumerate(tri):
        diff_si = get_diff(tri_si, e, idx)
        diff_eng = get_diff(tri_eng, e, idx)
        diff_ger = get_diff(tri_ger, e, idx)
        if diff_si != -1:
            sim_sum_si += diff_si
        if diff_eng != -1:
            sim_sum_eng += diff_eng
        if diff_ger != -1:
            sim_sum_ger += diff_ger

    # fourgram processing
    for idx, e in enumerate(four):
        diff_si = get_diff(four_si, e, idx)
        diff_eng = get_diff(four_eng, e, idx)
        diff_ger = get_diff(four_ger, e, idx)
        if diff_si != -1:
            sim_sum_si += diff_si
        if diff_eng != -1:
            sim_sum_eng += diff_eng
        if diff_ger != -1:
            sim_sum_ger += diff_ger

    # fivegram processing
    # for idx, e in enumerate(five):
    #     diff_si = get_diff(five_si, e, idx)
    #     diff_eng = get_diff(five_eng, e, idx)
    #     diff_ger = get_diff(five_ger, e, idx)
    #     if diff_si != -1:
    #         sim_sum_si += diff_si
    #     if diff_eng != -1:
    #         sim_sum_eng += diff_eng
    #     if diff_ger != -1:
    #         sim_sum_ger += diff_ger

    # print("English similarity sum is: " + str(sim_sum_eng))
    # print("Slovene similarity sum is: " + str(sim_sum_si))
    # print("German similarity sum is: " + str(sim_sum_ger))
    if min([sim_sum_si, sim_sum_eng, sim_sum_ger]) == sim_sum_eng:
        return "english"
    elif min([sim_sum_si, sim_sum_eng, sim_sum_ger]) == sim_sum_si:
        return "slovenian"
    elif min([sim_sum_si, sim_sum_eng, sim_sum_ger]) == sim_sum_ger:
        return "german"


def main():
    create_model = True
    if create_model:
        build_model(path="hiphoplyrics.txt")
    else:
        bigrams, trigrams, fourgrams, fivegrams = get_ngrams("korpus/kas-5000.text.xml")
        print("Detecting language ...")
        detect_lang(bigrams, trigrams, fourgrams, fivegrams)


if __name__ == "__main__":
    main()
