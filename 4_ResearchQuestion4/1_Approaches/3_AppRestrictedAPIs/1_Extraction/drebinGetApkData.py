# IMPORT
import sys
sys.path.append("Modules")
sys.path.append("androguard")

from androguard.misc            import AnalyzeAPK
from drebinCommonModules        import logger
from xml.dom                    import minidom
import BasicBlockAttrBuilder    as BasicBlockAttrBuilder
import PScoutMapping            as PScoutMapping
import multiprocessing          as mp
import os, re, time
import psutil, logging
import requests ,argparse
import lxml 
import drebinCommonModules      as CM

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

def GetFromXML(ApkDirectoryPath, ApkFile):
    '''
    Get requested permission etc. for an ApkFile from Manifest files.
    :param String ApkDirectoryPath
    :param String ApkFile
    :return RequestedPermissionSet
    :rtype Set([String])
    :return ActivitySet
    :rtype Set([String])
    :return ServiceSet
    :rtype Set([String])
    :return ContentProviderSet
    :rtype Set([String])
    :return BroadcastReceiverSet
    :rtype Set([String])
    :return HardwareComponentsSet
    :rtype Set([String])
    :return IntentFilterSet
    :rtype Set([String])
    '''
    ApkDirectoryPath = os.path.abspath(ApkDirectoryPath)
    ApkFileName = os.path.splitext(ApkFile)[0]

    RequestedPermissionSet = set()
    ActivitySet = set()
    ServiceSet = set()
    ContentProviderSet = set()
    BroadcastReceiverSet = set()
    HardwareComponentsSet = set()
    IntentFilterSet = set()
    try:
        ApkFile = os.path.abspath(ApkFile)
        (a,  _,  _) = AnalyzeAPK(ApkFile)
        f = open(os.path.splitext(ApkFile)[0] + ".xml", "w")
        f.write(lxml.etree.tostring( a.xml['AndroidManifest.xml'], pretty_print=True).decode() )
        f.close()
    except Exception as e:
        print(e)
        logger.error(e)
        logger.error("Executing Androlyze on " + ApkFile + " to get AndroidManifest.xml Failed.")
        return
    try:
        f = open(ApkFileName + ".xml", "r")
        Dom = minidom.parse(f)
        DomCollection = Dom.documentElement

        DomPermission = DomCollection.getElementsByTagName("uses-permission")
        for Permission in DomPermission:
            if Permission.hasAttribute("android:name"):
                RequestedPermissionSet.add(Permission.getAttribute("android:name"))

        DomActivity = DomCollection.getElementsByTagName("activity")
        for Activity in DomActivity:
            if Activity.hasAttribute("android:name"):
                ActivitySet.add(Activity.getAttribute("android:name"))

        DomService = DomCollection.getElementsByTagName("service")
        for Service in DomService:
            if Service.hasAttribute("android:name"):
                ServiceSet.add(Service.getAttribute("android:name"))

        DomContentProvider = DomCollection.getElementsByTagName("provider")
        for Provider in DomContentProvider:
            if Provider.hasAttribute("android:name"):
                ContentProviderSet.add(Provider.getAttribute("android:name"))

        DomBroadcastReceiver = DomCollection.getElementsByTagName("receiver")
        for Receiver in DomBroadcastReceiver:
            if Receiver.hasAttribute("android:name"):
                BroadcastReceiverSet.add(Receiver.getAttribute("android:name"))

        DomHardwareComponent = DomCollection.getElementsByTagName("uses-feature")
        for HardwareComponent in DomHardwareComponent:
            if HardwareComponent.hasAttribute("android:name"):
                HardwareComponentsSet.add(HardwareComponent.getAttribute("android:name"))

        DomIntentFilter = DomCollection.getElementsByTagName("intent-filter")
        DomIntentFilterAction = DomCollection.getElementsByTagName("action")
        for Action in DomIntentFilterAction:
            if Action.hasAttribute("android:name"):
                IntentFilterSet.add(Action.getAttribute("android:name"))


    except Exception as e:
        logger.error(e)
        logger.error("Cannot resolve " + DestinationFolder + "'s AndroidManifest.xml File!");
        return RequestedPermissionSet, ActivitySet, ServiceSet, ContentProviderSet, BroadcastReceiverSet, HardwareComponentsSet, IntentFilterSet
    finally:
        f.close()
        return RequestedPermissionSet, ActivitySet, ServiceSet, ContentProviderSet, BroadcastReceiverSet, HardwareComponentsSet, IntentFilterSet

def GetFromInstructions(ApkDirectoryPath, ApkFile, PMap, RequestedPermissionList):
    '''
    Get required permissions, used Apis and HTTP information for an ApkFile.
    Reloaded version of GetPermissions.

    :param String ApkDirectoryPath
    :param String ApkFile
    :param PScoutMapping.PScoutMapping PMap
    :param RequestedPermissionList List([String])
    :return UsedPermissions
    :rtype Set([String])
    :return RestrictedApiSet
    :rtype Set([String])
    :return SuspiciousApiSet
    :rtype Set([String])
    :return URLDomainSet
    :rtype Set([String])
    '''

    UsedPermissions = set()
    RestrictedApiSet = set()
    SuspiciousApiSet = set()
    URLDomainSet = set()
    try:
        ApkFile = os.path.abspath(ApkFile)
        a, d, dx = AnalyzeAPK(ApkFile)
    except Exception as e:
        print(e)
        logger.error(e)
        logger.error("Executing Androlyze on " + ApkFile + " Failed.")
        return
    for _dex in d:
        for method in _dex.get_methods():
            g = dx.get_method(method)
            for BasicBlock in g.get_basic_blocks().get():
                Instructions = BasicBlockAttrBuilder.GetBasicBlockDalvikCode(BasicBlock)
                Apis, SuspiciousApis = BasicBlockAttrBuilder.GetInvokedAndroidApis(Instructions)
                Permissions, RestrictedApis = BasicBlockAttrBuilder.GetPermissionsAndApis(Apis, PMap,
                                                                                          RequestedPermissionList)
                UsedPermissions = UsedPermissions.union(Permissions)
                RestrictedApiSet = RestrictedApiSet.union(RestrictedApis)
                SuspiciousApiSet = SuspiciousApiSet.union(SuspiciousApis)
                for Instruction in Instructions:
                    URLSearch = re.search("https?://([\da-z\.-]+\.[a-z\.]{2, 6}|[\d.]+)[^'\"]*", Instruction, re.IGNORECASE)
                    if (URLSearch):
                        URL = URLSearch.group()
                        Domain = re.sub("https?://(.*)", "\g<1>",
                                        re.search("https?://([^/:\\\\]*)", URL, re.IGNORECASE).group(), 0, re.IGNORECASE)
                        URLDomainSet.add(Domain)
        # Got Set S6, S5, S7 described in Drebian paper
    return UsedPermissions, RestrictedApiSet, SuspiciousApiSet, URLDomainSet

def ProcessingDataForGetApkData(APK_PATH, sha256, PMap):

    try:
        StartTime = time.time()

        downloadAPK(APK_PATH,sha256)

        logger.info("Start to process " + sha256 + "...")
        print("Start to process " + sha256 + "...")

        DataDictionary = {}
        RequestedPermissionSet, ActivitySet, ServiceSet, ContentProviderSet, BroadcastReceiverSet, HardwareComponentsSet,\
        IntentFilterSet = GetFromXML(APK_PATH, APK_PATH + sha256 + ".apk")

        RequestedPermissionList = list(RequestedPermissionSet)
        ActivityList = list(ActivitySet)
        ServiceList = list(ServiceSet)
        ContentProviderList = list(ContentProviderSet)
        BroadcastReceiverList = list(BroadcastReceiverSet)
        HardwareComponentsList = list(HardwareComponentsSet)
        IntentFilterList = list(IntentFilterSet)
        DataDictionary["RequestedPermissionList"] = RequestedPermissionList
        DataDictionary["ActivityList"] = ActivityList
        DataDictionary["ServiceList"] = ServiceList
        DataDictionary["ContentProviderList"] = ContentProviderList
        DataDictionary["BroadcastReceiverList"] = BroadcastReceiverList
        DataDictionary["HardwareComponentsList"] = HardwareComponentsList
        DataDictionary["IntentFilterList"] = IntentFilterList
        # Got Set S2 and others
        UsedPermissions, RestrictedApiSet, SuspiciousApiSet, URLDomainSet = GetFromInstructions(APK_PATH, APK_PATH + sha256 + ".apk", PMap, RequestedPermissionList)

        UsedPermissionsList = list(UsedPermissions)
        RestrictedApiList = list(RestrictedApiSet)
        SuspiciousApiList = list(SuspiciousApiSet)
        URLDomainList = list(URLDomainSet)
        DataDictionary["UsedPermissionsList"] = UsedPermissionsList
        DataDictionary["RestrictedApiList"] = RestrictedApiList
        DataDictionary["SuspiciousApiList"] = SuspiciousApiList
        DataDictionary["URLDomainList"] = URLDomainList
        # Set S6, S5, S7, S8

        # Save the .data file
        CM.ExportToJson(os.path.splitext(APK_PATH + sha256 + ".apk")[0] + ".data", DataDictionary)

    except Exception as e:
        FinalTime = time.time()
        logger.error(e)
        logger.error(sha256 + " processing failed in " + str(FinalTime - StartTime) + "s...")
        print(sha256 + " processing failed in " + str(FinalTime - StartTime) + "s...")

        deleteAPK(APK_PATH,sha256)
        return sha256, False
    else:
        FinalTime = time.time()
        logger.info(sha256 + " processed successfully in " + str(FinalTime - StartTime) + "s")
        print(sha256 + " processed successfully in " + str(FinalTime - StartTime) + "s")

        deleteAPK(APK_PATH,sha256)
        return sha256, True

def GetApkData(ProcessNumber, APK_PATH, apkList):
    
    CWD = os.getcwd()
    os.chdir(os.path.join(CWD, "Modules"))
    PMap = PScoutMapping.PScoutMapping()
    os.chdir(CWD)

    pool = mp.Pool(int(ProcessNumber))
    ProcessingResults = []
    ScheduledTasks = []
    ProgressBar = CM.ProgressBar()

    for apkFile in apkList:
        if CM.FileExist(APK_PATH + apkFile + ".data"):
            pass
        else:
            ScheduledTasks.append(apkFile)
            ProcessingResults = pool.apply_async(ProcessingDataForGetApkData, args=(APK_PATH, apkFile, PMap),
                                                 callback=ProgressBar.CallbackForProgressBar)
    pool.close()
    if (ProcessingResults):
        ProgressBar.DisplayProgressBar(ProcessingResults, len(ScheduledTasks), type="hour")
    pool.join()

    return

def downloadAPK(APK_PATH, sha256):

    # Download APK from Androzoo
    apkUrl = "https://androzoo.uni.lu/api/download?apikey={}&sha256={}".format(ANDROZOO_API_KEY, sha256)
    req = requests.get(apkUrl, allow_redirects=True)
    open(APK_PATH+'{}.apk'.format(sha256), "wb").write(req.content)

def deleteAPK(APK_PATH, sha256):
    # Remove apk and xml file
    os.remove(APK_PATH + '{}.apk'.format(sha256))
    os.remove(APK_PATH + '{}.xml'.format(sha256))
