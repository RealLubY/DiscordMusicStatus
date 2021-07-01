# This is a little script that changes your discord custom status to the song name you are currently listening.
# This only works with youtube music, scince thats the platform i prefer, and the tab must be the active one.
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

    if win32gui.IsWindowVisible(hwnd):
        x = win32gui.GetWindowText(hwnd)
        if browser and "YouTube Music" in str(x):
            song = deEmojify(str(x).replace(f" - YouTube Music - {browser}", ""))


def update_status(title : None): # sending a request to chnage your custim discord status
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
    #data = '{"custom_status":{"text":"life is just a game...","emoji_id":"776686859140857887","emoji_name":"fir_happy"}}' #if you want to have an emoji (custom emoji)
    return requests.patch('https://discord.com/api/v9/users/@me/settings', headers=headers, data=data)


def main(): # some logic to combine the functions, tbh its messy
    global song, old, status
    while True:
        time.sleep(5)
        song = None
        win32gui.EnumWindows(winEnumHandler, None) # get current song
        if not song or song == "YouTube Music - Google Chrome":
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


main()