import collections
import re
import json
import t2e
import time
# from lyrics_extractor import SongLyrics


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


def character_ngrams(text, n=3):
    n_grams = [text[i:i + n] for i in range(len(text) - n + 1)]
    ngrams_freq = collections.Counter(n_grams)
    ngrams_map = ngrams_freq.most_common()
    return ngrams_map


def build_model_path(path, write=False):
    try:
        infile = open(path, "r")
        data = infile.read().replace('\n', ' ')
    except IOError:
        print("File does not exist")
        exit(1)
    
    infile.close()
    return build_model(data, write=write)


def build_model(data, write=False):
    # Read lyrics from file
    raw_text = pre_process_text(data)

    # Word ngrams
    words_array = raw_text.split()
    w_unigram = list(ngrams(words_array, n=1))
    w_bigram = list(ngrams(words_array, n=2))
    w_trigram = list(ngrams(words_array, n=3))
    w_fourgram = list(ngrams(words_array, n=4))
    w_fivegram = list(ngrams(words_array, n=5))

    w_unigram_freq = collections.Counter(w_unigram).most_common()
    w_bigram_freq = collections.Counter(w_bigram).most_common()
    w_trigram_freq = collections.Counter(w_trigram).most_common()
    w_fourgram_freq = collections.Counter(w_fourgram).most_common()
    w_fivegram_freq = collections.Counter(w_fivegram).most_common()

    # Character ngrams
    c_unigram_freq = character_ngrams(raw_text, 1)
    c_bigram_freq = character_ngrams(raw_text, 2)
    c_trigram_freq = character_ngrams(raw_text, 3)
    c_fourgram_freq = character_ngrams(raw_text, 4)
    c_fivegram_freq = character_ngrams(raw_text, 5)

    profile = {
        'word_ngrams': {
            'unigrams': dict(w_unigram_freq[:300]),
            'bigrams': dict(w_bigram_freq[:300]),
            'trigrams': dict(w_trigram_freq[:300]),
            'fourgrams': dict(w_fourgram_freq[:300]),
            'fivegrams': dict(w_fivegram_freq[:300])
        },
        'char_ngrams': {
            'unigrams': dict(c_unigram_freq[:300]),
            'bigrams': dict(c_bigram_freq[:300]),
            'trigrams': dict(c_trigram_freq[:300]),
            'fourgrams': dict(c_fourgram_freq[:300]),
            'fivegrams': dict(c_fivegram_freq[:300])
        }
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


def get_ngram_value(profile, new_profile):
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


def calculate(new_profile, path="learning_profiles/profile.json", word_ngrams=True):
    try:
        infile = open(path, "r")
        profile = json.load(infile)
    except IOError:
        print("Cannot open file")
        exit(1)

    infile.close()

    if word_ngrams:
        ngram_sum = (1 - (get_ngram_value(profile["word_ngrams"], new_profile["word_ngrams"]) / 360000)) * 100
    else:
        ngram_sum = (1 - (get_ngram_value(profile["char_ngrams"], new_profile["char_ngrams"]) / 270784)) * 100

    return round(ngram_sum, 2)


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


def write_results(finals):
    results_w_ngram = open("word_ngram.txt", "w")
    results_c_ngram = open("char_ngram.txt", "w")
    results_t2e = open("t2e.txt", "w")

    results_w_ngram.write(r"Pesem & Vrednost \\\hline" + "\n")
    results_c_ngram.write(r"Pesem & Vrednost \\\hline" + "\n")
    results_t2e.write(r"Pesem & Vrednost v % \\\hline" + "\n")

    # Results based on word ngram value
    finals.sort(key=lambda e: e["word_ngram"]["value"], reverse=True)
    for r in finals:
        results_w_ngram.write(
            r["title"] + " & " + str(r["word_ngram"]["value"]) + r"\\\hline" + "\n")

    # Results based on char ngram value
    finals.sort(key=lambda e: e["char_ngram"]["value"], reverse=True)
    for r in finals:
        results_c_ngram.write(
            r["title"] + " & " + str(r["char_ngram"]["value"]) + r"\\\hline" + "\n")

    # Results based on t2e value
    finals.sort(key=lambda e: e["t2e"]["value"], reverse=True)
    for r in finals:
        results_t2e.write(
            r["title"] + " & " + str(r["t2e"]["value"]) + r"\\\hline" + "\n")

    results_w_ngram.close()
    results_c_ngram.close()
    results_t2e.close()


def main():
    create_model = False
    get_lyrics = False
    write = True
    if create_model:
        if get_lyrics:
            extract_lyrics = SongLyrics("AIzaSyDqKiRUEY58zJ6rXIGb9vo7NY6G1vuNf90", "13133a888d06ff0f6")
            val = input("Enter a song: ")
            data = extract_lyrics.get_lyrics(val)
            with open("learning_profiles/hiphoplyrics.txt", "a") as myfile:
                myfile.write(data["lyrics"])
        build_model_path(path="learning_profiles/hiphoplyrics.txt", write=True)
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
        own_results = calculate(new_profile=profile, word_ngrams=True)
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
            results_time.write(r"Pesem & Lastna impl. & T2E \\\hline" + "\n")

        finals = []
        for s in test_data["lyrics"]:
            # T2E TEST
            start = round(time.time() * 1000)
            t2e_results = text2emotion(s["path"])
            # t2e_results = {"Angry": 0}
            end = round(time.time() * 1000)
            t2e_results["Angry"] = round(t2e_results["Angry"] * 100, 2)
            t2e_elapsed = end - start

            # WORD NGRAM TEST
            start = round(time.time() * 1000)
            profile = build_model_path(s["path"])
            own_results_w = calculate(new_profile=profile, word_ngrams=True)
            end = round(time.time() * 1000)
            own_elapsed_w = end - start

            # CHARACTER NGRAM TEST
            start = round(time.time() * 1000)
            profile = build_model_path(s["path"])
            own_results_c = calculate(new_profile=profile, word_ngrams=False)
            end = round(time.time() * 1000)
            own_elapsed_c = end - start

            print("\n" + s["artist"] + " - " + s["title"])
            print("Word ngram value: " + str(own_results_w) + "% in " + str(own_elapsed_w) + " ms")
            print("Character ngram value: " + str(own_results_c) + "% in " + str(own_elapsed_c) + " ms")
            print("T2E value: " + str(t2e_results["Angry"]) + " in " + str(t2e_elapsed) + " ms")

            final_struct = {
                "artist": s["artist"],
                "title": s["title"],
                "word_ngram": {
                    "time": own_elapsed_w,
                    "value": own_results_w
                },
                "char_ngram": {
                    "time": own_elapsed_c,
                    "value": own_results_c
                },
                "t2e": {
                    "time": t2e_elapsed,
                    "value": t2e_results["Angry"]
                }
            }

            finals.append(final_struct)

            if write:
                # results.write(s["artist"] + r"\\" + s["title"] + " & " + str(own_results_w) + " & " + str(t2e_results["Angry"]) + r"\\\hline" + "\n")
                results.write(s["title"] + " & " + str(own_results_w) + " & " + str(t2e_results["Angry"]) + r"\\\hline" + "\n")
                # results_time.write(s["artist"] + r"\\" + s["title"] + " & " + str(own_elapsed_w) + " & " + str(t2e_elapsed) + r"\\\hline" + "\n")
                results_time.write(s["title"] + " & " + str(own_elapsed_w) + " & " + str(t2e_elapsed) + r"\\\hline" + "\n")

        if write:
            results.close()
            results_time.close()
            write_results(finals)


if __name__ == "__main__":
    
    main()
