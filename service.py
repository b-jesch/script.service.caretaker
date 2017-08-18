import xbmcgui
import os
from resources.lib.tools import *

__addonid__ = xbmcaddon.Addon().getAddonInfo('id')
__addonversion__ = xbmcaddon.Addon().getAddonInfo('version')
__addonpath__ = xbmcaddon.Addon().getAddonInfo('path')
__LS__ = xbmcaddon.Addon().getLocalizedString

BLACKLIST = os.path.join(xbmc.translatePath(__addonpath__), 'resources', 'data', 'blacklist')
bl_installed = []

def run_service():
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
            aid = addon.get('addonid', '')
            writeLog('check if \'%s\' is blacklisted' % (aid))
            if aid in blacklisted: bl_installed.append(addon)

        if len(bl_installed) == 0:
            writeLog('No potentially harmful repositories found', xbmc.LOGNOTICE)
        else:
            for bl_repo in bl_installed:
                writeLog('Potentially harmful repository \'%s\' (%s) found' %
                         (bl_repo.get('name', ''), bl_repo.get('addonid', '')), xbmc.LOGNOTICE)
            notify(__LS__(30011), __LS__(30012), icon=xbmcgui.NOTIFICATION_WARNING)

    else:
        writeLog('Could not execute JSON query', xbmc.LOGFATAL)

if __name__ == '__main__':
    run_service()
