from vkbottle import BaseStateGroup, Keyboard
from vkbottle.bot import Message, Bot
from typing import Optional
import service
import keyboards
import configparser


class UserStates(BaseStateGroup):
    MAIN = "main"
    LAST_NEWS = "last_news"
    KEYWORD_NEWS = "keyword_news"
    ENABLE_SUB = "enable_sub"
    SUB_SETTINGS = "subs_settings"
    SUB_PERIOD = "sub_period"
    SUB_AMOUNT = "sub_amount"


config = configparser.ConfigParser()
config.read("config.ini")

bot = Bot(token='vk1.a._VMMcenwxoUJeUuNEXX15VupIMrYky0hsY4Bb-_beGCzber9nGC57d2pcFF6YoV_j1q57H_2Jw67U1iWLD19hkctse5UPnbNtxNNOb1x0EeypQs_bEqUV4_xHpOoXQqRO71x4i0Ii2jg03cDPjZKfhzOwn6_xJRkw583SvpMnI-keG00OxoJRf_81NsJKfOXV1vGItRqWcaStTs_sJl7EA')


def start_bot():
    bot.run_forever()


@bot.on.message(text="Начать")
async def start_handler(message: Message):
    await bot.state_dispenser.set(UserStates.MAIN)
    await message.answer(
        "Привет! Наш бот позволяет вам читать все самые свежие новости в \
        мире. Для управления воспользуйтесь кнопками внизу.\n\
        Источник новостей: тг-канал Раньше всех. Ну почти.",
        keyboard=keyboards.START,
    )

@bot.on.message(state=UserStates.MAIN, text="Последние новости")
async def news_handler(message: Message):
    await bot.state_dispenser.set(UserStates.LAST_NEWS)
    await message.answer("Сколько новостей прислать? (1-10)")

@bot.on.message(state=UserStates.LAST_NEWS, text="<amount>")
async def news_amount_handler(message: Message, amount: Optional[str]):
    if not amount.isnumeric():
        await message.answer("Я не понял тебя. Введи число от 1 до 10, пожалуйста.")
    else:
        amount = int(amount)
        if not(1 <= amount <= 10):
            await message.answer("Я не понял тебя. Введи число от 1 до 10, пожалуйста.")
        else:
            news = service.get_news(amount)
            for n in news:
                await message.answer(n)
