# Import
from androguard.core.bytecodes.apk  import APK as androguardAPK
from PIL                            import Image
import xml.etree.ElementTree        as ET
import os, requests, subprocess
import pytesseract, fnmatch
import re, spacy
import shutil
import zipfile
import cv2
import numpy as np
import time

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

# Counting files in a folder
def countFiles(folderPath):
    count = 0
    for _, _, files in os.walk(folderPath):
        count += len(files)
    return count

# Merge BG and FG
def mergeImages(foregroundPath, backgroundPath, outputPath):

    # Read the foreground and background images with alpha channels
    foreground = cv2.imread(foregroundPath, cv2.IMREAD_UNCHANGED)
    background = cv2.imread(backgroundPath)

    # Resize the background image to match the foreground's dimensions
    background = cv2.resize(background, (foreground.shape[1], foreground.shape[0]))

    # Extract the alpha channel from the foreground image
    alpha = foreground[:, :, 3] / 255.0

    # Expand the alpha channel to three color channels
    alpha = np.dstack([alpha] * 3)

    # Multiply the foreground with the alpha channel
    foreground = foreground[:, :, :3] * alpha

    # Multiply the background with (1 - alpha)
    background = background * (1 - alpha)

    # Add the foreground and background to get the merged image
    merged_image = foreground + background

    # Save the merged image
    cv2.imwrite(outputPath, merged_image)

# Search for a file in a folder and its subfolders
def searchFile(startPath, fileName):
    for root, _, files in os.walk(startPath):
        if fileName in files:
            return os.path.join(root, fileName)
    return None

# Search for a file in a folder given a substring
def searchFileWithSubstring(startPath, substring):
    for root, dirs, files in os.walk(startPath):
        for file in files:
            if substring in file:
                return os.path.join(root, file)

# Search for the icon when getting None from the other approaches
def searchIconWhenNone(startPath, fileName):
    print("⛏️ 3) Looking for any PNG file containing: {} ".format(fileName))

    for root, _, files in os.walk(startPath):
        for file in files:
            if fileName in file and file.lower().endswith('.png'):
                if "foreground" in file or "background" in file:
                    print("⛏️ 3) Merging FG and BG to get a full Icon")

                    fgPath  = searchFileWithSubstring(root, "foreground")
                    bgPath  = searchFileWithSubstring(root, "background")
                    outPath = os.path.join(root, fileName + ".png")
                    mergeImages(fgPath,bgPath, outPath)
                    return os.path.join(root, fileName + ".png")
                if "round" in file:
                    print("⛏️ 3) Round Icon Found")
                    return os.path.join(root, file)
                
    return None

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

# Decompile an APK using JADX
def decompileAPKwithJADX(apkPath, sha256):
    # Decompiling APK File
    cmd = 'jadx -d {} {}{}.apk'.format(apkPath + sha256 + "/",apkPath, sha256)

    # Check if the decompiled directory exists
    if not os.path.exists(apkPath + sha256 + "/"):
        print("EXECUTING: {}\n".format(cmd))
        results = subprocess.run(cmd.split(), stdout=subprocess.PIPE,shell=True)
        #output, error = process.communicate()
        time.sleep(30)

    return apkPath + sha256 + "/"

# Unzip the APK as a normal ZIP Archive
def unzipAPK(apkPath, sha256):
    os.rename(apkPath + sha256 + ".apk", apkPath + sha256 + ".zip")
    # Extract the contents of the ZIP file
    with zipfile.ZipFile(apkPath + sha256 + ".zip", 'r') as zipRef:
        zipRef.extractall(apkPath + sha256 + "/")

    return apkPath + sha256 + "/"

# Get the iconFileName looking at th emanifest
def getIconFileNameFromManifest(manifestPath):
    # Open the XML file
    tree = ET.parse(manifestPath)
    root = tree.getroot()

    # Define the tag and field you want to search for
    tagToSearch   = 'application'  
    fieldToSearch = '{http://schemas.android.com/apk/res/android}icon' 

    # Search for the tag and field
    for tag in root.iter(tagToSearch):
        for field in tag.attrib:
            if field == fieldToSearch:
                iconPath = tag.attrib[field]
    
    return iconPath.split("/")[-1] + ".png"

# Get the Icon in a different way
def getIconAlternative(apkPath, sha256, outputDir):

    iconPath = None
    decompiledPath = None
    try:
        # Decompile the APK using ApkTool and 
        decompiledPath = decompileAPKwithJADX(apkPath, sha256)

        # get iconName from the manifest
        iconFile = getIconFileNameFromManifest(decompiledPath + "AndroidManifest.xml")

        print("⛏️ 2) Searching for: {}".format(iconFile))

        # Geth the path to the icon 
        iconPath = searchFile(decompiledPath, iconFile)
 
        # If not None
        if iconPath != None:
            print("✅ 2) Apktool + Manifest OK")
            print("⛏️ 2) Path: {}".format(iconPath))
        # Try to see if you can get something similar
        if iconPath == None:
            print("❌ 2) None Path ")
            print("⛏️ 3) Search for files containing the filename as a substring")
            iconPath = searchIconWhenNone(decompiledPath, iconFile[:-4])

            if iconPath != None:
                print("✅ 3) Apktool + Manifest + Similarity OK")
                print("⛏️ 3) Path: {}".format(iconPath))
            else:
                print("❌ 3) None Path ")

    except Exception as e:
        print("⚠️ Error 2: {}".format(e))
        
    # Copy the Icon
    try:
        shutil.move(iconPath, outputDir + sha256 + ".png")
    except Exception as e:
        print("⚠️ Error 3: {}".format(e))

    # Delete the folder with the decompiled APK
    deleteFolder(decompiledPath)

# To extract the icon of a given app
def extractIcon(sha256, apkPath, outputDir):

    print("\n⛏️ App : {}".format(sha256))
    outputPath = os.path.join(outputDir, '{}.png'.format(sha256))
    if os.path.exists(outputPath):
        print("⏭️ Skip")
    else:
        try:
            # Download the apk 
            downloadAPK(apkPath, sha256)
            # Open the APK file
            with zipfile.ZipFile(apkPath + sha256 + ".apk", 'r') as apkZip:
                # Get the path to the icon file using Androguard
                print("⛏️ 1) Use Androguard to retrieve the iconPath")
                apk = androguardAPK(apkPath + sha256 + ".apk")
                iconPath = apk.get_app_icon()

                # Not None
                if iconPath != None:
                    # PNG Found
                    if iconPath.lower().endswith(".png"):
                        print("✅ 1) Androguard OK")
                        print("⛏️ 1) Path: {}".format(iconPath))
                        with apkZip.open(iconPath) as iconFile, open(outputPath, 'wb') as outputFile:
                            outputFile.write(iconFile.read())  
                    # XML Found
                    if iconPath.lower().endswith(".xml"):
                        print("❌ 1) XML Found")
                        print("⛏️ 2) Use Apktool to retrieve the iconPath from the Manifest")
                        getIconAlternative(apkPath, sha256, outputDir)
                # None Path            
                else:
                    print("❌ 1) NonePath Found")
                    print("⛏️ 2) Use Apktool to retrieve the iconPath from the Manifest")
                    getIconAlternative(apkPath, sha256, outputDir)

                # delete the Apk
                deleteAPK(apkPath, sha256)

        except Exception as e:
            print("⚠️ Error 1: {}".format(e))

        