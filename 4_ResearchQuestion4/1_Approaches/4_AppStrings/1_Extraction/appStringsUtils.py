from androguard.core.bytecodes  import apk
import xml.etree.ElementTree    as ET
import requests
import shutil
import os
import subprocess
import re
import zipfile
import time

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

# Decompile an APK using Apktool
def decompileAPK(apkPath, sha256):
    # Decompiling APK File
    cmd = 'apktool d {}{}.apk -o {}'.format(apkPath, sha256, apkPath + sha256 + "/")

    # Check if the decompiled directory exists
    if not os.path.exists(apkPath + sha256 + "/"):
        #print("EXECUTING: {}\n".format(cmd))
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

    return apkPath + sha256 + "/"

# To check if a string contains NON ASCHI Chars
def containsNonASCII(text):
    # Regex
    pattern = re.compile(r'[^\x00-\x7F]')
    if pattern.search(text):
        return True
    else:
        return False

# Extract Strings from an XML FIle
def extractStringsFromXML(xmlFile):

    try:
        # Parse the strings.xml file
        tree = ET.parse(xmlFile)
        root = tree.getroot()
    except Exception as e:
        print("⚠️ Error With XML FILE {}".format(e))
        return None
    
    # Extract the strings from the XML
    strings = []
    for string_elem in root.iter("string"):
        string_value = string_elem.text
        if string_value:
            strings.append(string_value)

    return strings


# Extract Strings from an APK
def getStringsFromAPK(sha256, apkPath):

    #print("\n🔑 APP: {}".format(sha256))

    appStrings = []

    # Download the app
    try:
        downloadAPK(apkPath, sha256)
    except Exception as e:
        print("⚠️ Error Download Androzoo {}".format(e))
        return None

    # Decompile the App
    try:
        decompiledPath = decompileAPK(apkPath,sha256)
    except Exception as e:
        print("⚠️ Error with ApkTOOL {}".format(e))
        return None
    
    # Iterate through all the directories and files in the decompiled path
    for root, dirs, files in os.walk(decompiledPath + "res/"):
        for directory in dirs:
            if directory == "values" or directory.startswith("values-") and "en" in directory:

                print("🔍 Looking inside {}".format(directory))

                for file in os.listdir(os.path.join(root,directory)):
                    if file == "strings.xml":
                        appStrings.extend(extractStringsFromXML(os.path.join(root,directory,file)))

    # Delete apk and folder
    deleteAPK(apkPath, sha256)
    deleteFolder(decompiledPath)
                
    return appStrings        