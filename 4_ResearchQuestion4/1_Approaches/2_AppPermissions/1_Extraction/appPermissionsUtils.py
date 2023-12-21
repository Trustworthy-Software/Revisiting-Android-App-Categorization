from androguard.core.bytecodes  import apk
import requests
import shutil
import os
import subprocess
import re

### API KEYS ###
from dotenv import load_dotenv
load_dotenv()
ANDROZOO_API_KEY = os.getenv('ANDROZOO_API_KEY')
OPENAI_API_KEY   = os.getenv('OPENAI_API_KEY')

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

# Get features from Drebin Data
def getUsedPermission(sha256, drebinPath):
    # Search for file
    drebinDataPath = os.path.join(drebinPath, sha256 + ".data")

    # Read fetures from Drebin File
    with open(drebinDataPath, 'r') as f:
        lines = f.readlines()
        features = [line.strip() for line in lines]

    # Filter features
    features = [x for x in features if x.startswith('UsedPermissionsList')]
    
    return features

# Get features from Drebin Data
def getRequestedPermission(sha256, drebinPath):
    # Search for file
    drebinDataPath = os.path.join(drebinPath, sha256 + ".data")

    # Read fetures from Drebin File
    with open(drebinDataPath, 'r') as f:
        lines = f.readlines()
        features = [line.strip() for line in lines]

    # Filter features
    features = [x for x in features if x.startswith('RequestedPermissionList')]

    return features