from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
import requests, json, subprocess, helper, time, asyncio, sys, re, os
from pyrogram import Client, filters
from pyrogram.types import Message
from subprocess import getstatusoutput
from aiohttp import ClientSession
from flask import Flask
from config import api_id, api_hash, bot_token

app = Flask(__name__)
@app.route('/')
def hello(): return "Bot is running!"

bot = Client("bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@bot.on_message(filters.command(["stop"]))
async def cancel_command(bot, m):
    await m.reply_text("**STOPPED**🛑🛑")
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command(["start"]))
async def account_login(bot, m):
    editable = await m.reply_text(f"**Hey {m.from_user.first_name}**\nSend txt file or links")
    input_msg = await bot.listen(editable.chat.id)
    file_name = "Default_Batch"
    
    if input_msg.document:
        x = await input_msg.download()
        file_name = os.path.splitext(os.path.basename(x))[0]
        with open(x, "r") as f: content = f.read()
        os.remove(x)
    else: content = input_msg.text

    # লিঙ্কের ফরম্যাট ঠিক করার লজিক (নাম এবং লিঙ্ক আলাদা করা)
    links = []
    for line in content.split("\n"):
        if "http" in line:
            if ":" in line and "://" in line:
                # যদি 'Name:https' ফরম্যাটে থাকে
                parts = line.split(":", 1)
                name_part = parts[0].strip()
                url_part = parts[1].strip()
                if "://" not in url_part: url_part = "https:" + url_part
                links.append([name_part, url_part])
            else:
                # যদি সরাসরি লিঙ্ক থাকে (যেমন: Namehttps://...)
                match = re.search(r"(https?://\S+)", line)
                if match:
                    url_found = match.group(1)
                    name_found = line.replace(url_found, "").strip()
                    links.append([name_found or "Video", url_found])

    if not links:
        await editable.edit("No valid links found! ❌")
        return

    await editable.edit(f"Total: **{len(links)}**\nSend start index (Default 1):")
    idx_in = await bot.listen(editable.chat.id)
    count = int(idx_in.text) if idx_in.text.isdigit() else 1
    
    await editable.edit("Batch Name (or 'd'):")
    b_in = await bot.listen(editable.chat.id)
    b_name = file_name if b_in.text == 'd' else b_in.text
    
    await editable.edit("Resolution (144, 360, 720):")
    res_in = await bot.listen(editable.chat.id)
    res_val = res_in.text
    
    await editable.edit("Credit (or 'de'):")
    c_in = await bot.listen(editable.chat.id)
    CR = f"[{m.from_user.first_name}]" if c_in.text == 'de' else c_in.text
    
    await editable.edit("Token (or 'No'):")
    t_in = await bot.listen(editable.chat.id)
    token = t_in.text
    
    await editable.edit("Thumb URL (or 'No'):")
    th_in = await bot.listen(editable.chat.id)
    thumb = th_in.text
    if thumb.startswith("http"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    await editable.delete()

    for i in range(count - 1, len(links)):
        try:
            name1 = links[i][0].replace("Extractor Bot", "").replace("Made By", "").strip()
            if not name1: name1 = "Video File"
            url = links[i][1]
            
            # লিঙ্ক ক্লিন করা
            url = url.replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").strip()
            
            name = f'{str(count).zfill(3)}) {name1[:60]}'
            cc = f'**{str(count).zfill(3)}.** {name1}\n**Batch:** {b_name}\n**By:** {CR}'

            if "visionias" in url:
                async with ClientSession() as s:
                    async with s.get(url) as r:
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", await r.text()).group(1)
            elif 'classplusapp' in url or "testbook" in url:
                if '&' in url: url, cid = url.split('&')
                h = {'x-access-token': token, 'user-agent': 'Mobile-Android'}
                url = requests.get("https://api.classplusapp.com/cams/uploader/video/jw-signed-url", params={'contentId': cid}, headers=h).json().get("url")

            if "drive" in url:
                ka = await helper.download(url, name)
                await bot.send_document(m.chat.id, ka, caption=cc); os.remove(ka)
            elif ".pdf" in url:
                os.system(f'yt-dlp -o "{name}.pdf" "{url}"')
                await bot.send_document(m.chat.id, f"{name}.pdf", caption=cc); os.remove(f"{name}.pdf")
            else:
                prog = await m.reply_text(f"**Downloading:** `{name}`")
                res_file = await helper.download_video(url, name, res_val)
                filename = res_file[0] if isinstance(res_file, tuple) else res_file
                if filename and os.path.exists(filename):
                    await prog.delete()
                    await helper.send_vid(bot, m, cc, filename, thumb, name)
                    os.remove(filename)
                else: await prog.edit(f"**Failed:** `{name}`")
            count += 1
        except Exception as e:
            await m.reply_text(f"**Error at {count}:** {e}"); count += 1
            
    await m.reply_text("🔰Done Boss🔰")

bot.run()
