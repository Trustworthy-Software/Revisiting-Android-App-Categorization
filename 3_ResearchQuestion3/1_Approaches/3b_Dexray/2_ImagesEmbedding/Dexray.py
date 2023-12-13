# IMPORT
from androguard.core.bytecodes.apk  import APK
from PIL                            import Image
import numpy                        as np
import tensorflow                   as tf
import os, requests, subprocess
import pytesseract, fnmatch
import re, spacy
import shutil

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

# Genetare Dex Bytes of a given apk
def generateDexBytes(apk: APK) -> bytes:
    for f in apk.get_files():
        if f.endswith(".dex"):
            yield apk.get_file(f)

# Gennerate a PNG image starting from an APK
def generatePNG(sha256, APK_PATH, OUTPUT_PATH):
    
    # Download the apk
    #print("\n🔑  Analyzing: {}".format(sha256))
    downloadAPK(APK_PATH, sha256)

    apk = APK(APK_PATH + sha256 + ".apk")

    stream = bytes()
    for s in generateDexBytes(apk):
        stream += s
    current_len = len(stream)
    image = Image.frombytes(mode='L', size=(1, current_len), data=stream)
    image.save(OUTPUT_PATH + "{}.png".format(sha256))
    
    # Delete the apk and the folder
    deleteAPK(APK_PATH, sha256)
    return

# Get a tensor representing an Image
def getImage(pathImg):
    image = np.asarray(Image.open(str(pathImg)))
    image = tf.convert_to_tensor(image, dtype_hint=None, name=None)
    return image

# Get Img Shape
def getShape(image):
    return image.shape[0]

# Decode Img 
def decodeImg(pathImg):
    IMG_SIZE = 128

    image = tf.numpy_function(getImage, [pathImg], tf.uint8)
    shape = tf.numpy_function(getShape, [image], tf.int64)
    image = tf.reshape(image, [shape, 1, 1])
    image = tf.image.convert_image_dtype(image, tf.float32)
    image = tf.image.resize(image, [IMG_SIZE*IMG_SIZE, 1])

    return tf.reshape(image, [IMG_SIZE*IMG_SIZE, 1])

# Decode img starting from sha256
def getImgFeatures(sha256, imagesPath):
    return decodeImg(imagesPath + sha256 + ".png")

# Encode the img using a pretrained model over the image tensor
def encodeImg(imgFeatures, model):
    X = np.reshape(imgFeatures, (1, 16384, 1))
    return model.predict(X, verbose=False)