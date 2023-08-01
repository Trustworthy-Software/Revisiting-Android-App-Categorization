# Imports
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

# Load text file into a list wher evey item is a line
def loadTxtFile(filePath):
    lines = []  
    with open(filePath , 'r') as file:
        for line in file:
            lines.append(line.strip())

    return lines

# Decompile an APK using JADX
def decompileAPKwithJADX(apkPath, sha256):
    # Decompiling APK File
    cmd = 'jadx -d {} {}{}.apk'.format(apkPath + sha256 + "/",apkPath, sha256)

    # Check if the decompiled directory exists
    if not os.path.exists(apkPath + sha256 + "/"):
        print("⚡ Running JADX")
        try:
            subprocess.run(cmd, shell = True, timeout = 600)
        except subprocess.TimeoutExpired:
            print("⌛ Decompilation timed out")
            return None
    else:
        print("⏭️ Already Decompiled")
        
    return apkPath + sha256 + "/"

# Get list of imports that could be libraries
def getPotentialLibsList(decompiledPath):

    # Define your regex pattern
    regexForImport = r"import\s+([.\w]*)\s*;"

    potentialLibsList = []

    # Traverse the directory and process each Java file
    for root, dirs, files in os.walk(decompiledPath):
        for fileName in files:
            if fileName.endswith(".java"):
                filePath = os.path.join(root, fileName)
                
                # Open the Java file and read its contents
                with open(filePath, "r") as file:
                    fileContent = file.read()
                    
                    # Apply the regex pattern to the file content
                    matches = re.findall(regexForImport, fileContent)
                    
                    # Do something with the matches found
                    for match in matches:
                        potentialLibsList.append(match)
                        #print("Match:", match)

    return sorted(list(set(potentialLibsList)))

# Get list of all the libraries
def getLibraries(potentialLibsList, whiteList):

    librariesSet = set()

    # Check in the whitelist of libraries
    for potentialLib in potentialLibsList:
        for lib in whiteList:
            if potentialLib.startswith(lib + "."):
                # Split the rest of the possibleLib statment
                subLibs = potentialLib.replace(lib + ".","").split(".")
                #print("{} + {}".format(lib,str(subLibs)))

                # I have a class...
                if(len(subLibs)==1):
                    #print("{} + {}".format(lib,str(subLibs)))
                    librariesSet.add(lib)
                # I have a lib...
                else:
                    librariesSet.add(lib + "." + subLibs[0])
                break
    
    return sorted(list(librariesSet))

# Get list of system libraries
def getSystemLibraries(potentialLibsList, whiteList):

    systemLibrariesSet = set()

    # Check in the whitelist of libraries
    for potentialLib in potentialLibsList:
        for lib in whiteList:
            if potentialLib.startswith(lib + "."):
                # Split the rest of the possibleLib statment
                subLibs = potentialLib.replace(lib + ".","").split(".")
                #print("{} + {}".format(lib,str(subLibs)))

                # I have a class...
                if(len(subLibs)==1):
                    #print("{} + {}".format(lib,str(subLibs)))
                    systemLibrariesSet.add(lib)
                # I have a lib...
                else:
                    systemLibrariesSet.add(lib + "." + subLibs[0])
                break
    
    return sorted(list(systemLibrariesSet))

# EXtract Libraries from APK
def getLibrariesFromApk(sha256, apkPath, whitelistLibrariesList, systemWhitelistLibrariesList):

    #print("\n⛏️ Working on {}".format(sha256))

    # Download the app
    downloadAPK(apkPath, sha256)

    # Decompile the app with JADX
    decompiledPath = decompileAPKwithJADX(apkPath, sha256)

    potentialLibsList = []

    if decompiledPath is not None:

        # Get all the import
        potentialLibsList = getPotentialLibsList(decompiledPath)
        print("\n#️⃣ Potential Libraries: {}".format(len(potentialLibsList)))

        # Get Libraries
        #librariesList = getLibraries(potentialLibsList, whitelistLibrariesList)
        #print("#️⃣ LIBRARIES          : {}".format(len(librariesList)))
        
        # Get SystemLibraries
        #systemLibrariesList = getSystemLibraries(potentialLibsList, systemWhitelistLibrariesList)
        #print("#️⃣ SYSTEM LIBRARIES   : {}".format(len(systemLibrariesList)))

        # Delete eFolder
        deleteFolder(decompiledPath)

    # Delete APK
    deleteAPK(apkPath, sha256)

    return potentialLibsList    