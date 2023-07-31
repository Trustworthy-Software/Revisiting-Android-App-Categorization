# IMPORT
from PIL            import Image
from nltk.stem      import WordNetLemmatizer, PorterStemmer
from nltk.tokenize  import word_tokenize
from collections    import Counter
import os, requests
import subprocess
import pytesseract
import fnmatch
import re, shutil

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

# Get the XML Values from the decompiled APK
def getXmlValues(APK_PATH, sha256):
    # Folder with the strings.xml file
    folder_path= "{}{}/res/values".format(APK_PATH, sha256)

    xmlValues = []

    # Get the values from the strings.xml file
    for dirpath, dirs, files in os.walk(folder_path):
        for filename in fnmatch.filter(files, 'strings.xml'):
            try:
                i=0
                f=open(os.path.join(dirpath, filename), encoding='ISO-8859-1')
                for word in f:
                    stringWithQuotes = word
                    findDoubleQuotes = re.compile('">([^>]*)</',
                                                    re.DOTALL | re.MULTILINE | re.IGNORECASE)  # Ignore case not needed here, but can be useful.
                    listOfQuotes = findDoubleQuotes.findall(stringWithQuotes)
                    listOfQuotes = str (listOfQuotes)

                    listOfQuotes = re.sub(r'[^A-Za-z\s]+', "", listOfQuotes)  # Remove any single letter
                    listOfQuotes = re.sub(r"\b[a-zA-Z]\b", "", listOfQuotes)  # Remove any single letter

                    xmlValues.append(listOfQuotes)
                   
            except:
                pass

    # Remove duplicates
    xmlValues = list(set(xmlValues))

    # Keep only words with length >= 4
    xmlValues = [word.replace("\n"," ").strip() for word in xmlValues if len(word) >= 4 and len(word) <=100]

    # Sort alpahbetically
    xmlValues.sort()

    return xmlValues

# Get the text contained in the GUI of the app
def getGuiText(APK_PATH, sha256):
    
    # Folder with decompiled APK
    folder_path= "{}{}".format(APK_PATH, sha256)

    guiText = []

    # Try to open all the file as images and get text
    for dirpath, dirs, files in os.walk(folder_path):
        for filename in fnmatch.filter(files, '*.*'):
            try:
                f = Image.open(os.path.join(dirpath, filename))
                text = pytesseract.image_to_string(f, lang='eng')
        
                out_str = str(text)
                out_str = re.sub(r"\b[a-zA-Z]\b", "", out_str) #Remove any single letter
                out_str = re.sub(r'[^A-Za-z\s]+', "", out_str) #Remove any non alphabatic charecter
                out_str = out_str.replace('(', '')
                out_str = out_str.replace(')', '')
                out_str = out_str.replace(',', '')
                out_str = out_str.replace('.', '')
                out_str = out_str.replace('  ', ' ')

                guiText.append(out_str)
            except Exception as e:
                pass

    # Remove duplicates
    guiText = list(set(guiText))

    # Keep only words with length >= 4
    guiText = [word.replace("\n"," ").strip() for word in guiText if len(word) >= 4 and len(word) <=100]

    # Sort alpahbetically
    guiText.sort()

    return guiText

# Define a function to split a camel case string into separate words
def splitCamelCase(s):
        return re.sub('([a-z])([A-Z])', r'\1 \2', s).split()
    
# Get Method Names from the decompiled APK 
def getMethodNames(APK_PATH, sha256):
    # Folder with decompiled APK
    folder_path= "{}{}".format(APK_PATH, sha256)

    methodNames = []

    # Get all the mehtod names from Smali files
    for dirpath, dirs, files in os.walk(folder_path):
        for filename in fnmatch.filter(files, '*.smali'):
            f = open(os.path.join(dirpath, filename), encoding="utf8")
            for word in f:
                i = 8
                if re.match("(.*)\.method(.*)", word):
                    # Get the method name
                    methodNames.append(word.split("(")[0].replace(".method ", ""))
    

    # Split according to CamelCase convention
    methodNamesText = []
    for method in methodNames:
        methodNamesText.extend(splitCamelCase(method))

    # Read java keywords from fil
    with open('javaKeywords.txt', 'r') as f:
        javaKeywords = f.readlines()

    # Delete Java Keywords
    for i in range(0,len(methodNamesText)):
        for keyword in javaKeywords:
            methodNamesText[i] = methodNamesText[i].replace(keyword.strip(),"")
        methodNamesText[i] = methodNamesText[i].strip()    
    
    # Clean the words from space and digits
    for i in range(0,len(methodNamesText)):
        methodNamesText[i] = re.sub(r'\s\s+|\d+', '', methodNamesText[i])  # Remove multiple spaces and digits
        methodNamesText[i] = re.sub(r'\s+([a-zA-Z])', r'\1', methodNamesText[i])  # Remove spaces before letters
    
    # Remove duplicates
    methodNamesText = list(set(methodNamesText))

    # Keep only words with length >= 4
    methodNamesText = [word for word in methodNamesText if len(word) >= 4 and len(word) <=100]

    # Sort alpahbetically
    methodNamesText.sort()

    return methodNamesText

# Extract all the features (XML,GUI,MethodNames)
def getAll(sha256, APK_PATH):
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

    # Get XML Values
    xmlValues = getXmlValues(APK_PATH, sha256)
    #print(xmlValues)

    # Get GUI Text
    guiText = getGuiText(APK_PATH,sha256)
    #print(guiText)

    # Get Method Names
    methodNamesText = getMethodNames(APK_PATH, sha256)
    #print(methodNamesText)
    
    # Delete the apk and the folder
    deleteAPK(APK_PATH, sha256)
    deleteFolder(APK_PATH + '{}/'.format(sha256))

    #return xmlValues, guiText, methodNamesText
    return xmlValues, guiText, methodNamesText

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
def getMostFrequentWords(appsDF,columns):

    # Get all words in the dataset
    allWords = []
    for column in columns:
        for row in appsDF[column]:
            allWords.extend(row)

    # Get most frequent words
    FREQUENCY_TRESHOLD = 0.1
    wordCounts    = Counter(allWords)
    frequentWords = [word for word, count in wordCounts.items() if (count / len(allWords)) >= FREQUENCY_TRESHOLD]

    # print("\nAll Words : {}".format(len(allWords)))
    # print("Frequent Words : {}".format(len(frequentWords)))
    # print(frequentWords)

    # # Print some frequency stats
    # for word, count in wordCounts.most_common(5):
    #     frequency = count / len(allWords) * 100
    #     print(f"'{word}' occurs {frequency:.2f}% of the time.")

    return frequentWords

# Print some info for test purposes
def test(appsDF, column):
    # Total length for each column
    print("Total: {}".format(sum(appsDF[column].apply(lambda x: len(x)))))

    # Print an example
    test = appsDF.loc[1,column]
    test = sorted(test)
    print("Example - len: {}".format(len(test)))
    print(test[0:5])

    return 
    
# Preprocess everything using stemming,lemmatization and frequency    
def preprocess(appsDF, columns):

    # Step 1 : Tokenization
    print("\n🔨 1. Tokenization")
    for column in columns:
        # Tokenize
        appsDF[column] = appsDF[column].progress_apply(lambda x: [word_tokenize(string) for string in x])
        appsDF[column] = appsDF[column].apply( lambda lst: [item for sublist in lst for item in sublist])
        # print("\nTokenized")
        # test(appsDF,column)

    # Print Average length
    printAvgLen(appsDF,columns)

    # Step 2 : Preprocessing
    print("\n🔨 2. Stemming and Lemmatization")
    for column in columns:
        # Convert to lowercase and remove duplicates
        appsDF[column] = appsDF[column].apply(lambda x: list(set([y.lower() for y in x])))
        # print("\nLower case and duplicates")
        # test(appsDF,column)

        # Remove short words
        appsDF[column] = appsDF[column].apply(lambda x: [y for y in x if len(y) > 3 ])
        # print("\nRemove too short words")
        # test(appsDF,column)

        # Stem And Lemmatize
        appsDF[column] = appsDF[column].progress_apply(lambda x: [stemAndLemmatize(y) for y in x])
        # print("\nLemmatize and stemming")
        # test(appsDF,column)

        # Remove duplicates and sort
        appsDF[column] = appsDF[column].apply(lambda lst: list(sorted(set(lst))))
        # print("\nRemoving Duplicates and sort")
        # test(appsDF,column)
    
    # Print Average length
    printAvgLen(appsDF,columns)

    # Step 3 : Remove too frequent words
    print("\n🔨 3. Removing too frequent words")
    frequentWords = getMostFrequentWords(appsDF,columns)
    for column in columns:
        #print("\n📝 Working with: {}".format(column))

        # Remove too frequent words
        appsDF[column] = appsDF[column].progress_apply(lambda lst: [word for word in lst if word not in frequentWords])
        # print("\nRemoving frequent words")
        # test(appsDF,column)
    
    # Print Average length
    printAvgLen(appsDF,columns)

    return

# Average length of the lists given a column
def printAvgLen(appsDF, columns):

    print("\nAverage lengths:")
    for column in columns:
        avgLen = appsDF[column].apply(lambda x: len(x)).mean()
        print("-- {:15}: {}".format(column,int(avgLen)))  

    return
