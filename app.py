import requests
import json
import subprocess
import helper
import time
import asyncio
import sys
import re
import os
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from subprocess import getstatusoutput
from aiohttp import ClientSession
from flask import Flask

# Flask app for health checks
app = Flask(__name__)

@app.route('/')
def hello():
    return "Bot is running!"

from config import api_id, api_hash, bot_token

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
    elif input_msg.text:
        content = input_msg.text.splitlines()
    else:
        await m.reply_text("Invalid input! 🥲")
        return

    for line in content:
        if "://" in line:
            parts = line.split("://", 1)
            if len(parts) == 2:
                links.append((parts[0], parts[1]))

    if not links:
        await m.reply_text("No valid links found! 🥲")
        return

    await editable.edit(f"Total links found: **{len(links)}**\nSend start index (Default 1):")
    input0 = await bot.listen(editable.chat.id)
    count = int(input0.text) if input0.text and input0.text.isdigit() else 1

    await editable.edit("**Enter Batch Name or 'd' for filename:**")
    input1 = await bot.listen(editable.chat.id)
    b_name = file_name if input1.text == 'd' else input1.text

    await editable.edit("**Enter resolution (144, 240, 360, 480, 720, 1080):**")
    input2 = await bot.listen(editable.chat.id)
    raw_text2 = input2.text 

    await editable.edit("**Enter Your Name or 'de' for default:**")
    input3 = await bot.listen(editable.chat.id)
    CR = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})" if input3.text == 'de' else input3.text

    await editable.edit("**Enter Token (PW/Classplus) or 'No':**")
    input4 = await bot.listen(editable.chat.id)
    working_token = input4.text

    await editable.edit("**Send Thumb URL or 'No':**")
    input6 = await bot.listen(editable.chat.id)
    thumb_url = input6.text
    thumb = "No"
    if thumb_url.startswith("http"):
        getstatusoutput(f"wget '{thumb_url}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"

    await editable.delete()

    for i in range(count - 1, len(links)):
        try:
            name1 = re.sub(r'[\\/*?:"<>|]', '', links[i][0]).strip()
            url_part = links[i][1].strip()
            
            url_part = url_part.replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("/view?usp=sharing","")
            url = "https://" + url_part

            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url) as resp:
                        text = await resp.text()
                        match = re.search(r"(https://.*?playlist.m3u8.*?)\"", text)
                        if match: url = match.group(1)

            elif 'classplusapp' in url or "testbook.com" in url:
                if '&' in url:
                    main_url, contentId = url.split('&', 1)
                    headers = {'x-access-token': working_token, 'api-version': '18'}
                    params = {'contentId': contentId, 'offlineDownload': "false"}
                    res_json = requests.get("https://api.classplusapp.com/cams/uploader/video/jw-signed-url", params=params, headers=headers).json()
                    url = res_json.get("url", url)

            elif "d1d34p8vz63oiq" in url or "sec1.pw.live" in url:
                url = f"https://anonymouspwplayer-907e62cf4891.herokuapp.com/pw?url={url}?token={working_token}"

            name = f'{str(count).zfill(3)}) {name1[:60]}'
            cc = f'**{str(count).zfill(3)}.** {name1}\n**Batch:** {b_name}\n**By:** {CR}'

            if "drive" in url:
                ka = await helper.download(url, name)
                await bot.send_document(m.chat.id, document=ka, caption=cc)
                os.remove(ka)
            elif ".pdf" in url:
                os.system(f'yt-dlp -o "{name}.pdf" "{url}"')
                await bot.send_document(m.chat.id, document=f'{name}.pdf', caption=cc)
                os.remove(f'{name}.pdf')
            else:
                prog = await m.reply_text(f"**Downloading:-**\n`{name}`\n**Quality:** {raw_text2}")
                res_file = await helper.download_video(url, name, raw_text2)
                await prog.delete()
                await helper.send_vid(bot, m, cc, res_file, thumb, name)
            
            count += 1
            await asyncio.sleep(1)

        except Exception as e:
            await m.reply_text(f"**Failed:** `{name1}`\n**Error:** `{str(e)}`")
            count += 1
            continue

    await m.reply_text("🔰 **Done Boss!** 🔰")

if __name__ == "__main__":
    bot.run()
