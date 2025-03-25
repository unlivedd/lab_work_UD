import asyncio
import re
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import BOT_TOKEN
from db import add_task, get_tasks, update_task, delete_tasks_by_date
from datetime import datetime


bot = Bot(token=BOT_TOKEN)


dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Я бот для управления задачами. Введи /help, чтобы узнать команды.")

@dp.message(Command("help"))
async def help_command(message: types.Message):
    text = (
        "/add <текст> <дата> - Добавить задачу (дата в формате YYYY-MM-DD HH:MM)\n"
        "/list - Показать список задач\n"
        "/done <ID> - Отметить задачу выполненной\n"
        "/delete <дата> - Удалить задачи на указанную дату\n"
    )
    await message.answer(text)

@dp.message(Command("add"))
async def add_task_handler(message: types.Message):
    try:
        match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})$', message.text)
        if not match:
            raise ValueError("Неверный формат даты. Используйте: ГГГГ-ММ-ДД ЧЧ:ММ")
        
        deadline_str = match.group(1)
        text = message.text.replace(f"/add {deadline_str}", "").strip()
        
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")
        
        user_id = message.from_user.id
        add_task(user_id, text, deadline)
        await message.answer("✅ Задача добавлена!")
    except ValueError as ve:
        await message.answer(f"🚫 Ошибка: {ve}")
    except Exception:
        await message.answer("❌ Пример: /add Купить молоко 2025-03-22 15:30")

@dp.message(Command("list"))
async def list_tasks(message: types.Message):
    user_id = message.from_user.id
    tasks = get_tasks(user_id)
    if not tasks:
        await message.answer("У вас нет задач.")
        return

    response = "Ваши задачи:\n"
    now = datetime.now()
    for task in tasks:
        try:
            if isinstance(task["deadline"], str):
                deadline = datetime.strptime(task["deadline"], "%Y-%m-%d %H:%M")
            else:
                deadline = task["deadline"]
            
            days_left = (deadline - now).days
            hours_left = (deadline - now).seconds // 3600
            status = "✅" if task.get("completed", False) else "❌"
            response += (
                f"{task['_id']} | {task['text']} | "
                f"{deadline.strftime('%Y-%m-%d %H:%M')} | "
                f"{status} (Осталось: {days_left} дн. {hours_left} ч.)\n"
            )
        except Exception as e:
            response += f"{task['_id']} | 🚫 Некорректные данные: {e}\n"

    await message.answer(response)

@dp.message(Command("done"))
async def complete_task(message: types.Message):
    try:
        _, task_id = message.text.split(maxsplit=1)
        modified_count = update_task(task_id, completed=True)
        
        if modified_count == 0:
            await message.answer("Задача не найдена или ID некорректен!")
        else:
            await message.answer("✅ Задача выполнена!")
    except Exception as e:
        print(f"Ошибка: {e}")
        await message.answer("Использование: /done <ID>")

@dp.message(Command("delete"))
async def delete_task_handler(message: types.Message):
    try:
        _, date = message.text.split(maxsplit=1)
        user_id = message.from_user.id
        delete_tasks_by_date(user_id, date)
        await message.answer("Задачи на указанную дату удалены!")
    except:
        await message.answer("Использование: /delete <дата> (формат YYYY-MM-DD)")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
