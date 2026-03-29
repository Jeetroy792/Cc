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

# ... (আগের ইমপোর্টগুলো একই থাকবে)

@bot.on_message(filters.command(["start"]))
async def account_login(bot: Client, m: Message):
    editable = await m.reply_text(f"**Hey [{m.from_user.first_name}](tg://user?id={m.from_user.id})\nSend txt file or links**")
    
    input_msg: Message = await bot.listen(editable.chat.id)
    links = []
    file_name = "downloaded_file"

    if input_msg.document:
        x = await input_msg.download()
        file_name, ext = os.path.splitext(os.path.basename(x))
        with open(x, "r") as f:
            content = f.read().splitlines()
        os.remove(x)
    else:
        content = input_msg.text.splitlines()

    # লিঙ্ক প্রসেসিং - এখানে ভুল হওয়ার সম্ভাবনা বেশি ছিল
    for line in content:
        if "://" in line:
            # line.split("://", 1) একটি লিস্ট দেয়, আমরা সেটাকে আলাদা ভেরিয়েবলে নিচ্ছি
            parts = line.split("://", 1)
            if len(parts) == 2:
                links.append((parts[0], parts[1])) # Tuple আকারে সেভ করছি

    if not links:
        await m.reply_text("No valid links found! 🥲")
        return

    await editable.edit(f"Total links found: **{len(links)}**\nSend start index (Default is 1):")
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text if input0.text else "1"
    count = int(raw_text)

    await editable.edit("**Enter Batch Name or 'd' for filename:**")
    input1: Message = await bot.listen(editable.chat.id)
    b_name = file_name if input1.text == 'd' else input1.text

    await editable.edit("**Enter resolution (144, 240, 360, 480, 720, 1080):**")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    
    # রেজোলিউশন ম্যাপিং
    res_dict = {"144": "256x144", "240": "426x240", "360": "640x360", "480": "854x480", "720": "1280x720", "1080": "1920x1080"}
    res = res_dict.get(raw_text2, "UN")

    await editable.edit("**Enter Thumb URL or 'No':**")
    input6: Message = await bot.listen(editable.chat.id)
    thumb_url = input6.text
    thumb = "No"
    if thumb_url.startswith("http"):
        getstatusoutput(f"wget '{thumb_url}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"

    await editable.delete()

    for i in range(count - 1, len(links)):
        try:
            name_part = links[i][0].strip()
            url_part = links[i][1].strip()
            url = "https://" + url_part

            # PW/Classplus Logic
            if "d1d34p8vz63oiq" in url or "sec1.pw.live" in url:
                # working_token আগে ইনপুট নিয়ে রাখতে হবে (আমি এখানে logic বজায় রাখলাম)
                url = f"https://anonymouspwplayer-907e62cf4891.herokuapp.com/pw?url={url}?token={working_token}"

            # ফাইল নেম ক্লিনিং
            clean_name = re.sub(r'[\\/*?:"<>|]', '', name_part).replace("https", "").replace("http", "").strip()
            name = f'{str(count).zfill(3)}) {clean_name[:60]}'
            
            cc = f'**{str(count).zfill(3)}.** {clean_name}\n**Batch:** {b_name}\n**By:** {m.from_user.first_name}'

            if ".pdf" in url:
                os.system(f'yt-dlp -o "{name}.pdf" "{url}"')
                await bot.send_document(m.chat.id, document=f'{name}.pdf', caption=cc)
                os.remove(f'{name}.pdf')
            else:
                prog = await m.reply_text(f"**Downloading:-**\n`{name}`\nQuality: {raw_text2}")
                # helper function কল করার সময় parameters চেক করবে
                res_file = await helper.download_video(url, name, raw_text2) 
                await prog.delete()
                await helper.send_vid(bot, m, cc, res_file, thumb, name)
            
            count += 1
        except Exception as e:
            await m.reply_text(f"**Failed:** `{name}`\n**Error:** {str(e)}")
            count += 1
            continue

    await m.reply_text("🔰 **Done Boss!** 🔰")

# ... (বাকি অংশ)

    thumb = input6.text
    if thumb.startswith("http://") or thumb.startswith("https://"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = "No"

    if len(links) == 1:
        count = 1
    else:
        count = int(raw_text)

    try:
        for i in range(count - 1, len(links)):

            V = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
            url = "https://" + V

            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Pragma': 'no-cache', 'Referer': 'http://www.visionias.in/', 'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',}) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

            elif 'classplusapp' in url or "testbook.com" in url or "classplusapp.com/drm" in url or "media-cdn.classplusapp.com/drm" in url:
                url, contentId = url.split('&')
                
                headers = {
                    'host': 'api.classplusapp.com',
                    'x-access-token': f'{working_token}',    
                    'accept-language': 'EN',
                    'api-version': '18',
                    'app-version': '1.4.73.2',
                    'build-number': '35',
                    'connection': 'Keep-Alive',
                    'content-type': 'application/json',
                    'device-details': 'Xiaomi_Redmi 7_SDK-32',
                    'device-id': 'c28d3cb16bbdac01',
                    'region': 'IN',
                    'user-agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
                    'webengage-luid': '00000187-6fe4-5d41-a530-26186858be4c',
                    'accept-encoding': 'gzip'
                }
                
                params = {
                    'contentId': contentId,
                    'offlineDownload': "false"
                }

                url = requests.get("https://api.classplusapp.com/cams/uploader/video/jw-signed-url", params=params, headers=headers).json().get("url")

            elif "d1d34p8vz63oiq" in url or "sec1.pw.live" in url:
                url = f"https://anonymouspwplayer-907e62cf4891.herokuapp.com/pw?url={url}?token={working_token}"
                
            else:
                url = url
                
            name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            name = f'{str(count).zfill(3)}) {name1[:60]}'
            
            try:                               
                cc = f'** {str(count).zfill(3)}.** {name1}\n**Batch Name :** {b_name}\n\n**Downloaded by : {CR}**'
                cc1 = f'** {str(count).zfill(3)}.** {name1}\n**Batch Name :**{b_name}\n\n**Downloaded by : {CR}**'
                if "drive" in url:
                    try:
                        ka = await helper.download(url, name)
                        copy = await bot.send_document(chat_id=m.chat.id,document=ka, caption=cc1)
                        count+=1
                        os.remove(ka)
                        time.sleep(1)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue
                elif ".pdf" in url:
                    try:
                        cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_document(chat_id=m.chat.id,document=f'{name}.pdf', caption=cc1)
                        count += 1
                        os.remove(f'{name}.pdf')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue
                else:
                    prog = await m.reply_text(f"**Downloading:-**\n\n** Video Name :-** `{name}\nQuality - {raw_text2}`\n**link:**`{url}`**")
                    res_file = await helper.download_video(url, name, raw_text2)
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name)
                    count += 1

            except Exception as e:
                await m.reply_text(f"**This #Failed File is not Counted**\n**Name** =>> `{name}`\n**Link** =>> `{url}`\n\n ** fail reason »** {e}")
                count += 1
                continue

    except Exception as e:
        await m.reply_text(e)
    await m.reply_text("🔰Done Boss🔰")

bot.run()
