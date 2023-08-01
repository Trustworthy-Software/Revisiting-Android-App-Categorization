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

# Part of Speech Detection
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

# Lemmatization
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

# Preprocess Descriptions
def preprocessDescription(description):

    # Apply all the steps
    description = remove_html(description)
    description = remove_non_ascii(description)
    description = remove_punctuation(description)
    description = do_lowercase(description)
    description = remove_numbers(description)
    description = remove_stopwords(description)
    description = remove_non_english(description)
    description = apply_lemmatization(description)

    return description
