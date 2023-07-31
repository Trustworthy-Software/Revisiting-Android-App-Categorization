# IMPORT
from gensim.models                  import KeyedVectors
from gensim.scripts.glove2word2vec  import glove2word2vec
from   tqdm                         import tqdm
import pandas   as pd
import numpy    as np
import nltk,re,wordnet

def remove_ascii_words(df): 
    non_ascii_words = [] 
    for i in range(len(df)): 
        for word in df.loc[i, 'Description'].split(' '): 
            if len(word)< 3 and len(word) > 15: 
                if any([ord(character) >= 128 for character in word]): 
                    non_ascii_words.append(word) 
                    df.loc[i, 'Description'] = df.loc[i, 'Description'].replace(word, '') 
    return non_ascii_words

def get_good_tokens(sentence): 
    replaced_punctation = list(map(lambda token: re.sub('[^A-Za-z]+', '', token), sentence)) 
    removed_punctation = list(filter(lambda token: token, replaced_punctation)) 
    return removed_punctation

def preprocessing(df):
    stopwords   = nltk.corpus.stopwords.words('english') 
    lemma       = nltk.stem.WordNetLemmatizer() 
    pStemmer    = nltk.stem.porter.PorterStemmer()

    remove_ascii_words(df) # Remove words with non-ASCII characters
    df['Description'] = df.Description.str.lower() # Convert text to lowercase
    df['Description'] = df['Description'].replace(r'http\S+', '', regex=True).replace(r'www\S+', '', regex=True) # Remove URLs from text
    df['document_sentences'] = df.Description.str.split('.') # Split texts into individual sentences
    df['tokenized_sentences'] = list(map(lambda sentences: list(map(nltk.word_tokenize, sentences)), df.document_sentences)) # Tokenize sentences
    df['tokenized_sentences'] = list(map(lambda sentences: list(map(get_good_tokens, sentences)), df.tokenized_sentences)) # Remove unwanted characters
    df['tokenized_sentences'] = list(map(lambda sentences: list(filter(lambda lst: lst, sentences)), df.tokenized_sentences)) # Remove empty lists
    df['stop'] = '' # Initialize stop column
    for i in range(len(df)):
        df.stop[i] = list(map(lambda doc: [word for word in doc if word not in stopwords], df.loc[i, 'tokenized_sentences'])) # Remove stopwords
    df['lemm'] = '' # Initialize lemm column
    for i in range(len(df)):
        df.lemm[i] = list(map(lambda sentence: list(map(lemma.lemmatize, sentence)), df.loc[i, 'stop'])) # Lemmatize text
    df['stem'] = '' # Initialize stem column
    for i in range(len(df)):
        df.stem[i] = list(map(lambda sentence: list(map(pStemmer.stem, sentence)), df.loc[i, 'lemm'])) # Stem text

def getEmbeddingFeatures(model, sentence_group):
    not_included = []
    featureVec = np.zeros(model.vector_size, dtype="float32")
    nwords = 0
    
    words = np.concatenate(sentence_group)
    index2word_set = set(model.wv.vocab.keys())
    
    for word in words:
        if word in index2word_set and len(word) > 2:
            featureVec = np.add(featureVec, model[word])
            nwords += 1.
        if word not in index2word_set:
            not_included.append(word)
    
    if nwords > 0:
        featureVec = np.divide(featureVec, nwords)
    
    return featureVec