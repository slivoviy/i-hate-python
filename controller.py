from vkbottle import BaseStateGroup, LoopWrapper
from vkbottle.bot import Message, Bot
from typing import Optional
from logging import Formatter
import service
import keyboards
import configparser
import logging


class UserStates(BaseStateGroup):
    MAIN = "main"
    LAST_NEWS = "last_news"
    KEYWORD_NEWS = "keyword_news"
    ENABLE_SUB = "enable_sub"
    SUB_SETTINGS = "sub_settings"
    SUB_PERIOD = "sub_period"
    SUB_AMOUNT = "sub_amount"


config = configparser.ConfigParser()
config.read("config.ini")

bot = Bot(token=config["VK"]["group_key"])

sub_period = 6
sub_amount = 10

csv_file = "log.csv"
csv_handler = logging.FileHandler(
    csv_file, mode="a"
) 
csv_handler.setFormatter(Formatter("%(asctime)s,%(levelname)s,%(user_id)s,%(message)s"))

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(csv_handler)


def start_bot():
    bot.run_forever()


@bot.on.message(text="Начать")
async def start_handler(message: Message):
    await bot.state_dispenser.set(message.peer_id, UserStates.MAIN)
    await message.answer(
        "Привет! Наш бот позволяет вам читать все самые свежие новости в \
        мире. Для управления воспользуйтесь кнопками внизу.\n\
        Источник новостей: тг-канал Раньше всех. Ну почти.",
        keyboard=keyboards.MAIN,
    )
    logger.info('Клиент находится в меню', extra={'user_id': message.peer_id})


@bot.on.message(state=UserStates.MAIN, text="Последние новости")
async def news_handler(message: Message):
    logger.info('Клиент хочет получить последние новости', extra={'user_id': message.peer_id})
    await bot.state_dispenser.set(message.peer_id, UserStates.LAST_NEWS)
    await message.answer("Сколько новостей прислать? (1-10)")


@bot.on.message(state=UserStates.LAST_NEWS, text="<amount>")
async def news_amount_handler(message: Message, amount: Optional[str]):
    if not amount.isnumeric():
        await message.answer("Я не понял тебя. Введи число от 1 до 10, пожалуйста.")
    else:
        amount = int(amount)
        if not (1 <= amount <= 10):
            await message.answer("Я не понял тебя. Введи число от 1 до 10, пожалуйста.")
        else:
            news = service.get_news(amount)
            for n in news:
                await message.answer(n, keyboard=keyboards.MAIN)
            await bot.state_dispenser.set(message.peer_id, UserStates.MAIN)
            logger.info('Клиент получил последние новости', extra={'user_id': message.peer_id})
            logger.info('Клиент находится в меню', extra={'user_id': message.peer_id})


@bot.on.message(state=UserStates.MAIN, text="Новости по ключевому слову")
async def keyword_news_handler(message: Message):
    await bot.state_dispenser.set(message.peer_id, UserStates.KEYWORD_NEWS)
    await message.answer("Введите ключевое слово, по которому провести поиск")
    logger.info('Клиент хочет получить новости по ключевому слову', extra={'user_id': message.peer_id})


@bot.on.message(state=UserStates.KEYWORD_NEWS, text="<word>")
async def news_search_handler(message: Message, word: Optional[str]):
    news = service.get_news_by_keyword(word)
    if len(news) > 0:
        for n in news:
            await message.answer(n, keyboard=keyboards.MAIN)
        await bot.state_dispenser.set(message.peer_id, UserStates.MAIN)
        logger.info('Клиент получил новости по ключевому слову', extra={'user_id': message.peer_id})
        logger.info('Клиент находится в меню', extra={'user_id': message.peer_id})
    else:
        await message.answer(
            "Извините, по данному ключевому слову ничего не нашлось",
            keyboard=keyboards.MAIN,
        )
        await bot.state_dispenser.set(message.peer_id, UserStates.MAIN)


@bot.on.message(state=UserStates.MAIN, text="Настроить рассылку новостей")
async def sub_settings_handler(message: Message):
    await bot.state_dispenser.set(message.peer_id, UserStates.SUB_SETTINGS)
    await message.answer(
        "Выберите необходимую настройку", keyboard=keyboards.SUB_SETTINGS
    )
    logger.info('Клиент хочет настроить рассылку', extra={'user_id': message.peer_id})


@bot.on.message(state=UserStates.SUB_SETTINGS, text="Период рассылки новостей")
async def sub_period_handler(message: Message):
    await bot.state_dispenser.set(message.peer_id, UserStates.SUB_PERIOD)
    await message.answer("Выберите из списка ниже", keyboard=keyboards.TIME_SETTINGS)
    logger.info('Клиент хочет настроить период рассылки', extra={'user_id': message.peer_id})


@bot.on.message(state=UserStates.SUB_SETTINGS, text="Количество присылаемых новостей")
async def sub_amount_handler(message: Message):
    await bot.state_dispenser.set(message.peer_id, UserStates.SUB_AMOUNT)
    await message.answer("Выберите число присылаемых новостей (1- 20)")
    logger.info('Клиент хочет настроить количество', extra={'user_id': message.peer_id})


@bot.on.message(state=UserStates.SUB_PERIOD, text="<hours> часа")
@bot.on.message(state=UserStates.SUB_PERIOD, text="<hours> часов")
@bot.on.message(state=UserStates.SUB_PERIOD, text="<hours> час")
async def sub_period_set_handler(message: Message, hours: Optional[int]):
    sub_period = hours
    await bot.state_dispenser.set(message.peer_id, UserStates.MAIN)
    await message.answer(
        "Запомнил! Теперь новости будут приходить с такой частотой",
        keyboard=keyboards.MAIN,
    )
    logger.info('Клиент настроил период рассылки', extra={'user_id': message.peer_id})
    logger.info('Клиент находится в меню', extra={'user_id': message.peer_id})


@bot.on.message(state=UserStates.SUB_AMOUNT, text="<amount>")
async def sub_amount_set_handler(message: Message, amount: Optional[str]):
    if not amount.isnumeric():
        await message.answer("Я не понял тебя. Введи число от 1 до 20, пожалуйста.")
    else:
        amount = int(amount)
        if not (1 <= amount <= 20):
            await message.answer("Я не понял тебя. Введи число от 1 до 20, пожалуйста.")
        else:
            sub_amount = amount
            await bot.state_dispenser.set(message.peer_id, UserStates.MAIN)
            await message.answer(
                "Запомнил! Теперь буду присылать именно столько новостей",
                keyboard=keyboards.MAIN,
            )
            logger.info('Клиент настроил количество новостей', extra={'user_id': message.peer_id})
            logger.info('Клиент находится в меню', extra={'user_id': message.peer_id})
