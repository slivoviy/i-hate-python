import logging
import re
from logging import Formatter
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.utils.formatting import Text

import configparser
import service
import keyboards


config = configparser.ConfigParser()
config.read("config.ini")

bot = Bot(token=config["Telegram"]["bot_token"])
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

csv_file = "log.csv"
csv_handler = logging.FileHandler(
    csv_file, mode="a"
) 
csv_handler.setFormatter(Formatter("%(asctime)s,%(levelname)s,%(user_id)s,%(message)s"))

logger = logging.getLogger()
logger.setLevel(level=logging.INFO)
logger.addHandler(csv_handler)

class UserStates(StatesGroup):
    MAIN = State()
    LAST_NEWS = State()
    KEYWORD_NEWS = State()                
    SUB_SETTINGS = State()             
    SUB_PERIOD = State()
    SUB_AMOUNT = State()


@dp.message_handler(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    await state.set_state(UserStates.MAIN)
    
    await message.answer(
        "Привет! Наш бот позволяет вам читать все самые свежие новости в "
        "мире. Для управления воспользуйтесь кнопками внизу.\n"
        "Источник новостей: тг-канал Раньше всех. Ну почти.",
        reply_markup=keyboards.MAIN
    )
    
    logger.info('Клиент находится в меню', extra={'user_id': message.from_user.id})


@dp.message_handler(Text(equals="Последние новости"), state=UserStates.MAIN)
async def news_handler(message: types.Message, state: FSMContext):
    logger.info('Клиент хочет получить последние новости', extra={'user_id': message.from_user.id})
    await state.set_state(UserStates.LAST_NEWS)
    await message.answer("Сколько новостей прислать? (1-10)")


@dp.message_handler(lambda message: message.text.isdigit(), state=UserStates.LAST_NEWS)
async def news_amount_handler(message: types.Message, state: FSMContext):
    amount = int(message.text)
    if not (1 <= amount <= 10):
        await message.answer("Я не понял тебя. Введи число от 1 до 10, пожалуйста.")
    else:
        news = service.get_news(amount)
        for n in news:
            await message.answer(n)
        await state.set_state(UserStates.MAIN)
        logger.info('Клиент получил последние новости', extra={'user_id': message.from_user.id})
        logger.info('Клиент находится в меню', extra={'user_id': message.from_user.id})


@dp.message_handler(lambda message: not message.text.isdigit(), state=UserStates.LAST_NEWS)
async def news_amount_invalid_handler(message: types.Message):
    await message.answer("Я не понял тебя. Введи число от 1 до 10, пожалуйста.")


@dp.message_handler(Text(equals="Новости по ключевому слову"), state=UserStates.MAIN)
async def keyword_news_handler(message: types.Message, state: FSMContext):
    await state.set_state(UserStates.KEYWORD_NEWS)
    await message.answer("Введите ключевое слово, по которому провести поиск")
    logger.info('Клиент хочет получить новости по ключевому слову', extra={'user_id': message.from_user.id})


@dp.message_handler(state=UserStates.KEYWORD_NEWS)
async def news_search_handler(message: types.Message, state: FSMContext):
    word = message.text
    news = service.get_news_by_keyword(word)
    if news:
        for n in news:
            await message.answer(n, reply_markup=keyboards.MAIN)
        await state.set_state(UserStates.MAIN)
        logger.info('Клиент получил новости по ключевому слову', extra={'user_id': message.from_user.id})
    else:
        await message.answer(
            "Извините, по данному ключевому слову ничего не нашлось",
            reply_markup=keyboards.MAIN
        )
        await state.set_state(UserStates.MAIN)
    logger.info('Клиент находится в меню', extra={'user_id': message.from_user.id})


@dp.message_handler(Text(equals="Настроить рассылку новостей"), state=UserStates.MAIN)
async def sub_settings_handler(message: types.Message, state: FSMContext):
    await state.set_state(UserStates.SUB_SETTINGS)
    await message.answer(
        "Выберите необходимую настройку", reply_markup=keyboards.SUB_SETTINGS
    )
    logger.info('Клиент хочет настроить рассылку', extra={'user_id': message.from_user.id})


@dp.message_handler(Text(equals="Период рассылки новостей"), state=UserStates.SUB_SETTINGS)
async def sub_period_handler(message: types.Message, state: FSMContext):
    await state.set_state(UserStates.SUB_PERIOD)
    await message.answer("Выберите из списка ниже", reply_markup=keyboards.TIME_SETTINGS)
    logger.info('Клиент хочет настроить период рассылки', extra={'user_id': message.from_user.id})


@dp.message_handler(Text(equals="Количество присылаемых новостей"), state=UserStates.SUB_SETTINGS)
async def sub_amount_handler(message: types.Message, state: FSMContext):
    await state.set_state(UserStates.SUB_AMOUNT)
    await message.answer("Выберите число присылаемых новостей (1-20)")
    logger.info('Клиент хочет настроить количество новостей', extra={'user_id': message.from_user.id})


@dp.message_handler(state=UserStates.SUB_PERIOD)
async def sub_period_set_handler(message: types.Message, state: FSMContext):
    hours_match = re.match(r"(\d+)\sчас(ов|а|)?", message.text)

    if hours_match:
        sub_period = int(hours_match.groups()[0])

        await state.finish()
        await message.answer(
            f"Запомнил! Теперь новости будут приходить каждые {sub_period} час(ов)!",
            reply_markup=keyboards.MAIN
        )
        logger.info('Клиент настроил период рассылки', extra={'user_id': message.from_user.id})
    else:
        await message.answer("Пожалуйста, введите количество часов в формате: '3 часа' или '1 час'")

    logger.info('Клиент находится в меню', extra={'user_id': message.from_user.id})


@dp.message_handler(state=UserStates.SUB_AMOUNT)
async def sub_amount_set_handler(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply("Я не понял тебя. Введи число от 1 до 20, пожалуйста.")
    else:
        amount = int(message.text)
        if not 1 <= amount <= 20:
            await message.reply("Я не понял тебя. Введи число от 1 до 20, пожалуйста.")
        else:
            
            await state.finish()
            await message.reply(
                f"Запомнил! Теперь буду присылать именно {amount} новост(ей).",
                reply_markup=keyboards.MAIN
            )
            logger.info('Клиент настроил количество новостей', extra={'user_id': message.from_user.id})


@dp.message_handler(lambda message: message.text.isdigit(), state=UserStates.SUB_AMOUNT)
async def sub_amount_set_handler(message: types.Message, state: FSMContext):
    amount = int(message.text)
    if not (1 <= amount <= 20):
        await message.answer("Я не понял тебя. Введи число от 1 до 20, пожалуйста.")
    else:
        await state.set_state(UserStates.MAIN)
        await message.answer(
            f"Запомнил! Теперь буду присылать именно {amount} новост(ей).",
            reply_markup=keyboards.MAIN
        )
        logger.info('Клиент настроил количество новостей', extra={'user_id': message.from_user.id})
        logger.info('Клиент находится в меню', extra={'user_id': message.from_user.id})


@dp.message_handler(lambda message: not message.text.isdigit(), state=UserStates.SUB_AMOUNT)
async def sub_amount_invalid_handler(message: types.Message):
    await message.answer("Я не понял тебя. Введи число от 1 до 20, пожалуйста.")


if __name__ == '__main__':
    dp.run_polling(bot)
