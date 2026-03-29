from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
import requests
import json
import subprocess
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait
from pyromod import listen
from pyrogram.types import Message
from p_bar import progress_bar
from subprocess import getstatusoutput
from aiohttp import ClientSession
import helper
import time
import asyncio
from config import api_id, api_hash, bot_token, auth_users, sudo_users
import sys
import re
import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Bot is running!"

bot = Client(
    "bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token)

@bot.on_message(filters.command(["stop"]))
async def cancel_command(bot: Client, m: Message):
    # ভেরিফিকেশন রিমুভ করা হয়েছে
    await m.reply_text("**STOPPED**🛑🛑", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command(["start"]))
async def account_login(bot: Client, m: Message):
    # ভেরিফিকেশন রিমুভ করা হয়েছে, সরাসরি কাজ শুরু হবে
    editable = await m.reply_text(f"**Hey [{m.from_user.first_name}](tg://user?id={m.from_user.id})\nSend txt file**")
    input: Message = await bot.listen(editable.chat.id)
    if input.document:
        x = await input.download()
        await input.delete(True)
        file_name, ext = os.path.splitext(os.path.basename(x))
        credit = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
        path = f"./downloads/{m.chat.id}"
        try:
            with open(x, "r") as f:
                content = f.read()
            content = content.split("\n")
            links = []
            for i in content:
                links.append(i.split("://", 1))
            os.remove(x)
        except:
            await m.reply_text("Invalid file input.🥲")
            os.remove(x)
            return
    else:
        content = input.text
        content = content.split("\n")
        links = []
        for i in content:
            links.append(i.split("://", 1))
   
    await editable.edit(f"Total links found are **{len(links)}**\n\nSend From where you want to download initial is **1**")
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)
    await editable.edit("**Enter Batch Name or send d for grabing from text filename.**")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text
    await input1.delete(True)
    if raw_text0 == 'd':
        b_name = file_name
    else:
        b_name = raw_text0
    await editable.edit("**Enter resolution**")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)
    try:
        if raw_text2 == "144": res = "256x144"
        elif raw_text2 == "240": res = "426x240"
        elif raw_text2 == "360": res = "640x360"
        elif raw_text2 == "480": res = "854x480"
        elif raw_text2 == "720": res = "1280x720"
        elif raw_text2 == "1080": res = "1920x1080" 
        else: res = "UN"
    except: res = "UN"
    await editable.edit("**Enter Your Name or send `de` for use default**")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)
    
    # credit লজিক ঠিক রাখা হয়েছে
    credit = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
    CR = credit if raw_text3 == 'de' else raw_text3
    
    await editable.edit("**Enter Your PW/Classplus Woking Token\n\nOtherwise Send No**")
    input4: Message = await bot.listen(editable.chat.id)
    working_token = input4.text
    await input4.delete(True)
    await editable.edit("Now send the **Thumb url**\nEg")
    input6: Message = await bot.listen(editable.chat.id)
    thumb = input6.text
    await input6.delete(True)
    await editable.delete()
    if thumb.startswith("http"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else: thumb = "No"
    count = int(raw_text) if len(links) > 1 else 1
    try:
        for i in range(count - 1, len(links)):
            V = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
            url = "https://" + V
            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)
            elif 'classplusapp' in url or "testbook.com" in url:
                url, contentId = url.split('&')
                headers = {'host': 'api.classplusapp.com', 'x-access-token': f'{working_token}', 'user-agent': 'Mobile-Android'}
                params = {'contentId': contentId, 'offlineDownload': "false"}
                url = requests.get("https://api.classplusapp.com/cams/uploader/video/jw-signed-url", params=params, headers=headers).json().get("url")
            elif "d1d34p8vz63oiq" in url or "sec1.pw.live" in url:
                url = f"https://anonymouspwplayer-907e62cf4891.herokuapp.com/pw?url={url}?token={working_token}"
            name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").strip()
            name = f'{str(count).zfill(3)}) {name1[:60]}'
            try:
                cc = f'** {str(count).zfill(3)}.** {name1}\n**Batch Name :** {b_name}\n\n**Downloaded by : {CR}**'
                if "drive" in url:
                    ka = await helper.download(url, name)
                    await bot.send_document(chat_id=m.chat.id,document=ka, caption=cc)
                    count+=1
                    os.remove(ka)
                elif ".pdf" in url:
                    os.system(f'yt-dlp -o "{name}.pdf" "{url}"')
                    await bot.send_document(chat_id=m.chat.id,document=f'{name}.pdf', caption=cc)
                    count += 1
                    os.remove(f'{name}.pdf')
                else:
                    prog = await m.reply_text(f"**Downloading:-**\n`{name}`")
                    res_file = await helper.download_video(url, name, raw_text2)
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, res_file, thumb, name)
                    count += 1
            except Exception as e:
                await m.reply_text(f"**Failed:** `{name}`\n{e}")
                count += 1
    except Exception as e:
        await m.reply_text(str(e))
    await m.reply_text("🔰Done Boss🔰")

bot.run()
