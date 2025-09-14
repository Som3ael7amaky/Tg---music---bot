# bot.py
import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, SESSION_STRING, is_dev, OWNER_ID
import strings
import roles
import games
import music_core
from roles import init_db, get_role, set_role, remove_role, list_roles

# init DB
init_db()

app = Client(
    "music_user",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING or None,
    workdir="."
)

# in-memory sessions for trivia
trivia_sessions = {}  # chat_id -> {"q":..., "a":..., "asker": user_id}

# helper: map roles priority
ROLE_ORDER = ["slave","member","vip","mod","admin","developer","owner"]
def role_rank(role_name):
    try:
        return ROLE_ORDER.index(role_name)
    except ValueError:
        return 0

def get_effective_role(user_id: int):
    # owner and devs override DB
    if user_id == OWNER_ID:
        return "owner"
    if user_id in __import__("config").DEVELOPER_IDS:
        return "developer"
    r = get_role(user_id)
    return r if r else "member"

def require_min_role(min_role):
    def decorator(func):
        async def wrapper(client, message: Message, *args, **kwargs):
            uid = message.from_user.id
            eff = get_effective_role(uid)
            if role_rank(eff) < role_rank(min_role):
                return await message.reply_text(strings.NO_PERMISSION[0].format(user=message.from_user.mention))
            return await func(client, message, *args, **kwargs)
        return wrapper
    return decorator

# ---------------------------
# Basic commands
# ---------------------------
@app.on_message(filters.private & filters.command(["start","help"]))
async def start(_, message):
    text = strings.WELCOME[0].format(user=message.from_user.mention)
    await message.reply_text(text)

@app.on_message(filters.private & filters.command("myrank"))
async def myrank(_, message):
    role = get_effective_role(message.from_user.id)
    await message.reply_text(strings.role_sarcastic(role, message.from_user.mention))

# ---------------------------
# Developer commands (رفع وتنزيل رتب)
# ---------------------------
@app.on_message(filters.command(["rank_add","promote"]) & filters.private)
async def rank_add(_, message):
    # صيغة: /rank_add user_id|@username role
    uid = message.from_user.id
    if not is_dev(uid):
        return await message.reply_text(strings.NO_PERMISSION[0].format(user=message.from_user.mention))
    args = message.text.split()
    if len(args) < 3:
        return await message.reply_text("اكتب: /rank_add <@username|user_id> <role>\nمثال: /rank_add @user vip")
    target = args[1]
    role = args[2].lower()
    # حلّل target
    if target.startswith("@"):
        try:
            m = await app.get_users(target)
            target_id = m.id
        except Exception as e:
            return await message.reply_text("مش لاقي المستخدم.")
    else:
        try:
            target_id = int(target)
        except:
            return await message.reply_text("اكتب id أو @username صحيح.")
    set_role(target_id, role)
    mention = f"[{target_id}](tg://user?id={target_id})"
    await message.reply_text(f"✅ رفعت {mention} لي رتبة **{role}**\n" + strings.role_sarcastic(role, mention))

@app.on_message(filters.command(["rank_remove","demote"]) & filters.private)
async def rank_remove_cmd(_, message):
    uid = message.from_user.id
    if not is_dev(uid):
        return await message.reply_text(strings.NO_PERMISSION[0].format(user=message.from_user.mention))
    args = message.text.split()
    if len(args) < 2:
        return await message.reply_text("اكتب: /rank_remove <@username|user_id>")
    target = args[1]
    if target.startswith("@"):
        try:
            m = await app.get_users(target)
            target_id = m.id
        except Exception:
            return await message.reply_text("مش لاقي المستخدم.")
    else:
        try:
            target_id = int(target)
        except:
            return await message.reply_text("اكتب id أو @username صحيح.")
    remove_role(target_id)
    mention = f"[{target_id}](tg://user?id={target_id})"
    await message.reply_text(f"✅ نزلت رتبة {mention} — رجع عضو عادي.")

@app.on_message(filters.private & filters.command("list_roles"))
async def list_roles_cmd(_, message):
    if not is_dev(message.from_user.id):
        return await message.reply_text(strings.NO_PERMISSION[0].format(user=message.from_user.mention))
    rows = list_roles()
    if not rows:
        return await message.reply_text("لا توجد رتب مسجلة.")
    text = "قائمة الرتب:\n"
    for uid, role in rows:
        text += f"- [{uid}](tg://user?id={uid}) → {role}\n"
    await message.reply_text(text)

# ---------------------------
# Group admin commands (kick/mute example)
# ---------------------------
@app.on_message(filters.group & filters.command("kick"))
async def kick_cmd(_, message):
    # يتحقق لو اللي طالب هو مشرف أو مطور
    try:
        member = await app.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in ("administrator","creator") and not is_dev(message.from_user.id):
            return await message.reply_text(strings.NO_PERMISSION[0].format(user=message.from_user.mention))
    except:
        return await message.reply_text("مش قادر أتحقق من صلاحياتك.")
    # يحتاج reply أو @user
    if message.reply_to_message:
        target = message.reply_to_message.from_user.id
    else:
        parts = message.text.split()
        if len(parts) < 2:
            return await message.reply_text("استخدم الأمر بالرد على رسالة أو /kick @username")
        target_username = parts[1]
        try:
            user = await app.get_users(target_username)
            target = user.id
        except:
            return await message.reply_text("مش لاقي المستخدم.")
    try:
        await app.kick_chat_member(message.chat.id, target)
        await message.reply_text("تم الطرد ✅")
    except Exception as e:
        await message.reply_text(f"فشل في الطرد: {e}")

# ---------------------------
# Music commands (مبسطة: add to queue / show queue / skip)
# ---------------------------
@app.on_message(filters.group & filters.command("play"))
async def play_cmd(_, message):
    # مثال: /play song name or link
    args = message.text.split(None,1)
    if len(args) < 2:
        return await message.reply_text("اكتب اسم الأغنية أو الرابط بعد /play")
    query = args[1]
    msg = await message.reply_text("🔎 بتنزل/بتجهز الأغنية...")
    try:
        info = await asyncio.get_event_loop().run_in_executor(None, music_core.download_audio, query)
    except Exception as e:
        return await msg.edit(f"❌ خطأ في التحميل: {e}")
    # أضف للطابور
    pos = music_core.add_to_queue(message.chat.id, {
        "title": info["title"],
        "filepath": info["filepath"],
        "requester": message.from_user.mention
    })
    await msg.edit(f"✅ أضيفت للطابور: **{info['title']}** — موقعها #{pos}\n(ملاحظة: التشغيل في الڤويس تشات يحتاج ربط pytgcalls لاحقاً)")

@app.on_message(filters.group & filters.command("queue"))
async def show_queue(_, message):
    q = music_core.get_queue(message.chat.id)
    if not q:
        return await message.reply_text("الطابور فارغ.")
    txt = "قائمة التشغيل:\n"
    for i,it in enumerate(q, start=1):
        txt += f"{i}. {it['title']} — {it['requester']}\n"
    await message.reply_text(txt)

@app.on_message(filters.group & filters.command("skip"))
async def skip_cmd(_, message):
    # تحقق صلاحيات
    try:
        member = await app.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in ("administrator","creator") and not is_dev(message.from_user.id):
            return await message.reply_text(strings.NO_PERMISSION[0].format(user=message.from_user.mention))
    except:
        return await message.reply_text("مش قادر أتحقق من صلاحياتك.")
    popped = music_core.pop_queue(message.chat.id)
    if not popped:
        return await message.reply_text("مافيش حاجة للتخطي.")
    await message.reply_text(f"⏭ تم تخطي: {popped['title']}\n(لو في عناصر تانية هتشتغل لو ربطت ال-pytgcalls)")

# ---------------------------
# Games & fun commands
# ---------------------------
@app.on_message(filters.private & filters.command("coin"))
async def coin(_, message):
    res = games.coin_flip()
    await message.reply_text(strings.GAMES_TEXT["coin"][0].format(result=res))

@app.on_message(filters.private & filters.command("dice"))
async def dice(_, message):
    num = games.dice_roll()
    await message.reply_text(strings.GAMES_TEXT["dice"][0].format(num=num))

@app.on_message(filters.private & filters.command("rps"))
async def rps(_, message):
    # /rps rock
    args = message.text.split()
    if len(args) < 2:
        return await message.reply_text("اكتب: /rps <rock|paper|scissors>")
    you = args[1].lower()
    if you not in ("rock","paper","scissors"):
        return await message.reply_text("اختار: rock أو paper أو scissors")
    bot_choice = games.rps_result  # we'll compute below
    import random
    bot_pick = random.choice(["rock","paper","scissors"])
    res = games.rps_result(you, bot_pick)
    if res == "tie":
        await message.reply_text(strings.GAMES_TEXT["rps_tie"][0].format(user=message.from_user.mention, opponent="البوت", choice=you))
    elif res == "win":
        await message.reply_text(strings.GAMES_TEXT["rps_win"][0].format(user=message.from_user.mention, opponent="البوت", your=you, their=bot_pick))
    else:
        await message.reply_text(strings.GAMES_TEXT["rps_lose"][0].format(user=message.from_user.mention, opponent="البوت", your=you, their=bot_pick))

@app.on_message(filters.group & filters.command("duel"))
async def duel(_, message):
    # /duel @user  => يؤدي لاختيار عشوائي بينك وبين الشخص
    parts = message.text.split()
    if len(parts) < 2 and not message.reply_to_message:
        return await message.reply_text("استخدم: /duel @user أو بالرد على رسالة الشخص.")
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
    else:
        try:
            user = await app.get_users(parts[1])
            target_id = user.id
        except:
            return await message.reply_text("مش لاقي المستخدم.")
    winner = games.duel_coin(message.from_user.id, target_id)
    if winner == message.from_user.id:
        winner_mention = message.from_user.mention
    else:
        # fetch mention
        u = await app.get_users(target_id)
        winner_mention = u.mention
    await message.reply_text(f"⚔️ المواجهة خلصت! الفائز: {winner_mention}")

# ---------------------------
# Trivia
# ---------------------------
@app.on_message(filters.group & filters.command("trivia"))
async def trivia_cmd(_, message):
    q = games.get_random_trivia()
    trivia_sessions[message.chat.id] = {"q": q["q"], "a": q["a"], "asker": message.from_user.id}
    await message.reply_text(f"❓ سؤال: {q['q']}\nجاوب بـ /answer <الإجابة>")

@app.on_message(filters.group & filters.command("answer"))
async def answer_cmd(_, message):
    args = message.text.split(None,1)
    if len(args) < 2:
        return await message.reply_text("اكتب إجابتك بعد /answer")
    chat_id = message.chat.id
    session = trivia_sessions.get(chat_id)
    if not session:
        return await message.reply_text("مافيش سؤال شغّال دلوقتي. استخدم /trivia")
    user_ans = args[1].strip().lower()
    correct = session["a"].strip().lower()
    if user_ans == correct:
        await message.reply_text(f"✅ صح! الإجابة: {session['a']}  — مبروك {message.from_user.mention}")
        trivia_sessions.pop(chat_id, None)
    else:
        await message.reply_text("❌ مش صح، جرّب تاني.")

# ---------------------------
# On start
# ---------------------------
if __name__ == "__main__":
    print("Starting bot...")
    app.run()