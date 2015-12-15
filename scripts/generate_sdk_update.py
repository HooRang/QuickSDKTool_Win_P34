#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author xiaohei
# Date 2015-06-18

try: input = raw_input
except NameError: pass

import os,os.path
import shutil,errno
import sys
import time

from xml.etree import ElementTree as ET
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import ElementTree

def generate_updates():

    """
        扫描渠道SDK配置目录下的所有渠道SDK下的config.xml,根据里面配置的versionCode来生成
        需要更新的渠道SDK文件。

        每个渠道SDK生成一个更新文件，格式为zip
        最后生成一个version.txt，作为版本控制文件
        生成的目录为updates

        每次只生成有更新的渠道SDK，也就是将扫描的结果和updates目录下已经存在的version.txt
        进行比对，生成新增的渠道SDK，以及versionCode有增加的渠道SDK

    """

    print(u"generating sdk update files, please wait...")

    rootPath = "./config/sdk"

    if not os.path.exists(rootPath):
        print("The sdks folder is not exists."+os.path.abspath(rootPath))
        return

    outputPath = "./updates"

    if not os.path.exists(outputPath):
        os.makedirs(outputPath)

    backup_version_file(outputPath)

    sdkList = get_old_versions(outputPath)

    for sdk in os.listdir(rootPath):
        if os.path.isfile(sdk):
            continue

        sdkConfig = rootPath + "/" + sdk + "/config.xml"
        if not os.path.exists(sdkConfig):
            print("There is no config.xml file in " + sdk)
            continue

        versionCode = parse_sdk_version(sdk, sdkConfig)
        if versionCode == None:
            continue

        if not is_need_update(outputPath, sdk, versionCode, sdkList):
            continue

        print("generate update of sdk %s..." % sdk)

        sdkPath = os.path.join(rootPath, sdk)

        zipName = sdk + "_%s" % time.strftime('%Y%m%d%H%M%S')
        zipFilePath = os.path.join(outputPath, zipName)

        shutil.make_archive(zipFilePath, "zip", sdkPath)

        if not os.path.exists(zipFilePath+".zip"):
            print("The zip file of sdk %s generate faild. %s" % (sdk, os.path.abspath(zipFilePath+".zip")))
            continue

        sdkList.append([sdk, versionCode, zipName+".zip", os.path.getsize(zipFilePath+".zip")])

        print("generate update of sdk %s success." % sdk)

    generate_version_file(outputPath, sdkList)



def is_need_update(outputPath, sdk, newVersion, oldSDKList):

    """
        判断当前渠道SDK是否需要更新，根据versionCode判断
    """

    for s in oldSDKList:
        if sdk == s[0]:
            if newVersion > s[1]:
                oldFile = os.path.join(outputPath, s[2])
                if os.path.exists(oldFile):
                    os.remove(oldFile)
                oldSDKList.remove(s)

                print("remove old exists update file of sdk %s " % sdk)
                return True
            else:
                return False


    return True



def generate_version_file(outputPath, sdkList):

    """
        生成version.txt
    """

    if sdkList is None or len(sdkList) <= 0:
        print("generate version.txt faild. no sdk selected.")
        return

    versionFile = open(outputPath+"/version.txt", "w")
    for sdk in sdkList:
        versionFile.write("[%s,%s,%s,%s]\n" % (sdk[0], sdk[1], sdk[2], sdk[3]))

    versionFile.close()

    print("generate version.txt success.")


def backup_version_file(outputPath):

    """
        备份上一次的version.txt
    """

    oldVersionFile = os.path.join(outputPath, "version.txt")
    if not os.path.exists(oldVersionFile):
        return

    shutil.copy(oldVersionFile, os.path.join(outputPath, 'version_back.txt'))


def get_old_versions(outputPath):

    """
        解析上一次生成的version.txt
    """

    oldVersionFile = os.path.join(outputPath, "version.txt")
    if not os.path.exists(oldVersionFile):
        return []

    sdkList = []
    of = open(oldVersionFile, 'r')
    lines = of.readlines()
    of.close()

    if lines is None or len(lines) <= 0:
        return []

    for line in lines:
        line = line.strip()
        line = line[1:]
        line = line[:-1]
        sdkList.append(line.split(','))


    return sdkList


def parse_sdk_version(sdk, configXml):

    """
        从渠道SDK配置目录下的config.xml中解析出versionCode
    """

    try:
        tree = ET.parse(configXml)
        root = tree.getroot()
    except:
        print("Can not parse %s config.xml :path:%s" % sdk, configXml)
        return None

    versionNode = root.find('version')
    if versionNode is None:
        print("There is no version node in config.xml of sdk %s" % sdk)
        return None

    versionCodeNode = versionNode.find('versionCode')
    if versionCodeNode is None:
        print("The versionCode is not exists in [version] node of sdk %s" % sdk)
        return None

    return versionCodeNode.text



if __name__ == "__main__":

    generate_updates()

    input("Press Enter to continue:")

