import xbmc
import xbmcaddon
import xbmcgui
import json
import os


__addonid__ = xbmcaddon.Addon().getAddonInfo('id')
__addonversion__ = xbmcaddon.Addon().getAddonInfo('version')
__addonpath__ = xbmcaddon.Addon().getAddonInfo('path')
__LS__ = xbmcaddon.Addon().getLocalizedString

BLACKLIST = os.path.join(xbmc.translatePath(__addonpath__), 'resources', 'data', 'blacklist')
hits = []

def jsonrpc(query):
    querystring = {"jsonrpc": "2.0", "id": 1}
    querystring.update(query)
    return json.loads(xbmc.executeJSONRPC(json.dumps(querystring, encoding='utf-8')))

def service():
    with open(BLACKLIST, 'r') as filehandle:
        blacklisted = filehandle.read().splitlines()
    xbmc.log('[%s %s] %s blacklisted repositories loaded' % (__addonid__, __addonversion__, len(blacklisted)), xbmc.LOGDEBUG)

    query = {"method": "Addons.GetAddons",
             "params": {"type": "xbmc.addon.repository",
                       "enabled": "all",
                       "properties": ["name"]}
             }

    response = jsonrpc(query)
    if 'result' in response:
        for addon in response['result']['addons']:
            ai = addon.get('addonid', '')
            xbmc.log('[%s %s] check if %s is in blacklist' % (__addonid__, __addonversion__, ai), xbmc.LOGDEBUG)
            if ai in blacklisted: hits.append(addon)

        if len(hits) == 0:
            xbmc.log('[%s %s] No potentially harmful repositories found' % (__addonid__, __addonversion__), xbmc.LOGNOTICE)
        else:
            for hit in hits:
                xbmc.log('[%s %s] Potentially harmful repository \'%s\' (%s) found' % (__addonid__, __addonversion__, hit.get('name', ''), hit.get('addonid', '')), xbmc.LOGNOTICE)
            xbmcgui.Dialog().notification(__LS__(30011), __LS__(30012), xbmcgui.NOTIFICATION_WARNING)
    else:
        xbmc.log('[%s %s] Could not execute JSON query' % (__addonid__, __addonversion__), xbmc.LOGFATAL)

if __name__ == '__main__':
    service()