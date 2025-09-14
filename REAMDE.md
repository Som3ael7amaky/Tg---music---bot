# TG Music Bot - With Ranks & Games

بوت تيليجرام للموسيقى + أوامر تسلية وألعاب + نظام رتب.
احتياجات:
- Python 3.10+
- ffmpeg مثبت
- pyrogram, pytgcalls, yt-dlp, tgcrypto

ملفات:
- bot.py (الملف الرئيسي)
- config.py (المتغيرات والصلاحيات)
- roles.py (إدارة الرتب - sqlite)
- games.py (ألعاب وتسالي)
- music_core.py (نظام Queue وdownload)
- strings.py (ردود فخمة وساخرة)
- requirements.txt
- .gitignore

شغّل:
1. ضِع API_ID / API_HASH / SESSION_STRING و OWNER_ID في المتغيرات البيئية أو .env
2. ثبت الباكيجات: `pip install -r requirements.txt`
3. شغّل: `python bot.py`