#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author xiaohei
# Date 2015-06-18

import os,os.path
import shutil,errno
import sys
import time
import config_utils
import http_utils

from xml.etree import ElementTree as ET
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import ElementTree

try: input = raw_input
except NameError: pass

def check_sdk_update():

    """
        检查版本更新，在config/local目录下，存放一个打包工具使用的配置文件local.properties
        在该配置文件中，配置渠道SDK更新的服务器地址sdk_update_url.

        每次更新将远程的version.txt存放在local目录下
        用于下一次更新时，将远程的version.txt和本地的version.txt进行比对，从而筛选出需要
        更新的渠道SDK

        根据version.txt比对的结果，下载服务器上的需要更新的渠道SDK的zip文件
        临时放在local目录下

        然后解压到渠道SDK配置目录下，同时删除zip文件

    """

    print("checking update, please wait...")

    local_config = config_utils.getLocalConfig()

    if "sdk_update_url" not in local_config:
        print("the sdk_update_url is not exists in local.properties. check update failed.")
        return

    localUpdatePath = './local'
    if not os.path.exists(localUpdatePath):
        os.makedirs(localUpdatePath)

    sdkPath = './config/sdk'
    if not os.path.exists(sdkPath):
        os.makedirs(sdkPath)

    updateUrl = local_config['sdk_update_url']
    updateVersionUrl = updateUrl + "version.txt"

    old_updates = get_old_versions(localUpdatePath)
    new_updates = get_new_versions(localUpdatePath, updateVersionUrl)

    olds = []
    for sdk in new_updates:
        for old_sdk in old_updates:
            if sdk[0] == old_sdk[0] and sdk[1] == old_sdk[1]:
                olds.append(sdk)
                break

    new_updates = [sdk for sdk in new_updates if sdk not in olds]

    updateCount = len(new_updates)

    if updateCount <= 0:
        print("There is no sdk need update.")
    else:
        input("Total %s sdk to update, Press Enter to update:" % updateCount)

    for sdk in new_updates:
        print("Now to download %s ..." % sdk[0])
        url = updateUrl + sdk[2]
        zipFile = os.path.join(localUpdatePath, sdk[2])
        content = http_utils.get(url, None)

        f = open(zipFile, 'wb')
        f.write(content)
        f.close()

        print("%s update success, now to unzip..." % sdk[0])

        currsdkPath = os.path.join(sdkPath, sdk[0])
        if os.path.exists(currsdkPath):
            shutil.rmtree(currsdkPath)

        os.makedirs(currsdkPath)

        shutil.unpack_archive(zipFile, currsdkPath)

        os.remove(zipFile)



def get_new_versions(localUpdatePath, updateVersionUrl):

    """
        获取服务器上的version.txt文件，同时将该version.txt存放到local/目录下
    """

    content = http_utils.get(updateVersionUrl, None)
    if content is None:
        return []

    lines = content.decode('utf-8').split('\n')

    if lines is None or len(lines) <= 0:
        return []

    #save the new version.txt
    versionFile = os.path.join(localUpdatePath, "version.txt")
    f = open(versionFile, "w")
    f.writelines(lines)
    f.close()

    sdkList = []
    for line in lines:
        line = line.strip()

        if line is None or len(line) <= 0:
            continue

        line = line[1:]
        line = line[:-1]
        sdkList.append(line.split(','))

    return sdkList


def get_old_versions(localUpdatePath):

    """
        从本地local目录下解析version.txt 获取上次版本更新的记录信息
    """

    oldVersionFile = os.path.join(localUpdatePath, "version.txt")
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

        if line is None or len(line) <= 0:
            continue

        line = line[1:]
        line = line[:-1]
        sdkList.append(line.split(','))


    return sdkList


if __name__ == "__main__":

    check_sdk_update()

    input("Press Enter to continue:")

