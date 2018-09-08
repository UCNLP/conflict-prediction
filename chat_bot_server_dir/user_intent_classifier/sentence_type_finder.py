import nltk
from stanfordcorenlp import StanfordCoreNLP

def sentence_preprocess(sentence):
    # User 이름, 파일명 제외하고는 전체 문장 소문자화 하기.
    extension_list = [".py", ".py.", ".md", ".md.", ".txt", ".txt.", ".json", ".json."]
    word_list = sentence.split()
    for word in word_list:
        len_word = len(word)
        # user name
        if word[0:2] == "@" and (word[len_word-1] == ">" or word[len_word-3:len_word] == ">'s"):
            pass
        # file name
        elif word[len_word-3:len_word] in extension_list or word[len_word-4:len_word] in extension_list \
                or word[len_word-5:len_word] in extension_list or word[len_word-6:len_word] in extension_list:
            pass
        else:
            word_list[word_list.index(word)] = word.lower()

    sentence = ' '.join(word_list)

# sentence = sentence[0].lower() + sentence[1:]
    sentence = sentence.replace("please ", '')
# sentence = sentence.replace("Please ", '')
# sentence = sentence.replace("I think ", '')
    sentence = sentence.replace("i think ", '')
    sentence = sentence.replace("have to", "should")
    sentence = sentence.replace("don't have to", "shouldn\'t")
    sentence = sentence.replace("do not have to", "shouldn\'t")

    return sentence

def is_command(_sentence):
    nlp = StanfordCoreNLP('http://localhost', port=9000)
    # sentence 제일 앞에 modal 추가, _sentence 제일 첫 글자 소문자화(대신, 파일명, 사용자명은 바꾸면 안됨.)
    sentence = "Must " + _sentence[0].lower() + _sentence[1:]
    pos_tag_list = nlp.pos_tag(sentence)

    for pos_tag in pos_tag_list:
        if pos_tag[1] == "RB" or pos_tag[1] == "MD":
            pass
        elif pos_tag[1] == "VB" or pos_tag[1] == "VBP":
            return True
        else:
            return False

def is_desire(pos_tag_list):
    ignore_pos_list = ["PRP", "NN","NNP", "RB", ",","!",'.']
    desire_list = ["want", "hope", "wish", "desire", "need", "like"]

    for pos_tag in pos_tag_list:

        if pos_tag[1] in ignore_pos_list: #do : VBP
            pass
        elif pos_tag[0] in desire_list:
            return True
        else:
            return False

def is_suggestion(pos_tag_list):

    suggestion_noun_list = ["Sayme", "sayme", "You", "you", "SAYME",".",","]
    for pos_tag in pos_tag_list:
        if pos_tag[0] in suggestion_noun_list:
            pass
        elif pos_tag[1] == "MD":
            return True
        else:
            return False

def is_question(parse_list):
    if "SBARQ" in parse_list or "SQ" in parse_list:
        return True
    return False

def require_something_sentence(_sentence):
    nlp = StanfordCoreNLP('http://localhost', port=9000)
    sentence = sentence_preprocess(_sentence)
    pos_tag_list = nlp.pos_tag(sentence)
    parse_list = nlp.parse(sentence)
    if is_question(parse_list):
        return 1
    elif is_command(sentence):
        return 2
    elif is_suggestion(pos_tag_list):
        return 3
    elif is_desire(pos_tag_list):
        return 4
    else:
        return 5

