# IMPORT
from androguard.core.bytecodes  import apk
import xml.etree.ElementTree    as ET
import requests
import shutil
import os
import subprocess
import re

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
    
# Get the App Name STRING from Manifest
def extractAppNameStringFromManifest(decompiledPath):
    # Extract the app name from the manifest file
    manifestFile = os.path.join(decompiledPath, "AndroidManifest.xml")
    
    # Open the manifest file
    with open(manifestFile, "r", encoding="utf-8") as f:
        manifestContent = f.read()

    # Use regular expressions to extract the app name
    match = re.search('android:label="(.*?)"', manifestContent)

    if match:
        appNameString = match.group(1)
        return appNameString
    else:
        return None

# Find a node in the STRINGS XML TREE 
def findNodeValueInXML(XMLtree, appNameString):
    # Get Root
    root = XMLtree.getroot()
    
    # Traverse the XML tree to find the desired node
    for node in root.iter():
        if 'name' in node.attrib and node.attrib['name'] == appNameString:
            return node.text
    return None

# Get App Name from the Android Manifest
def getAppNameFromManifest(apkPath,sha256):
      
    print("🔍 Trying to use Android Manifest")

    # Decompile the App
    try:
        decompiledPath = decompileAPK(apkPath,sha256)
    except Exception as e:
        print("⚠️ Error with ApkTOOL {}".format(e))

    # Default Value for appName
    appName = None

    # Search for the appName string in the Android Manifest
    try:
        appNameString = extractAppNameStringFromManifest(decompiledPath)
    except Exception as e:
        print("⚠️ Error with Android Manifest {}".format(e))

    # Get Strings File
    stringsFile = os.path.join(os.path.join(decompiledPath, "res", "values"), "strings.xml")

    # Search for the App Name in the XML TREE of strings File
    appName = findNodeValueInXML(ET.parse(stringsFile), appNameString[8:])

    try:
        # Still Non ASCII
        if appName is not None and containsNonASCII(appName):
            # Get Strings File from VALUES-EN
            stringsFile = os.path.join(os.path.join(decompiledPath, "res", "values-en"), "strings.xml")
            appName = findNodeValueInXML(ET.parse(stringsFile), appNameString[8:])
    except Exception as e:
        print("⚠️ Values-EN not found {}".format(e))

    # Delete folder
    deleteFolder(decompiledPath)
    
    return appName

# Get App Name from Androguard, if not working use Androind Manifest
def getAppName(sha256,apkPath):

    #print("\n🔑 APP: {}".format(sha256))

    # Download the app
    try:
        downloadAPK(apkPath, sha256)
    except Exception as e:
        print("⚠️ Error Download Androzoo {}".format(e))

    # AppName Default Value
    appName = None
    
    # Load the app with Androguard and get AppName
    try:
        print("🔍 Retrieving AppName with Androguard")
        a = apk.APK(apkPath + sha256 + '.apk')
        appName = a.get_app_name()

    except Exception as e:
        # Print Error
        print("⚠️ Error with Androguard {}".format(e))

        # Try to use the Manifest File
        appName = getAppNameFromManifest(apkPath,sha256)

    # If NON ASCI CHARS use Manifest File to get AppName
    if(containsNonASCII(appName) == True):
        print("❌ NON ASCII CHARS {} - Using Android Manifest".format(appName))
        appName = getAppNameFromManifest(apkPath,sha256)

    # Print message
    if(appName != None):
        print("✅ App Name Retrieved")

    # Delete the apk file
    deleteAPK(apkPath, sha256)

    return appName