# IMPORT
import sys
sys.path.append("Modules")

from androguard.misc            import AnalyzeAPK
import BasicBlockAttrBuilder    as BasicBlockAttrBuilder
import PScoutMapping            as PScoutMapping
import os, re, time
import psutil, logging
import requests ,argparse
import requests
import shutil
import os
import subprocess
import re
import drebinGetApkData

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

# Get list of all the APIs
def getApisList(sha256, apkPath):

    #print("\n⛏️ Working on : {}".format(sha256))

    # Download the app
    try:
        downloadAPK(apkPath, sha256)
    except Exception as e:
        print("⚠️ Error Download Androzoo {}".format(e))
        return None

    # Empty list
    apisList = []

    # Analyize the app
    try:
        ApkFile = os.path.abspath(apkPath + '{}.apk'.format(sha256))
        a, d, dx = AnalyzeAPK(ApkFile)
    except Exception as e:
        print("⚠️ Error with Androguard {}".format(e))
        return None
    
    # Get all the APIs call from DEX
    for _dex in d:
        for method in _dex.get_methods():
            g = dx.get_method(method)
            for BasicBlock in g.get_basic_blocks().get():
                Instructions = BasicBlockAttrBuilder.GetBasicBlockDalvikCode(BasicBlock)
                
                ApisDictList, SuspiciousApisSet = BasicBlockAttrBuilder.GetInvokedAndroidApis(Instructions)   

                # Iterate over each dictionary in the list
                for ApisDict in ApisDictList:

                    ApiClass = ApisDict['ApiClass']
                    ApiName  = ApisDict['ApiName']
                    fullApi  = ApiClass + "." + ApiName
                    
                    # Append the combined name to the list
                    apisList.append(fullApi)

    print("✅ Extraction done - Len of APIs List: {}".format(len(apisList)))

    # Delete APK
    deleteAPK(apkPath, sha256)

    return apisList

# Get list of APIs protected by Permissions
def getRestrictedApisList(sha256, apkPath):

    #print("\n⛏️ Working on : {}".format(sha256))

    # Download the app
    try:
        downloadAPK(apkPath, sha256)
    except Exception as e:
        print("⚠️ Error Download Androzoo {}".format(e))
        return None

    # Empty list
    restrictedApisList = []

    # Analyize the app
    try:
        ApkFile = os.path.abspath(apkPath + '{}.apk'.format(sha256))
        a, d, dx = AnalyzeAPK(ApkFile)
    except Exception as e:
        print("⚠️ Error with Androguard {}".format(e))
        return None
    
    # Get Permissions
    RequestedPermissionSet, ActivitySet, ServiceSet, ContentProviderSet, BroadcastReceiverSet, HardwareComponentsSet,IntentFilterSet = drebinGetApkData.GetFromXML(apkPath, apkPath + "{}.apk".format(sha256))
    
    CWD = os.getcwd()
    os.chdir(os.path.join(CWD, "Modules"))
    PMap = PScoutMapping.PScoutMapping()
    os.chdir(CWD)

    # Get all the APIs call from DEX
    for _dex in d:
        for method in _dex.get_methods():
            g = dx.get_method(method)
            for BasicBlock in g.get_basic_blocks().get():
                Instructions = BasicBlockAttrBuilder.GetBasicBlockDalvikCode(BasicBlock)
                
                ApisDictList, SuspiciousApisSet = BasicBlockAttrBuilder.GetInvokedAndroidApis(Instructions)   

                Permissions, RestrictedApis = BasicBlockAttrBuilder.GetPermissionsAndApis(ApisDictList, PMap, list(RequestedPermissionSet))

                restrictedApisList.extend(list(RestrictedApis))

                # # Iterate over each dictionary in the list
                # for ApisDict in ApisDictList:

                #     ApiClass = ApisDict['ApiClass']
                #     ApiName  = ApisDict['ApiName']
                #     fullApi  = ApiClass + "." + ApiName
                    
                #     # Append the combined name to the list
                #     apisList.append(fullApi)

    #print(restrictedApisList)
    print("✅ Extraction done - Len of APIs List: {}".format(len(restrictedApisList)))

    # Delete APK
    deleteAPK(apkPath, sha256)

    return restrictedApisList