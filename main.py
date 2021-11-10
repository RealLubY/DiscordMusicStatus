# This is a little script that changes your discord custom status to the song name you are currently listening.
# This is only tested with youtube music, scince thats the platform i prefer, and the tab must be the active one.
# You can just open the tab in a new window for example.

import configparser
import time

import requests
import win32gui

from fake_useragent import UserAgent


ua = UserAgent()
cfg = configparser.ConfigParser()

song = None
old = None
status = False


def deEmojify(inputString): # remove any emojis in the song title
    return inputString.encode('ascii', 'ignore').decode('ascii')


def winEnumHandler(hwnd, ctx): # get current song, for this to work the music tab must be the active one
    global song
    cfg.read("cfg.ini")

    browser = cfg.get("MAIN", "browser")
    service = cfg.get("MAIN", "service")

    if win32gui.IsWindowVisible(hwnd):
        x = win32gui.GetWindowText(hwnd)
        if browser and service in str(x):
            song = deEmojify(str(x).replace(f" - {service} - {browser}", ""))


def update_status(title : None): # sending a request to chnage your custom discord status
    cfg.read("cfg.ini")

    headers = {
        'authority': 'discord.com',
        'authorization': cfg.get("MAIN", "token"),
        'user-agent': str(ua.chrome), # user agent
        'content-type': 'application/json',
        'origin': 'https://discord.com',
        'referer': 'https://discord.com/channels/@me',
    }
    if title == None and cfg.get("MAIN", "default_status") == "":
        data = '{"custom_status":null}'
    elif title == None:
        data = '{"custom_status":{"text":"%s"}}' % cfg.get("MAIN", "default_status")
    else:
        data = '{"custom_status":{"text":"%s %s"}}' % (cfg.get("MAIN", "text"), title)
    #data = '{"custom_status":{"text":"","emoji_id":"","emoji_name":""}}' #if you want to have an emoji (custom emoji)
    return requests.patch('https://discord.com/api/v9/users/@me/settings', headers=headers, data=data)


def main(): # some logic to combine the functions, tbh its messy
    global song, old, status
    while True:
        cfg.read("cfg.ini")

        song = None
        win32gui.EnumWindows(winEnumHandler, None) # get current song
        browser = cfg.get("MAIN", "browser")
        service = cfg.get("MAIN", "service")
        if not song or song == f"{service} - {browser}":
            old = None
            if status:
                update_status(None)
                status = False
            continue

        if old == song:
            continue
        old = song

        if update_status(song):
            status = True
        time.sleep(5)


main()
