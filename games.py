# games.py
import random
from strings import GAMES_TEXT, role_sarcastic
from roles import get_role

# نتائج العملات
def coin_flip():
    return random.choice(["Heads", "Tails"])

def dice_roll(sides=6):
    return random.randint(1, sides)

# لعبة حجر ورقة مقص
def rps_result(player_choice, bot_choice):
    # choices: rock, paper, scissors
    wins = {
        "rock": "scissors",
        "scissors": "paper",
        "paper": "rock"
    }
    if player_choice == bot_choice:
        return "tie"
    elif wins[player_choice] == bot_choice:
        return "win"
    else:
        return "lose"

# duel بين اثنين عن طريق قطعة نقود (فائز عشوائي)
def duel_coin(user1_id, user2_id):
    return random.choice([user1_id, user2_id])

# trivia بسيطة (قائمة أسئلة — ممكن توسعها)
TRIVIA_QS = [
    {"q": "ما هي عاصمة فرنسا؟", "a": "باريس"},
    {"q": "كم عدد أيام الأسبوع؟", "a": "7"},
    {"q": "ما هو رمز الماء الكيميائي؟", "a": "H2O"},
]

def get_random_trivia():
    return random.choice(TRIVIA_QS)