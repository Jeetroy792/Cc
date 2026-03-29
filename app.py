from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
import requests
import json
import subprocess
from pyrogram import Client, filters
from pyrogram.types.messages_and_media import message
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
from pyrogram.types import User, Message
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
    await m.reply_text("**STOPPED**🛑🛑", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command(["start"]))
async def account_login(bot: Client, m: Message):
    
    editable = await m.reply_text(f"**Hey [{m.from_user.first_name}](tg://user?id={m.from_user.id})\nSend txt file**")
    input: Message = await bot.listen(editable.chat.id)
    file_name = "Default_Batch"
    
    if input.document:
        x = await input.download()
        await input.delete(True)
        file_name, ext = os.path.splitext(os.path.basename(x))
        try:
            with open(x, "r") as f:
                content = f.read()
            os.remove(x)
        except:
            await m.reply_text("Invalid file input.🥲")
            return
    else:
        content = input.text
        
    content_lines = content.split("\n")
    links = []
    for i in content_lines:
        # শুধুমাত্র সঠিক লিঙ্ক ফরম্যাট (:// থাকা লাইন) গ্রহণ করবে
        if "://" in i and len(i.split("://", 1)) == 2:
            links.append(i.split("://", 1))
   
    if not links:
        await editable.edit("No valid links found in the input! ❌")
        return

    await editable.edit(f"Total links found are **{len(links)}**\n\nSend start index (Default is 1):")
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)

    await editable.edit("**Enter Batch Name or send d for grabbing from text filename.**")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text
    await input1.delete(True)
    b_name = file_name if raw_text0 == 'd' else raw_text0

    await editable.edit("**Enter resolution (144, 240, 360, 480, 720, 1080):**")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)
    
    await editable.edit("**Enter Your Name or send `de` for default:**")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)
    CR = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})" if raw_text3 == 'de' else raw_text3

    await editable.edit("**Enter Your Token/Password (otherwise send No):**")
    input4: Message = await bot.listen(editable.chat.id)
    working_token = input4.text
    await input4.delete(True)

    await editable.edit("Send the **Thumb URL** (otherwise send No):")
    input6: Message = await bot.listen(editable.chat.id)
    thumb_url = input6.text
    await input6.delete(True)
    await editable.delete()

    if thumb_url.startswith("http"):
        getstatusoutput(f"wget '{thumb_url}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = "No"

    count = int(raw_text) if raw_text.isdigit() else 1

    try:
        for i in range(count - 1, len(links)):
            # ভিডিওর নাম এবং লিঙ্ক আলাদা করা
            name1 = links[i][0].strip().replace(":", "").replace("/", "").replace("+", "")
            
            # অকেজো ক্রেডিট টেক্সট ফিল্টার করা
            if "Extractor Bot" in name1 or "Made By" in name1 or not name1:
                count += 1
                continue

            url_part = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","").strip()
            url = "https://" + url_part

            try:                               
                cc = f'** {str(count).zfill(3)}.** {name1}\n**Batch Name :** {b_name}\n\n**Downloaded by : {CR}**'
                name = f'{str(count).zfill(3)}) {name1[:60]}'

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

                if "drive" in url:
                    ka = await helper.download(url, name)
                    await bot.send_document(chat_id=m.chat.id, document=ka, caption=cc)
                    count += 1
                    os.remove(ka)
                elif ".pdf" in url:
                    os.system(f'yt-dlp -o "{name}.pdf" "{url}"')
                    await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc)
                    count += 1
                    os.remove(f'{name}.pdf')
                else:
                    prog = await m.reply_text(f"**Downloading:-**\n`{name}`")
                    res_file = await helper.download_video(url, name, raw_text2)
                    
                    if res_file is None:
                        await prog.edit(f"**Skipping (Invalid URL):** `{name}`")
                        count += 1
                        continue
                        
                    filename = res_file[0] if isinstance(res_file, tuple) else res_file
                    
                    if filename and os.path.exists(filename):
                        await prog.delete(True)
                        await helper.send_vid(bot, m, cc, filename, thumb, name)
                        count += 1
                        os.remove(filename)
                    else:
                        await prog.edit(f"**File Not Found:** `{name}`")
                        count += 1

            except Exception as e:
                await m.reply_text(f"**Failed:** `{name}`\n{e}")
                count += 1

    except Exception as e:
        await m.reply_text(str(e))
    await m.reply_text("🔰Done Boss🔰")

bot.run()
