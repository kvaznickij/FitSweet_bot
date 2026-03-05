import asyncio
import random
import datetime
import aiosqlite

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = "8647136285:AAFwaj5t1ARxHa4o_Eb7PTm038QW7YNv_YQ"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

DB_NAME = "users.db"

tasks = [
    "💪 Зроби 15 віджимань",
    "🏋️ Зроби 20 присідань",
    "⏱ Планка 30 секунд",
    "🔥 20 скручувань на прес",
    "🦘 15 стрибків",
    "🚶 Пройди 2000 кроків сьогодні",
    "🧘 Розтяжка 5 хвилин"
]

replies = [
    "🔥 Молодець! Так тримати!",
    "💪 Ти стаєш сильнішим щодня!",
    "🏆 Оце дисципліна!",
    "🚀 Крок за кроком до результату!",
    "👏 Пишаюсь тобою!",
    "✨ Супер! Не зупиняйся!"
]

done_button = ReplyKeyboardMarkup(resize_keyboard=True)
done_button.add(KeyboardButton("✅ Я виконав"))

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                streak INTEGER DEFAULT 0,
                last_done TEXT
            )
        """)
        await db.commit()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.chat.id,))
        await db.commit()

    await message.answer(
        "👋 Вітаю!\n"
        "Я буду надсилати тобі щоденні фізичні завдання 💪\n"
        "Натискай «Я виконав» після виконання!"
    )

@dp.message_handler(lambda message: message.text == "✅ Я виконав")
async def done_handler(message: types.Message):
    today = datetime.date.today().isoformat()

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT streak, last_done FROM users WHERE user_id = ?", (message.chat.id,)) as cursor:
            row = await cursor.fetchone()

        if row:
            streak, last_done = row

            if last_done == today:
                await message.answer("Ти вже сьогодні відзначив виконання 😉")
                return

            yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

            if last_done == yesterday:
                streak += 1
            else:
                streak = 1

            await db.execute(
                "UPDATE users SET streak = ?, last_done = ? WHERE user_id = ?",
                (streak, today, message.chat.id)
            )
            await db.commit()

            await message.answer(
                f"{random.choice(replies)}\n"
                f"🔥 Твоя серія днів: {streak}"
            )

async def send_daily_task():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            users = await cursor.fetchall()

        for user in users:
            try:
                await bot.send_message(
                    user[0],
                    random.choice(tasks),
                    reply_markup=done_button
                )
            except:
                pass

async def on_startup(dp):
    await init_db()
    if not scheduler.running:
        scheduler.start()

scheduler = AsyncIOScheduler()
scheduler.add_job(send_daily_task, 'cron', hour=9, minute=0)

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)