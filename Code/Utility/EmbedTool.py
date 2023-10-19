

import re
import discord
import requests

from Utility.DebugTool import Log


def GetGifUrl(viewUrl):
    page_content = requests.get(viewUrl).text
    regex = r"(?i)\b((https?://media[.]tenor[.]com/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))[.]gif)"
    all = re.findall(regex, page_content)
    if len(all) == 0:
        return None
    return all[0][0]


def GetPreviewUrl(message: discord.Message):
    for getSticker in message.stickers:
        return getSticker.url
    for getEmbed in message.embeds:
        if getEmbed.url != None:
            if len(getEmbed.url) > 4:
                match getEmbed.url[-4:]:
                    case ".gif" | ".png":
                        return getEmbed.url

            if re.match("https://tenor.com/view/", getEmbed.url):
                return GetGifUrl(getEmbed.url)
        else:
            print("embed.url == None")

    for attachement in message.attachments:
        if attachement.url != None:
            return attachement.url

    Log.W(message.embeds)
    Log.W(message.attachments)
    Log.W(message.stickers)
    Log.W(message.components)
    return None
