# Import
import nltk
import re

# Preprocess
def preProcess(description):
    snowballStemmer = nltk.stem.snowball.EnglishStemmer()
    englishVocab    = set(w.lower() for w in nltk.corpus.words.words())
    stopwords       = nltk.corpus.stopwords.words('english')
 
    description = re.sub(r'\W',' ',description)
    description = re.sub(r'\d','',description)
    tokens = nltk.word_tokenize(description)
    words = [snowballStemmer.stem(w) for w in tokens if len(w)>=3 and w.lower() not in stopwords and w.lower() in englishVocab]          
    preprocessedDescription = ' '.join(words)   

    return preprocessedDescription