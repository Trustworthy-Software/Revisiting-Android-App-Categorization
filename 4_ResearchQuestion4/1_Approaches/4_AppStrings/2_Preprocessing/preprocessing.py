# Import
from nltk                   import pos_tag
from nltk.corpus            import stopwords
from nltk.corpus            import wordnet
from nltk.stem              import SnowballStemmer
from nltk.stem.wordnet      import WordNetLemmatizer
from nltk.tokenize          import word_tokenize
import re
import string
import enchant
import os

# Remove all html tags from text
def remove_html(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

# Remove all words that are not in the US+GB dictionary
def remove_non_english(text):
    d_us = enchant.Dict("en_US")
    d_gb = enchant.Dict("en_GB")
    # build custom dict
    alt_dicts = []
    for d_file in os.listdir('no-filter-dict'):
        with open(os.path.join('no-filter-dict', d_file), 'r') as ff:
            list_terms = ff.read().lower().split()
            alt_dicts.extend(list_terms)
    new_text = ''
    for t in text.split():
        # if text is eith in US or GB english dict keep it
        if d_us.check(t) or d_gb.check(t):
            new_text = new_text + t + " "
            continue
        if t in alt_dicts:
            new_text = new_text + t + " "
            continue
    return new_text

# Replace non ascii chars with spaces
def remove_non_ascii(text):
    printable = set(string.printable)
    return filter(lambda x: x in printable, text)

# Replace punctuation chars '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~' with spaces
def remove_punctuation(text):
    return ''.join(map(lambda c: ' ' if c in string.punctuation else c, text))

# Remove words with no meaning or irrelevant for searching
def remove_stopwords(text):

    return ' '.join([s for s in text.split() if s not in
                     stopwords.words('english')])

# Extracts the root of every word 
def apply_stemming(text):
    stemmer = SnowballStemmer("english")
    tokens = word_tokenize(text)
    stemmed_tokens = map(stemmer.stem, tokens)
    return ' '.join(stemmed_tokens)

# Part of speech
def wordnet_pos_code(tag):
    if tag.startswith('NN'):
        return wordnet.NOUN
    elif tag.startswith('VB'):
        return wordnet.VERB
    elif tag.startswith('JJ'):
        return wordnet.ADJ
    elif tag.startswith('RB'):
        return wordnet.ADV
    else:
        return wordnet.NOUN  # default value

# Lemmatize
def apply_lemmatization(text):
    lmtzr = WordNetLemmatizer()
    tokens = word_tokenize(text)
    pos_tokens = pos_tag(tokens)
    lemm_tokens = []
    for token, pos in pos_tokens:
        w = lmtzr.lemmatize(token, wordnet_pos_code(pos))
        lemm_tokens.append(w)
    return ' '.join(lemm_tokens)

# Remove numbers from text
def remove_numbers(text):
    
    clean = re.compile('[0-9]')
    return re.sub(clean, '', text)

# Text to lowercase, for stopwords and stuff
def do_lowercase(text):  
    return text.lower()

# Preprocess
def preprocessText(text):

    #print(text)

    # Apply all the steps
    text = remove_html(text)
    text = remove_non_ascii(text)
    text = remove_punctuation(text)
    text = do_lowercase(text)
    text = remove_numbers(text)
    text = remove_stopwords(text)

    text = remove_non_english(text)
    text = apply_lemmatization(text)
    text = apply_stemming(text)

    return text

######### FREQUENCY ############

def printMostFrequentWords(counter):
    # SGet most Frequent words
    mostFrequentWords = counter.most_common()

    print(mostFrequentWords)

def getMostFrequentWords(counter, N):
    # SGet most Frequent words
    frequentWords = counter.most_common(N)
    mostFrequentWords = []

    for item in frequentWords:
        mostFrequentWords.append(item[0])

    return mostFrequentWords

def printMostFrequentWordsPercentage(counter):
    # Get tot number of words
    totalWords = sum(counter.values())

    # Calculate the percentage of each string occurrence
    percentages = [(word, count/totalWords * 100) for word, count in counter.items()]

    # Sort the percentages in descending order
    percentages.sort(key=lambda x: x[1], reverse=True)

    # Print the strings and their corresponding percentages
    for word, percentage in percentages:
        print(f"{word}: {percentage:.4f}%")

def getMostFrequentWordsByPercentage(counter, frequencyThreshold):
    # Get tot number of words
    totalWords = sum(counter.values())

    # Calculate the percentage of each string occurrence
    percentages = [(word, count/totalWords * 100) for word, count in counter.items()]

    # Filter words above the threshold
    frequentWords = [(word, percentage) for word, percentage in percentages if percentage >= frequencyThreshold]

    # Sort the common words by percentage in descending order
    frequentWords.sort(key=lambda x: x[1], reverse=True)

    mostFrequentWords = []

    for item in frequentWords:
        mostFrequentWords.append(item[0])

    return mostFrequentWords

def getLessFrequentWordsByPercentage(counter, frequencyThreshold):
    # Get tot number of words
    totalWords = sum(counter.values())

    # Calculate the percentage of each string occurrence
    percentages = [(word, count/totalWords * 100) for word, count in counter.items()]

    # Filter words above the threshold
    frequentWords = [(word, percentage) for word, percentage in percentages if percentage <= frequencyThreshold]

    # Sort the common words by percentage in descending order
    frequentWords.sort(key=lambda x: x[1], reverse=True)

    lessFrequentWords = []

    for item in frequentWords:
        lessFrequentWords.append(item[0])

    return lessFrequentWords