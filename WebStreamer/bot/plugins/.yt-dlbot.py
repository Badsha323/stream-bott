# © @Avishkarpatil [ Telegram ]

from urllib.parse import urlparse
from datetime import datetime
import yt_dlp
from WebStreamer.utils.mimetype import isMediaFile
from typing import Text
from WebStreamer.bot import StreamBot
from WebStreamer.vars import Var
from WebStreamer.utils.human_readable import humanbytes
from WebStreamer.utils.database import Database
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
db = Database(Var.DATABASE_URL, Var.SESSION_NAME)

AGREE_BUTTONS = InlineKeyboardMarkup(
        [[InlineKeyboardButton("I Agree", callback_data='agree')]]
    )

print("yt-dlbot.py started")
@StreamBot.on_message(filters.command('ytdl') & filters.private & ~filters.edited)
def start(b, m):
    b.send_message(
        chat_id=m.chat.id,
        text="Hi\nyou can now Directly send urls supported by yt-dlp\nhttps://github.com/ytdl-org/youtube-dl/blob/master/docs/supportedsites.md\nEg: https://www.youtube.com/watch?v=BaW_jenozKc",
        parse_mode="markdown",
        disable_web_page_preview=True
    )
@StreamBot.on_message(filters.private & filters.text & ~filters.edited & ~filters.command(["start","about","help","status","ban","unban","ytdl","ban","unban","remove","rem"]))
async def start(b, m):
    if await db.is_user_banned(m.from_user.id):
        await b.send_message(
                chat_id=m.chat.id,
                text="__Sᴏʀʀʏ Sɪʀ, Yᴏᴜ ᴀʀᴇ Bᴀɴɴᴇᴅ ᴛᴏ ᴜsᴇ ᴍᴇ. Cᴏɴᴛᴀᴄᴛ ᴛʜᴇ Dᴇᴠᴇʟᴏᴘᴇʀ__\n\n @DeekshithSH **Tʜᴇʏ Wɪʟʟ Hᴇʟᴘ Yᴏᴜ**",
                parse_mode="markdown",
                disable_web_page_preview=True
            )
    elif not await db.is_user_agreed(m.from_user.id):
        await b.send_message(
                chat_id=m.chat.id,
                text=Var.AGREE_TEXT,
                parse_mode="markdown",
                disable_web_page_preview=True,
                reply_markup=AGREE_BUTTONS
            )
    else:
        usr_text=m.text
        print(usr_text)
        res=urlparse(usr_text)
        if not res.netloc:
            if res.path:
                res=urlparse("http://"+usr_text)
        if res.netloc in ["www.youtube.com", "m.youtube.com", "youtu.be", "youtube.com"]:
            snt_msg=await m.reply_text(
                text=usr_text,
                reply_to_message_id=m.message_id,
            )
            class MyLogger:
                def debug(self, msg):
                    # For compatibility with youtube-dl, both debug and info are passed into debug
                    # You can distinguish them by the prefix '[debug] '
                    if msg.startswith('[debug] '):
                        pass
                    else:
                        self.info(msg)

                def info(self, msg):
                    pass
                
                def warning(self, msg):
                    global ytdlwarn
                    ytdlwarn=msg
                    pass
                
                async def error(self, msg):
                    await b.edit_message_text(
                        message_id=snt_msg.message_id,
                        chat_id=m.chat.id,
                        text="{}\nsend me urls supported by yt-dlp\nhttps://github.com/ytdl-org/youtube-dl/blob/master/docs/supportedsites.md".format(msg.split(".")[0])
                        )

            # ℹ️ See "progress_hooks" in the docstring of yt_dlp.YoutubeDL
            def my_hook(d):
                res=d
                if res['status'] == 'downloading':
                    size=humanbytes(res['downloaded_bytes'])
                    filename = res['filename'].split("Files/")[-1]
                    b.edit_message_text(
                        message_id=snt_msg.message_id,
                        chat_id=m.chat.id,
                        text="File Name: {}\nDownloading: {}/{}  {} \nSpeed: {}\nETA: {}</u>".format(filename, size, res['_total_bytes_str'], res['_percent_str'], res['_speed_str'], res['_eta_str'])
                        )    
                elif res['status'] == 'finished':
                    b.edit_message_text(
                        message_id=snt_msg.message_id,
                        chat_id=m.chat.id,
                        text="Download Finished \nNow Uploading to Telegram"
                        )


            def format_selector(ctx):
                """ Select the best video and the best audio that won't result in an mkv.
                This is just an example and does not handle all cases """

                # formats are already sorted worst to best
                formats = ctx.get('formats')[::-1]

                # acodec='none' means there is no audio
                best_video = next(f for f in formats
                                  if f['vcodec'] != 'none' and f['acodec'] == 'none')

                # find compatible audio extension
                audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[best_video['ext']]
                # vcodec='none' means there is no video
                best_audio = next(f for f in formats if (
                    f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))

                yield {
                    # These are the minimum required fields for a merged format
                    'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
                    'ext': best_video['ext'],
                    'requested_formats': [best_video, best_audio],
                    # Must be + separated list of protocols
                    'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
                }


            # ℹ️ See docstring of yt_dlp.YoutubeDL for a description of the options

            ydl_opts = {
                'format': format_selector,
                'postprocessors': [{
                    # Embed metadata in video using ffmpeg.
                    # ℹ️ See yt_dlp.postprocessor.FFmpegMetadataPP for the arguments it accepts
                    'key': 'FFmpegMetadata',
                    'add_chapters': True,
                    'add_metadata': True,
                }],
                'logger': MyLogger(),
                'progress_hooks': [my_hook],
                'outtmpl': 'Files/%(title)s-%(id)s.%(ext)s',
                'restrictfilenames': True
            }


            # Add custom headers
            yt_dlp.utils.std_headers.update({'Referer': 'https://www.google.com'})

            # ℹ️ See the public functions in yt_dlp.YoutubeDL for for other available functions.
            # Eg: "ydl.download", "ydl.download_with_info_file"
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(usr_text)

                # ℹ️ ydl.sanitize_info makes the info json-serializable
                # print(json.dumps(ydl.sanitize_info(info)))
                filename = ydl.prepare_filename(info)
                filename2=filename.split(".")[0]
                mediatype=isMediaFile(filename)

                async def progress(current, total):
                    await b.edit_message_text(
                        message_id=snt_msg.message_id,
                        chat_id=m.chat.id,
                        text=f"{current * 100 / total:.1f}% uploaded"
                        )   

                try:
                    if mediatype == 'audio':
                        await b.send_audio(
                            chat_id=m.chat.id,
                            audio=filename,
                            # caption=filename,
                            reply_to_message_id=m.message_id,
                        )
                    elif mediatype == 'video':
                        await b.send_video(
                            chat_id=m.chat.id,
                            video=filename,
                            progress=progress,
                            # caption=filename,
                            supports_streaming=True,
                            reply_to_message_id=m.message_id,
                        )
                    elif mediatype == 'image':
                        await b.send_photo(
                            chat_id=m.chat.id,
                            photo=filename,
                            # caption=filename,
                            reply_to_message_id=m.message_id,
                        )
                except:
                    log_msg=await b.send_message(text=f"**ʟɪɴᴋ :** {usr_text}\n**RᴇQᴜᴇꜱᴛᴇᴅ ʙʏ :** [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n**Uꜱᴇʀ ɪᴅ :** `{m.from_user.id}`", chat_id=Var.BIN_CHANNEL24, disable_web_page_preview=True, parse_mode="Markdown")
                    if ytdlwarn == 'Requested formats are incompatible for merge and will be merged into mkv.':
                        await b.edit_message_text(
                            message_id=snt_msg.message_id,
                            chat_id=m.chat.id,
                            text="🔸 𝗪𝗔𝗥𝗡𝗜𝗡𝗚 🚸\n{}\n🔹Uploading File to Telegram".format(ytdlwarn)
                        )
                        await b.send_video(
                            chat_id=m.chat.id,
                            video="{}.mkv".format(filename2),
                            supports_streaming=False,
                            # caption=filename,
                            reply_to_message_id=m.message_id,
                        )
                    else:
                        await b.send_text(
                            chat_id=m.chat.id,
                            text=ytdlwarn
                        )
                        await log_msg.reply_text(text="{}\n#ytdlp-error".format(ytdlwarn))
        else:
            try:
                snt_msg=await m.reply_text(
                text=usr_text,
                reply_to_message_id=await m.message_id,
                )
                class MyLogger:
                    def debug(self, msg):
                        # For compatibility with youtube-dl, both debug and info are passed into debug
                        # You can distinguish them by the prefix '[debug] '
                        if msg.startswith('[debug] '):
                            pass
                        else:
                            self.info(msg)

                    async def info(self, msg):
                        num=datetime.now().strftime("%H:%M:%S:%f")
                        await b.edit_message_text(
                            message_id=snt_msg.message_id,
                            chat_id=m.chat.id,
                            text=f"{num}| {msg}"
                            )

                    async def warning(self, msg):
                        global ytdlwarn
                        ytdlwarn=msg
                        pass
                    
                    async def error(self, msg):
                        await b.edit_message_text(
                            message_id=snt_msg.message_id,
                            chat_id=m.chat.id,
                            text="{}\nsend me urls supported by yt-dlp\nhttps://github.com/ytdl-org/youtube-dl/blob/master/docs/supportedsites.md".format(msg.split(".")[0])
                            )

                # ℹ️ See "progress_hooks" in the docstring of yt_dlp.YoutubeDL
                async def my_hook(d):
                    if res['status'] == 'finished':
                        await b.edit_message_text(
                            message_id=snt_msg.message_id,
                            chat_id=m.chat.id,
                            text="Download Finished \nNow Uploading to Telegram"
                            )


                # ℹ️ See docstring of yt_dlp.YoutubeDL for a description of the options

                ydl_opts = {
                    'postprocessors': [{
                        # Embed metadata in video using ffmpeg.
                        # ℹ️ See yt_dlp.postprocessor.FFmpegMetadataPP for the arguments it accepts
                        'key': 'FFmpegMetadata',
                        'add_chapters': True,
                        'add_metadata': True,
                    }],
                    'logger': MyLogger(),
                    'outtmpl': 'Files/%(title)s-%(id)s.%(ext)s',
                    'restrictfilenames': True
                }


                # Add custom headers
                yt_dlp.utils.std_headers.update({'Referer': 'https://www.google.com'})

                # ℹ️ See the public functions in yt_dlp.YoutubeDL for for other available functions.
                # Eg: "ydl.download", "ydl.download_with_info_file"
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(usr_text)

                    # ℹ️ ydl.sanitize_info makes the info json-serializable
                    # print(json.dumps(ydl.sanitize_info(info)))
                    filename = ydl.prepare_filename(info)
                    filename2=filename.split(".")[0]
                    mediatype=isMediaFile(filename)

                    async def progress(current, total):
                        await b.edit_message_text(
                            message_id=snt_msg.message_id,
                            chat_id=m.chat.id,
                            text=f"{current * 100 / total:.1f}% uploaded"
                            )   

                    try:
                        if mediatype == 'audio':
                            await b.send_audio(
                                chat_id=m.chat.id,
                                audio=filename,
                                caption=filename.split("/")[-1],
                                reply_to_message_id=m.message_id,
                            )
                        elif mediatype == 'video':
                            await b.send_video(
                                chat_id=m.chat.id,
                                video=filename,
                                progress=progress,
                                caption=filename.split("/")[-1],
                                supports_streaming=True,
                                reply_to_message_id=m.message_id,
                            )
                        elif mediatype == 'image':
                            await b.send_photo(
                                chat_id=m.chat.id,
                                photo=filename,
                                caption=filename.split("/")[-1],
                                reply_to_message_id=m.message_id,
                            )
                    except:
                        log_msg=await b.send_message(text=f"**ʟɪɴᴋ :** {usr_text}\n**RᴇQᴜᴇꜱᴛᴇᴅ ʙʏ :** [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n**Uꜱᴇʀ ɪᴅ :** `{m.from_user.id}`", chat_id=Var.BIN_CHANNEL24, disable_web_page_preview=True, parse_mode="Markdown")
                        if ytdlwarn == 'Requested formats are incompatible for merge and will be merged into mkv.':
                            await b.edit_message_text(
                                message_id=snt_msg.message_id,
                                chat_id=m.chat.id,
                                text="🔸 𝗪𝗔𝗥𝗡𝗜𝗡𝗚 🚸\n{}\n🔹Uploading File to Telegram".format(ytdlwarn)
                            )
                            await b.send_video(
                                chat_id=m.chat.id,
                                video="{}.mkv".format(filename2),
                                supports_streaming=False,
                                caption="{}.mkv".format(filename2.split("/")[-1]),
                                reply_to_message_id=m.message_id,
                            )
                        else:
                            await b.send_text(
                                chat_id=m.chat.id,
                                text=ytdlwarn
                            )
                            await log_msg.reply_text(text="{}\n#ytdlp-error".format(ytdlwarn))
            except:
                await b.send_text(
                    chat_id=m.chat.id,
                    text="Error"
                )