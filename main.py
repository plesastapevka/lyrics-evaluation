import collections
import re
import json
import t2e
import time
from lyrics_extractor import SongLyrics

def pre_process_text(text):
    clean_text = re.sub(r"\[[^<]+]", " ", text.lower())
    raw_text = re.sub(r'[^A-Za-zČčŠšŽžĐđäöüßÄÖÜẞ. ]', '', clean_text)

    # stopwords = ["i", "you", "and", "the", "im", "ima", "yeah", "ay", "oh", "aye", "uh", "ugh", "uhh", "argh", "rrr",
    # "na", "ooh", "ohh", "me", "a", "to", "in", "your"]
    stopwords = ["yeah", "ay", "oh", "aye", "uh", "ugh", "uhh", "argh", "rrr", "na", "ooh", "ohh", "a"]
    processed_text = raw_text.split()

    resultwords = [word for word in processed_text if word not in stopwords]
    result = ' '.join(resultwords)
    return result


def create_n_grams(text, n=3):
    n_grams = [text[i:i + n] for i in range(len(text) - n + 1)]
    ngrams_freq = collections.Counter(n_grams)
    ngrams_map = ngrams_freq.most_common()
    return [i[0] for i in ngrams_map]


def build_model_path(path):
    try:
        infile = open(path, "r")
        data = infile.read().replace('\n', ' ')
    except IOError:
        print("File does not exist")
        exit(1)
    
    infile.close()
    build_model(path)

def build_model(data, write=False):
    # Read lyrics from file
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
    # profile = {
    #     'unigrams': dict(unigram_freq),
    #     'bigrams': dict(bigram_freq),
    #     'trigrams': dict(trigram_freq),
    #     'fourgrams': dict(fourgram_freq),
    #     'fivegrams': dict(fivegram_freq)
    # }
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


def get_diff(ngram, element, idx, err_val):
    try:
        index = ngram.index(element)
        return abs(index - idx)
    except ValueError:
        return err_val


def process_ngram(new_ngram, ngram):
    ngram_sum = 0
    for idx, e in enumerate(ngram):
        diff = get_diff(new_ngram, e, idx, len(ngram))
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
    ngram_sum += process_ngram(uni_new, uni)
    ngram_sum += process_ngram(bi_new, bi)
    ngram_sum += process_ngram(tri_new, tri)
    ngram_sum += process_ngram(four_new, four)
    # ngram_sum += process_ngram(five_new, five)

    return ngram_sum


def text2emotion(path):
    try:
        infile = open(path, "r")
        data = infile.read()
    except IOError:
        print("Cannot open file")
        exit(1)
    return t2e.calculate_emotion(data)


def text2emotion_data(data):
    return t2e.calculate_emotion(data)

def main():
    create_model = False
    get_lyrics = True
    write = True
    if create_model:
        if get_lyrics:
            extract_lyrics = SongLyrics("AIzaSyDqKiRUEY58zJ6rXIGb9vo7NY6G1vuNf90", "13133a888d06ff0f6")
            val = input("Enter a song: ")
            data = extract_lyrics.get_lyrics(val)
            with open("learning_profiles/hiphoplyrics.txt", "a") as myfile:
                myfile.write(data["lyrics"])
        build_model(path="learning_profiles/hiphoplyrics.txt", write=True) 
    elif get_lyrics:
        extract_lyrics = SongLyrics("AIzaSyDqKiRUEY58zJ6rXIGb9vo7NY6G1vuNf90", "13133a888d06ff0f6")
        val = input("Enter a song: ")
        s = extract_lyrics.get_lyrics(val)

        start = round(time.time() * 1000)
        t2e_results = text2emotion_data(s["lyrics"])
        end = round(time.time() * 1000)
        t2e_elapsed = end - start

        start = round(time.time() * 1000)
        profile = build_model(s["lyrics"])
        own_results = calculate(new_profile=profile)
        end = round(time.time() * 1000)
        own_elapsed = end - start

        print("\n" + s["title"])
        print("Own value: " + str(own_results) + " in " + str(own_elapsed) + " ms")
        print("T2E value: " + str(t2e_results["Angry"]) + " in " + str(t2e_elapsed) + " ms")
    else:
        try:
            infile = open("test_data.json", "r")
            test_data = json.load(infile)
        except IOError:
            print("Cannot open file")
            exit(1)
        if write:
            results = open("results.txt", "w")
            results_time = open("results_time.txt", "w")

            results.write(r"Pesem & Lastna impl. & T2E \\\hline" + "\n")
            results_time.write(r"Pesem & Lastna impl. & T2E & \\\hline" + "\n")

        for s in test_data["lyrics"]:
            start = round(time.time() * 1000)
            t2e_results = text2emotion(s["path"])
            end = round(time.time() * 1000)
            t2e_elapsed = end - start

            start = round(time.time() * 1000)
            profile = build_model_path(s["path"])
            own_results = calculate(new_profile=profile)
            end = round(time.time() * 1000)
            own_elapsed = end - start

            print("\n" + s["artist"] + " - " + s["title"])
            print("Own value: " + str(own_results) + " in " + str(own_elapsed) + " ms")
            print("T2E value: " + str(t2e_results["Angry"]) + " in " + str(t2e_elapsed) + " ms")

            if write:
                results.write(s["artist"] + r"\\" + s["title"] + " & " + str(own_results) + " & " + str(t2e_results["Angry"]) + r"\\\hline" + "\n")
                results_time.write(s["artist"] + r"\\" + s["title"] + " & " + str(own_elapsed) + " & " + str(t2e_elapsed) + r"\\\hline" + "\n")

        if write:
            results.close()
            results_time.close()


if __name__ == "__main__":
    
    main()
