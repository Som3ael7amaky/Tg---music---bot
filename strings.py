# strings.py
import random

ROLE_SARCASTIC = {
    "owner": [
        "يا مولاي {user} — تاج الرأس وملهب الملك 👑",
        "مولاي {user} دخل القاعة والهواء انقلب فخامه."
    ],
    "developer": [
        "المهندس {user} — الأكواد بتترعش قدامه.",
        "{user} — لو الكود وقّف، هو السبب والحل."
    ],
    "admin": [
        "الدايركتور {user} — المسؤلية على دماغه.",
        "{user} — لو فوضى، هو اللى هيحّط النظام."
    ],
    "mod": [
        "المشرف {user} — شغال كحارس للبوابه.",
        "{user} — عينه على اللي بيزاغط في الجروب."
    ],
    "vip": [
        "VIP {user} — عنده كباية شاي مختلفة.",
        "{user} — خلي له مقعد خاص في البوت."
    ],
    "member": [
        "عضو {user} — مرحب بيك.",
        "{user} — لعبتك تكون حلوة."
    ],
    "slave": [
        "عبد {user} — لا تعليق، عنده شغل فاصل.",
        "{user} — قرب قدّمي وأشرلي."
    ]
}

WELCOME = [
    "أهلاً {user}! البوت تحت أمرك — قلّي عايز إيه.",
    "يا هلا {user} — استمتع وامرح، وابقى اديني مراجعة."
]

NO_PERMISSION = [
    "معليش {user}، مش مسموح ليك تعمل ده.",
    "إيه دا؟ صلاحياتك مش كفاية — تعالى بعدين."
]

GAMES_TEXT = {
    "coin": ["نقود تتقلب... الفائز: {result}"],
    "dice": ["نرد رمى ورقم حاصل: {num}"],
    "rps_win": ["فزت! {user} تفوق على {opponent} ({your} vs {their})"],
    "rps_lose": ["خسرت! {user} اتغلب بواسطة {opponent} ({your} vs {their})"],
    "rps_tie": ["تعادل! {user} و{opponent} كلاهما {choice}"]
}

def role_sarcastic(role, user_mention):
    arr = ROLE_SARCASTIC.get(role, ROLE_SARCASTIC["member"])
    return random.choice(arr).format(user=user_mention)