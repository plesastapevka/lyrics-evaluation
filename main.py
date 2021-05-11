import collections
import re
import json


def pre_process_text(text):
    # clean_text = re.sub(r"\[[^<]+]|((^|\s+)[ me | im | is | I'm | your | you | and | in | yeah | i | ay | aye | at | to | the | a]+(\s+|$))", " ", text.lower())
    # clean_text = re.sub(r"\[[^<]+]", " ", text.lower())
    clean_text = re.sub(r"\[[^<]+]|((^|\s+)[ yeah | ay | aye | uh | ugh | argh | na ]+(\s+|$))", " ", text.lower())
    raw_text = re.sub(r'[^A-Za-zČčŠšŽžĐđäöüßÄÖÜẞ. ]', '', clean_text)
    return raw_text


def create_n_grams(text, n=3):
    n_grams = [text[i:i + n] for i in range(len(text) - n + 1)]
    ngrams_freq = collections.Counter(n_grams)
    ngrams_map = ngrams_freq.most_common()
    return [i[0] for i in ngrams_map]


def build_model(path, write=False):
    # Read lyrics from file
    try:
        infile = open(path, "r")
        data = infile.read().replace('\n', ' ')
    except IOError:
        print("File does not exist")
        exit(1)

    infile.close()
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
    if write:
        try:
            outfile = open("learning_profiles/profile.json", "w")
            json.dump(profile, outfile)
            print("Profile created.")
        except IOError:
            print("Cannot write to file")
            exit(1)
        finally:
            outfile.close()
    else:
        return profile


def ngrams(s, n=2, i=0):
    while len(s[i:i+n]) == n:
        ret_val = s[i:i+n]
        yield " ".join(ret_val)
        i += 1


def get_diff(ngram, element, idx):
    try:
        index = ngram.index(element)
        return abs(index - idx)
    except ValueError:
        return len(ngram)


def process_ngram(new_ngram, ngram):
    ngram_sum = 0
    for idx, e in enumerate(new_ngram):
        diff = get_diff(ngram, e, idx)
        if diff != -1:
            ngram_sum += diff
    return ngram_sum


def calculate(new_profile, path="learning_profiles/profile.json"):
    try:
        infile = open(path, "r")
        profile = json.load(infile)
    except IOError:
        print("Cannot open file")
        exit(1)

    infile.close()

    # test profiles
    uni_new = list(new_profile["unigrams"].keys())
    bi_new = list(new_profile["bigrams"].keys())
    tri_new = list(new_profile["trigrams"].keys())
    four_new = list(new_profile["fourgrams"].keys())
    five_new = list(new_profile["fivegrams"].keys())

    # learning profiles
    uni = list(profile["unigrams"].keys())
    bi = list(profile["bigrams"].keys())
    tri = list(profile["trigrams"].keys())
    four = list(profile["fourgrams"].keys())
    five = list(profile["fivegrams"].keys())

    ngram_sum = 0

    # ngrams processing
    # ngram_sum += process_ngram(uni_new, uni)
    ngram_sum += process_ngram(bi_new, bi)
    ngram_sum += process_ngram(tri_new, tri)
    ngram_sum += process_ngram(four_new, four)
    ngram_sum += process_ngram(five_new, five)

    return ngram_sum


def main():
    create_model = False
    if create_model:
        build_model(path="learning_profiles/hiphoplyrics.txt", write=True)
    else:
        profile = build_model(path="test_lyrics/jcole_middle_child.txt")
        print("J. Cole - Middle Child: " + str(calculate(new_profile=profile)))

        profile = build_model(path="test_lyrics/eminem_kim.txt")
        print("Eminem - Kim: " + str(calculate(new_profile=profile)))

        profile = build_model(path="test_lyrics/melvoni_no_mans_land.txt")
        print("Melvoni - No Man's Land: " + str(calculate(new_profile=profile)))

        profile = build_model(path="test_lyrics/kid_cudi_day_n_nite.txt")
        print("Kid Cudi - Day 'n' Nite: " + str(calculate(new_profile=profile)))

        profile = build_model(path="test_lyrics/mobb_deep_shook_ones.txt")
        print("Mobb Deep - Shook Ones, Part II: " + str(calculate(new_profile=profile)))

        profile = build_model(path="test_lyrics/passenger_let_her_go.txt")
        print("Passenger - Let Her Go: " + str(calculate(new_profile=profile)))

        profile = build_model(path="test_lyrics/gnr_sweet_child.txt")
        print("Guns N' Roses - Sweet Child O' Mine: " + str(calculate(new_profile=profile)))


if __name__ == "__main__":
    main()
