import re
from dataclasses import dataclass
from itertools import islice

from typing import List

words_db = {}
sentences_and_marks = {}


def initialize_db(path: str):
    f = open(path, "r")
    content = f.read()
    content_list = content.splitlines()
    counter_of_sentences = 0
    for sentence1 in content_list:
        counter_of_sentences += 1
        for word1 in sentence1.split():
            word1 = word1.lower()
            if word1 in words_db.keys():
                append_list = words_db[word1]
                append_list.append((counter_of_sentences, path))
                words_db[word1] = append_list
            else:
                words_db[word1] = [(counter_of_sentences, path)]


@dataclass
class AutoCompleteData:
    completed_sentence: str
    source_text: str
    offset: int
    score: int


def get_best_k_completions(prefix: str) -> List[AutoCompleteData]:
    content_prefix = prefix.lower().split()
    found = False
    for word1 in content_prefix:
        if word1 in words_db.keys() and not found:
            list_of_tuples = words_db[word1]
            for tuple1 in list_of_tuples:
                file = open(tuple1[1], "r")
                line = file.readlines()[tuple1[0] - 1]
                content_line = line.lower().split()
                index_of_word = content_line.index(word1)
                index_of_prefix = content_prefix.index(word1)
                index = index_of_word - index_of_prefix
                found = check_if_include(content_line, content_prefix, line, index, tuple1)
        elif len(content_prefix) == 1: #mistake in only one word
            score=len(prefix)*2
            for word2 in words_db.keys():
                one_diff = False
                diff_array = dif(word2, prefix)
                if prefix in word2:
                    one_diff=True
                elif len(diff_array) <= 1 and (len(prefix)-len(word2))==1:
                  one_diff = True
                  if len(prefix) == len(word2): # exchange
                    if diff_array[0] >= 4:
                        score = score - 1
                    else:
                        score = score - (5 - diff_array[0])
                elif len(prefix)>len(word2) and (len(prefix)-len(word2))==1:
                    pref = prefix[diff_array[0] + 1:]
                    sen = word2[diff_array[0]:]
                    result = dif(pref, sen)
                    if not result and len(pref) == len(sen):
                        one_diff=True
                        if diff_array[0] >= 3:
                          score = score - 4
                        else:
                            score=score-((10 - diff_array[0])*2)-2
                elif (len(word2)-len(prefix))==1:  # erase one character from the middle of the prefix
                    pref = prefix[diff_array[0]:]
                    sen = word2[diff_array[0] + 1:]
                    result = dif(pref, sen)
                    if not result:
                        one_diff = True
                        if diff_array[0] >= 3:
                            score = score - 2
                        else:
                            score = score - (10 - (diff_array[0]) * 2)
                if one_diff==True:
                    list_of_tuples = words_db[word2]
                    for tuple1 in list_of_tuples:
                        file = open(tuple1[1], "r")
                        line = file.readlines()[tuple1[0] - 1]
                        sentences_and_marks[line] = (score, tuple1)





    sorted_marks = dict(sorted(sentences_and_marks.items(), key=lambda item: item[1], reverse=True))
    sorted_marks = list(islice(sorted_marks.items(), 5))
    return_list = []
    for i in sorted_marks:
        return_list.append(AutoCompleteData(i[0], i[1][1][1], i[1][1][0],
                                            i[1][0]))
    return return_list


def check_if_include(sentence: list, prefix: list, original_line: str, index: int, location: tuple):
    original_prefix = (" ").join(prefix)
    score = len(original_prefix) * 2
    j = 0
    i = index
    flag = True
    length_of_prefix = len(prefix)
    num = i + length_of_prefix
    count_diff = [0] * length_of_prefix  # mark the num of words that contains a difference
    while not i == num and i >= 0 and i < len(sentence):  # pass over the words in the prefix
        if not sentence[i] == prefix[j]:  # if a word of sentence does not match the prefix's word
            flag = False
            if len(prefix[j]) < len(sentence[i]):
                diff_array = dif(prefix[j], sentence[i])
                if len(diff_array) == 0 and len(sentence[i]) - len(prefix[j]) == 1:  # erase one character from the end
                    score=score
                elif len(diff_array) == 0:
                    score = score
                elif len(diff_array) == 1 and (
                        len(prefix[j]) - len(sentence[i]) == 0):  # exchange between one character
                    count_diff[j] = 1
                    if original_prefix.index(prefix[j]) + diff_array[0] >= 4:
                        score = score - 1
                    else:
                        score = score - (5 - original_prefix.index(prefix[j]) + diff_array[0])
                else:  # erase one character from the middle of the prefix
                    pref = prefix[j][diff_array[0]:]
                    sen = sentence[i][diff_array[0] + 1:]
                    result = dif(pref, sen)
                    if not result:
                        count_diff[j] = 1  # mark the diff
                        if original_prefix.index(prefix[j]) + diff_array[0] >= 3:
                            score = score - 2
                        else:
                            score = score - (10 - (original_prefix.index(prefix[j]) + diff_array[0]) * 2)
                    else:
                        return False


            else:  # when word of prefix>=word of sentence
                diff_array = dif(sentence[i], prefix[j])
                if len(diff_array) == 0 and (len(prefix[j]) - len(sentence[i]) == 1):  # if the difference is just one character in the end
                    count_diff[j] = 1  # mark the diff
                    if original_prefix.index(prefix[j]) >= 3:
                        score = score - 4
                    else:
                        score = score - (10 - (original_prefix.index(prefix[j])) * 2) - 2
                elif len(diff_array) == 1 and (len(prefix[j]) - len(sentence[i]) == 0):  # exchange
                    count_diff[j] = 1
                    if original_prefix.index(prefix[j]) + diff_array[0] >= 4:
                        score = score - 1
                    else:
                        score = score - (5 - original_prefix.index(prefix[j]) + diff_array[0])
                else:
                    pref = prefix[j][diff_array[0] + 1:]
                    sen = sentence[i][diff_array[0]:]
                    result = dif(pref, sen)
                    if not result and len(pref) == len(sen):
                        count_diff[j] = 1
                        if original_prefix.index(prefix[j]) + diff_array[0] >= 3:
                            score = score - 4
                        else:
                            score = score - (10 - (original_prefix.index(prefix[j]) + diff_array[0]) * 2) - 2
                    else:
                        return False

        j += 1
        i += 1
    if i < 0:
        return False
    if count_diff.count(1) <= 1:  # if there was one difference between the prefix and the sentence
        flag = True
    if flag:
        sentences_and_marks[original_line] = (score, location)  # call the mark function
    return flag


def dif(word_of_sentence: str, word_of_prefix: str):  # list of specific indexes of differences
    if len(word_of_sentence) > len(word_of_prefix):
        return [i for i in range(len(word_of_prefix)) if word_of_prefix[i] != word_of_sentence[i]]
    return [i for i in range(len(word_of_sentence)) if word_of_sentence[i] != word_of_prefix[i]]


#initialize_db(path=r"C:\Users\aannr\Downloads\2021-archive\2021-archive\RFC\2.0.txt")




def main():
    initialize_db(path=r"C:\Users\aannr\Downloads\2021-archive\2021-archive\RFC\2.0.txt")  # initialize the database
    flag = False
    while not flag:
        prefix = input("The system is ready.Please Enter your text:")
        flag = True
        while flag:
            if prefix[len(prefix) - 1] == '#':
                flag = False
            print("Here are the best 5 suggestions:")
            sentences_and_marks.clear()
            best_suggestions = get_best_k_completions(prefix)
            if not best_suggestions:
                print("No matches found for your prefix")
                flag = False
            else:
                i = 0
                for suggest in best_suggestions:
                    i += 1
                    print(str(i) + ". " + suggest.completed_sentence[
                                          :suggest.completed_sentence.rindex('\n')] + " (" + suggest.source_text[
                                                                                             suggest.source_text.rindex(
                                                                                                 '\\') + 1:suggest.source_text.rindex(
                                                                                                 '.')] + " " + str(
                        suggest.offset) + ")")
                if flag:
                    prefix += input(prefix)


main()