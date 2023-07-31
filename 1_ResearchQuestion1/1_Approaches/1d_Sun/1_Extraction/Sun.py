from androguard.core.bytecodes.apk   import APK
from PIL                             import Image
from nltk.stem                       import WordNetLemmatizer, PorterStemmer
from nltk.tokenize                   import word_tokenize
from collections                     import Counter
from nltk.corpus                     import words
from nltk.corpus                     import stopwords
import os, requests, subprocess
import pytesseract, fnmatch
import re, spacy
import shutil
import nltk

################## API KEYS ########################
from   dotenv import load_dotenv
import os,sys
# Load API KEYS from the .env file in the current directory
CONFIG_PATH = "../../../../config.env"
if not os.path.exists(CONFIG_PATH):
    print(f"⚠️ Error: File not found at path '{CONFIG_PATH}'.\n- Make sure the config.env file exists.\n- Ensure the CONFIG_PATH is correctly set.")
    sys.exit(1)
else:
    load_dotenv(CONFIG_PATH)
ANDROZOO_API_KEY = os.getenv('ANDROZOO_API_KEY')
OPENAI_API_KEY   = os.getenv('OPENAI_API_KEY')
#######################################################

# To download APK from AndroZoo
def downloadAPK(APK_PATH, sha256):
    # Download APK from Androzoo
    apkUrl = "https://androzoo.uni.lu/api/download?apikey={}&sha256={}".format(ANDROZOO_API_KEY, sha256)
    req = requests.get(apkUrl, allow_redirects=True)
    open(APK_PATH + '{}.apk'.format(sha256), "wb").write(req.content)

# To delete an APK once finished analyzing it
def deleteAPK(APK_PATH, sha256):
    # Remove apk and xml file
    os.remove(APK_PATH + '{}.apk'.format(sha256))

# To delete a folder given a specifc path
def deleteFolder(path):
    shutil.rmtree(path)

# Define a function to split a camel case string into separate words
def splitCamelCase(s):
    return re.sub('([a-z])([A-Z])', r'\1 \2', s).split()

# Function to split snake case strin into separate words
def splitSnakeCase(s):
    return re.split('_+', s)
    
# Extract strings from App resources directory
def extractStrings(apkDir):
    strings = []
    for root, dirs, files in os.walk(apkDir):
        for file in files:
            if file.endswith('.xml') or file.endswith('.smali'):
                filePath = os.path.join(root, file)
                with open(filePath, 'r', encoding='utf-8') as f:
                    try:
                        content = f.read()
                        strings.extend(findStrings(content))
                    except UnicodeDecodeError as e:
                        pass

    # Split according to CamelCase convention
    rawStrings = []
    for s in strings:
        rawStrings.extend(splitSnakeCase(s))    
    
    # Clean the words from space and digits
    for i in range(0,len(rawStrings)):
        rawStrings[i] = re.sub(r'\s\s+|\d+', '', rawStrings[i])  # Remove multiple spaces and digits
        rawStrings[i] = re.sub(r'\s+([a-zA-Z])', r'\1', rawStrings[i])  # Remove spaces before letters
    
    # Remove duplicates
    rawStrings = list(set(rawStrings))

    # Keep only words with length >= 4
    rawStrings = [word for word in rawStrings if len(word) >= 4 and len(word) <=100]

    # Sort alpahbetically
    rawStrings.sort()
    
    return rawStrings

# Find strings
def findStrings(content):
    strings = []
    start = 0
    while True:
        startQuote = content.find('"', start)
        if startQuote == -1:
            break
        endQuote = content.find('"', startQuote + 1)
        if endQuote == -1:
            break
        string = content[startQuote + 1:endQuote]
        strings.append(string)
        start = endQuote + 1
    return strings

# Extract all the strings from an APK
def extractStringsFromAPK(sha256, APK_PATH):

    # Download the apk
    #print("\n🔑  Analyzing: {}".format(sha256))
    downloadAPK(APK_PATH, sha256)

    # Decompiling APK File
    cmd = 'apktool d {}{}.apk -o {}'.format(APK_PATH, sha256, APK_PATH + sha256 + "/")

    # Check if the decompiled directory exists
    if not os.path.exists(APK_PATH + sha256 + "/"):
        #print("EXECUTING: {}\n".format(cmd))
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
    
    # Extract Strings
    rawStrings = extractStrings(APK_PATH + sha256 + "/")
    #print(rawStrings)

    # Delete the apk and the folder
    deleteAPK(APK_PATH, sha256)
    deleteFolder(APK_PATH + '{}/'.format(sha256))

    return rawStrings

# Stem and Lemmatize a token
def stemAndLemmatize(token):
    
    # Initialize the lemmatizer and stemmer
    lemmatizer = WordNetLemmatizer()
    stemmer    = PorterStemmer()
    
    # Stem and Lemmatize
    lemmatizedToken = lemmatizer.lemmatize(token)
    stemmedToken    = stemmer.stem(lemmatizedToken)

    return stemmedToken

# Get the most frequent Words
def getMostFrequentWords(appsDF,column):

    # Get all words in the dataset
    allWords = []
    for row in appsDF[column]:
        allWords.extend(row)

    # Get most frequent words
    FREQUENCY_TRESHOLD = 0.05
    wordCounts    = Counter(allWords)
    frequentWords = [word for word, count in wordCounts.items() if (count / len(allWords)) >= FREQUENCY_TRESHOLD]

    # print("\nAll Words : {}".format(len(allWords)))
    print("\nFrequent Words : {}".format(len(frequentWords)))
    print(frequentWords)

    # Print some frequency stats
    for word, count in wordCounts.most_common(5):
        frequency = count / len(allWords) * 100
        print(f"'{word}' occurs {frequency:.2f}% of the time.")

    return frequentWords

# Print Progress while preprocessing
def printProgress(appsDF,column):
    # Total length for each column
    print("Total: {}".format(sum(appsDF[column].apply(lambda x: len(x)))))

    # Print an example
    test = appsDF.loc[0,column]
    test = sorted(test)
    print("Example - len: {}".format(len(test)))
    print(test[0:20])

# Preprocess raw strings
def preprocess(appsDF, column):

    # Step 1 : Tokenization
    print("\n🔨 1. Tokenization")
    appsDF[column] = appsDF[column].progress_apply(lambda x: [word_tokenize(string) for string in x])
    appsDF[column] = appsDF[column].apply( lambda lst: [item for sublist in lst for item in sublist])
    #print("\nTokenized")
    #printProgress(appsDF,column)

    # Convert to lowercase and remove duplicates
    appsDF[column] = appsDF[column].apply(lambda x: list(set([y.lower() for y in x])))
    #print("\nLower case and duplicates")
    #printProgress(appsDF,column)

    # Print Average length
    printAvgLen(appsDF,column)

    # Step 3: Remove non-English tokens
    print("\n🔨 2. Removing non-English tokens")
    english_words = set(words.words())
    appsDF[column] = appsDF[column].progress_apply(lambda lst: [token for token in lst if token.lower() in english_words])
    #print("\nNon-English tokens removed")
    #printProgress(appsDF, column)

    # Remove short words
    appsDF[column] = appsDF[column].apply(lambda x: [y for y in x if len(y) > 3 ])
    #print("\nRemove too short words")
    #printProgress(appsDF,column)

    # Print Average length
    printAvgLen(appsDF,column)

    print("\n🔨 3. Stemming and lemmatization")
    # Stem And Lemmatize
    appsDF[column] = appsDF[column].progress_apply(lambda x: [stemAndLemmatize(y) for y in x])
    #print("\nLemmatize and stemming")
    #printProgress(appsDF,column)

    # Remove duplicates and sort
    appsDF[column] = appsDF[column].apply(lambda lst: list(sorted(set(lst))))
    #print("\nRemoving Duplicates and sort")
    #printProgress(appsDF,column)

    # Print Average length
    printAvgLen(appsDF,column)

    # Step 3: Remove stopwords
    print("\n🔨 4. Removing stopwords")
    stopwordsList = set(stopwords.words("english"))
    appsDF[column] = appsDF[column].progress_apply(lambda lst: [token for token in lst if token.lower() not in stopwordsList])
    
    # Print Average length
    printAvgLen(appsDF,column)

    # Step 3 : Remove too frequent words
    print("\n🔨 5. Removing too frequent words")
    frequentWords = getMostFrequentWords(appsDF,column)
    appsDF[column] = appsDF[column].progress_apply(lambda lst: [word for word in lst if word not in frequentWords])
    # print("\nRemoving frequent words")
    # test(appsDF,column)

    # Print Average length
    printAvgLen(appsDF,column)
    
    return 

# Average length of the lists given a column
def printAvgLen(appsDF, column):

    print("\nAverage lengths:")
    avgLen = appsDF[column].apply(lambda x: len(x)).mean()
    print("-- {:15}: {}".format(column,int(avgLen)))  

    return
