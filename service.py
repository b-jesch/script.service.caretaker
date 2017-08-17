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
    with open(BLACKLIST) as filehandle:
        blacklisted = filehandle.read().splitlines()

    query = {"method": "Addons.GetAddons",
             "params": {"type": "xbmc.addon.repository",
                       "enabled": True,
                       "properties": ["name"]}
             }

    result = jsonrpc(query)
    if 'addons' in result:
        for addon in result['addons']:
            ai = addon.get('addonid', '')
            if ai in blacklisted: hits.append(addon)

    if len(hits) == 0:
        xbmc.log('[%s %s] No potentially harmful repositories found' % (__addonid__, __addonversion__), xbmc.LOGNOTICE)
    else:
        for hit in hits:
            xbmc.log('[%s %s] Potentially harmful repository found: %s (%s)' % (__addonid__, __addonversion__, hit.get('name', '', hit.get('addonid', ''))), xbmc.LOGDEBUG)
        xbmcgui.Dialog().notification(__LS__(30011), __LS__(30012), xbmcgui.NOTIFICATION_WARNING)

if __name__ == '__main__':
    service()