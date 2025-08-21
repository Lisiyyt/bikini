import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from datetime import datetime

API_TOKEN = "8404274800:AAFiG1ZDTH9jrFz1c15g4geA5ZXQR_mwruE"  # вставь свой токен

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ----- ХРАНИЛИЩЕ ДАННЫХ -----
users = {}
cassa = {}  # касса за месяц

# ----- КНОПКИ -----
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📌 Главное меню", callback_data="menu"),
         InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="📑 Направления", callback_data="directions"),
         InlineKeyboardButton(text="➕ Дополнительно", callback_data="extra")]
    ])

def extra_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📜 Правила", callback_data="rules")],
        [InlineKeyboardButton(text="🏆 Топ воркеров", callback_data="top")]
    ])

# ----- /start -----
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or f"user{user_id}"

    if user_id not in users:
        users[user_id] = {
            "username": username,
            "balance": 0,
            "profits_day": 0,
            "profits_month": 0,
            "profits_all": 0
        }
    await message.answer("Добро пожаловать в Bikini Bottom Team 🏝", reply_markup=main_menu())

# ----- ОБРАБОТКА КНОПОК -----
@dp.callback_query()
async def callbacks(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username or f"user{user_id}"

    if callback.data == "menu":
        await callback.message.answer(
            "Информация о BIKINI BOTTOM TEAM\n\n"
            "👤 Проценты воркера:\n├ 50%\n\n"
            "📑 Направления для работы:\n├ ICloud | work📗",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📢 Канал профитов", url="https://t.me/")],
                [InlineKeyboardButton(text="➕ Дополнительно", callback_data="extra")]
            ])
        )

    elif callback.data == "profile":
        user = users.get(user_id)
        if user:
            await callback.message.answer(
                f"🍃 Ваш личный профиль\n\n"
                f"👤 Username: @{user['username']}\n🆔 ID: {user_id}\n\n"
                f"💳 Ваш кошелёк\n├ Баланс: {user['balance']}$\n\n"
                f"💲 Ваши профиты\n"
                f"├ За день: {user['profits_day']} профитов\n"
                f"├ За месяц: {user['profits_month']} профитов\n"
                f"└ За все время: {user['profits_all']} профитов"
            )

    elif callback.data == "extra":
        await callback.message.answer("➕ Дополнительно:", reply_markup=extra_menu())

    elif callback.data == "rules":
        await callback.message.answer("📜 Правила: Работать честно, профиты писать по формату!")

    elif callback.data == "directions":
        await callback.message.answer("🥰 Выберите направление которое Вам нравится...\n\nICloud ☁️")

# ----- ОБРАБОТКА ПРОФИТОВ И КАССЫ -----
@dp.message()
async def handle_profit(message: types.Message):
    text = message.text.strip()

    # ПРОФИТ
    if "Есть профит" in text:
        try:
            username = text.split()[0].replace("@", "").replace(",", "").strip()
            amount = int(text.split(" ")[-1].replace("$", "").strip())

            # ищем или создаём пользователя
            user_id = None
            for uid, data in users.items():
                if data["username"] == username:
                    user_id = uid
                    break

            if not user_id:
                user_id = f"virtual_{username}"
                users[user_id] = {
                    "username": username,
                    "balance": 0,
                    "profits_day": 0,
                    "profits_month": 0,
                    "profits_all": 0
                }

            user = users[user_id]
            user["profits_day"] += 1
            user["profits_month"] += 1
            user["profits_all"] += 1
            user["balance"] += amount

            # касса
            if user_id not in cassa:
                cassa[user_id] = []
            cassa[user_id].append(f"{amount}$")

            await message.reply(f"✅ Профит учтён для @{username}: {amount}$")

        except Exception as e:
            print("Ошибка обработки профита:", e)

    # КАССА
    elif text == "/cassa":
        if not cassa:
            await message.answer("Касса пуста.")
        else:
            lines = []
            for uid, profits in cassa.items():
                user = users[uid]
                lines.append(f"@{user['username']} ➝ {', '.join(profits)}")
            await message.answer("📊 Касса:\n" + "\n".join(lines))

# ----- СБРОС КАССЫ ПО МЕСЯЦАМ -----
async def reset_monthly():
    while True:
        now = datetime.now()
        if now.day == 1 and now.hour == 0 and now.minute == 0:
            for uid in users:
                users[uid]["profits_month"] = 0
                users[uid]["profits_day"] = 0
            cassa.clear()
        await asyncio.sleep(60)

# ----- ЗАПУСК БОТА -----
async def main():
    asyncio.create_task(reset_monthly())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

