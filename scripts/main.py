# -*- coding: utf-8 -*-
#Author:xiaohei
#CreateTime:2014-10-25
#
# The main operation entry for channel select and one thread.
#

import sys
import core
import file_utils
import apk_utils
import config_utils
import os
import os.path
import time
import log_utils

try: input = raw_input
except NameError: pass

def main(game, isPublic, isFullRes = False):

    print(u"**********当前配置的渠道号**********")
    print(u"\t渠道名 \t\t 渠道号 \t\t 渠道 \n")

    appName = game['appName']

    channels = config_utils.getAllChannels(appName, isPublic)

    if channels is None or len(channels) == 0:
        print("没有任何可以打包的渠道")
        return

    for ch in channels:
        name = ch['name']
        if len(name) <= 6:
            chStr = u"\t%s \t\t\t %s \t\t %s " % (ch['name'], ch['id'], ch['desc'])
        elif len(name) > 6 and len(name) <= 13:
            chStr = u"\t%s \t\t %s \t\t %s " % (ch['name'], ch['id'], ch['desc'])
        else:
            chStr = u"\t%s \t %s \t\t %s " % (ch['name'], ch['id'], ch['desc'])
        
        print(chStr)


    selected = []

    while(True):
        sys.stdout.write(u"请选择需要打包的渠道(渠道名),全部输入*,多个用逗号分割：")
        sys.stdout.flush()

        target = raw_input()

        if target == '*':
            selected = channels
        else:
            for t in target.split(','):
                t = t.strip()
                matchChannels = [c for c in channels if c['name'].lower() == t.lower()]
                if len(matchChannels) > 0:
                    selected.append(matchChannels[0])

        if len(selected) == 0:
            print(u"\n无效的渠道名，请重新输入！！\n")
        else:
            break

    clen = len(selected)
    log_utils.info("now hava %s channels to package...", clen)
    baseApkPath = file_utils.getFullPath('games/'+game['appName']+'/u8.apk')
    log_utils.info("the base apk file is : %s", baseApkPath)

    if not os.path.exists(baseApkPath):
        log_utils.error('the base apk file is not exists, must named with u8.apk')
        return

    sucNum = 0
    failNum = 0

    for channel in selected:
        ret = core.pack(game, channel, baseApkPath, isPublic)
        if ret:
            failNum = failNum + 1
        else:
            sucNum = sucNum + 1

    log_utils.info("<< success num:%s; failed num:%s >>", sucNum, failNum)
    if failNum > 0:
        log_utils.error("<< all done with error >>")
    else:
        log_utils.info("<< all nice done >>")
