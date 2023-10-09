from vkbottle import Keyboard, Text, KeyboardButtonColor

START = (
    Keyboard(one_time=True, inline=False)
    .add(Text("Последние новости"))
    .row()
    .add(Text("Новости"))
    .row()
    .add(Text("Настроить рассылку новостей"))
    .get_json()
) 

YES_NO = (
    Keyboard(one_time=True, inline=False)
    .add(Text("Да"), color=KeyboardButtonColor.POSITIVE)
    .add(Text("Нет"), color=KeyboardButtonColor.NEGATIVE)
    .get_json()
)

SUB_SETTINGS = (
    Keyboard(one_time=True, inline=False)
    .add(Text("Период рассылки новостей"))
    .add(Text("Количество присылаемых новостей"))
    .get_json()
)

TIME_SETTINGS = (
    Keyboard(one_time=True, inline=False)
    .add(Text("24 часа"))
    .add(Text("12 часов"))
    .row()
    .add(Text("6 часов"))
    .add(Text("2 часа"))
    .row()
    .add(Text("1 час"))
    .get_json()
)