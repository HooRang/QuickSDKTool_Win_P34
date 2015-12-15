import file_utils
import os
import os.path
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import ElementTree
import os
import os.path
import zipfile
import re
import subprocess
import platform
from xml.dom import minidom
import codecs
import sys

androidNS = 'http://schemas.android.com/apk/res/android'

def generateShareSDKXmlFile(pluginInfo, decompileDir):
	assetsPath = file_utils.getFullPath(decompileDir) + "/assets"

	if not os.path.exists(assetsPath):
		os.makedirs(assetsPath)

	shareSdkXml = assetsPath + "/ShareSDK.xml"

	if os.path.exists(shareSdkXml):
		os.remove(shareSdkXml)
		
	tree = ElementTree()
	root = Element('DevInfor')
	tree._setroot(root)

	shareNode = SubElement(root, 'ShareSDK')

	if 'params' in pluginInfo and pluginInfo['params'] != None and len(pluginInfo['params']) > 0:
		for param in pluginInfo['params']:
			paramName = param.get('name')
			if paramName == 'AppKey':
				paramValue = param.get('value')
				shareNode.set('AppKey', paramValue)
				break

	subplugins = pluginInfo.get('subplugins')

	if subplugins != None and len(subplugins) > 0:
		index = 1
		for subplg in subplugins:
			subplgNode = SubElement(root, subplg['name'])
			subparams = subplg.get('params')
			if subparams != None and len(subparams) > 0:
				for subparam in subparams:
					subplgNode.set(subparam['name'], subparam['value'])

			if subplgNode.get('Id') == None:
				subplgNode.set('Id', str(index))
			else:
				subplgNode.attrib['Id'] = str(index)

			if subplgNode.get('Enable') == None:
				subplgNode.set('Enable', 'true')
			else:
				subplgNode.attrib['Enable'] = 'true'

			index = index + 1

	tree.write(shareSdkXml, 'UTF-8')

def appendAppIdForQZone(pluginInfo, decompileDir):
	qzoneAppID = None
	subplugins = pluginInfo.get('subplugins')

	appId = 0
	if subplugins != None and len(subplugins) > 0:
		for subplg in subplugins:
			if subplg['name'] == "QZone":
				params = subplg.get('params')
				for param in params:
					if param['name'] == 'AppId':
						appId = int(param['value'])
						break

			if appId > 0:
				break

	if appId == 0:
		return

	manifestFile = decompileDir + "/AndroidManifest.xml"
	manifestFile = file_utils.getFullPath(manifestFile)
	ET.register_namespace('android', androidNS)

	tree = ET.parse(manifestFile)
	root = tree.getroot()

	applicationNode = root.find('application')
	if applicationNode is None:
		return
	key = '{'+androidNS+'}name'
	scheme = '{'+androidNS+'}scheme'

	activityNodes = applicationNode.findall('activity')
	if activityNodes != None and len(activityNodes) > 0:
		for activityNode in activityNodes:
			name = activityNode.get(key)
			if name == 'cn.sharesdk.framework.ShareSDKUIShell':
				intentNodes = activityNode.findall('intent-filter')
				if intentNodes != None and len(intentNodes) > 0:
					for intentNode in intentNodes:
						dataNode = SubElement(intentNode, 'data')
						dataNode.set(scheme, 'tencent'+str(appId))
						break

				else:
					intentNode = SubElement(activityNode, 'intent-filter')
					dataNode = SubElement(intentNode, 'data')
					dataNode.set(scheme, 'tencent'+str(appId))
					actionNode = SubElement(intentNode, 'action')
					actionNode.set(key, 'android.intent.action.VIEW')
					categoryNode = SubElement(intentNode, 'category')
					categoryNode.set(key, 'android.intent.category.DEFAULT')
					categoryNode2 = SubElement(intentNode, 'category')
					categoryNode2.set(key, 'android.intent.category.BROWSABLE')

	tree.write(manifestFile, 'UTF-8')


def execute(channel, pluginInfo, decompileDir, packageName):
	generateShareSDKXmlFile(pluginInfo, decompileDir)
	appendAppIdForQZone(pluginInfo, decompileDir)