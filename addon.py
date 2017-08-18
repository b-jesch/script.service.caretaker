import xbmc
import xbmcaddon
import os
import urllib2

from xml.dom import minidom
from resources.lib.tools import *

__addonid__ = xbmcaddon.Addon().getAddonInfo('id')
__addonversion__ = xbmcaddon.Addon().getAddonInfo('version')
__addonpath__ = xbmcaddon.Addon().getAddonInfo('path')
__LS__ = xbmcaddon.Addon().getLocalizedString

BLACKLIST = os.path.join(xbmc.translatePath(__addonpath__), 'resources', 'data', 'blacklist')
bl_installed = []

def get_addon_list(repo_path, repo_id):
    addon_list = []
    if repo_path == '': return
    remote_url = None

    try:
        xml = minidom.parse(os.path.join(repo_path, 'addon.xml'))
        extensions = xml.getElementsByTagName('extension')
        for extension in extensions:
            if extension.getAttribute('point') == 'xbmc.addon.repository':
                remote_url = extension.getElementsByTagName('info')[0].firstChild.wholeText
                break
        if remote_url == None: return
        writeLog('Getting content from %s' % (remote_url))

        # we got the remote_url, fill the addon_list

        xml = minidom.parseString(urllib2.urlopen(remote_url, timeout=5).read())
        remote_addons = xml.getElementsByTagName('addon')
        for addon in remote_addons:
            if addon.getAttribute('id') == repo_id: continue
            addon_list.append({'name': addon.getAttribute('name'), 'id': addon.getAttribute('id'), 'version': addon.getAttribute('version')})
        return addon_list

    except urllib2.URLError, e:
        writeLog('Could not read content of remote repository', xbmc.LOGFATAL)
        writeLog('%s' % (e.reason), xbmc.LOGFATAL)

    except Exception, e:
        print e.message

def run_script():
    with open(BLACKLIST, 'r') as filehandle:
        blacklisted = filehandle.read().splitlines()

    writeLog('%s blacklisted repositories loaded' % (len(blacklisted)))

    query = {"method": "Addons.GetAddons",
             "params": {"type": "xbmc.addon.repository",
                       "enabled": "all",
                       "properties": ["name", "path", "version"]}
             }

    response = jsonrpc(query)
    if 'addons' in response:
        for addon in response['addons']:
            ai = addon.get('addonid', '')
            writeLog('check if \'%s\' is blacklisted' % (ai))
            if ai in blacklisted: bl_installed.append(addon)

        if len(bl_installed) == 0:
            writeLog('No potentially harmful repositories found', xbmc.LOGNOTICE)
            notify(__LS__(30010), __LS__(30014))
        else:
            for bl_repo in bl_installed:
                writeLog('Potentially harmful repository \'%s\' (%s) found' %
                         (bl_repo.get('name', ''), bl_repo.get('addonid', '')), xbmc.LOGNOTICE)

                bl_addons = get_addon_list(bl_repo.get('path', ''), bl_repo.get('addonid', ''))
                # print bl_addons

            dialogOk(__LS__(30010), __LS__(30013))
    else:
        writeLog('Could not execute JSON query', xbmc.LOGFATAL)

if __name__ == '__main__':
    run_script()
