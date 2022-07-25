from vkbottle.tools import Keyboard, Text, KeyboardButtonColor


SpamVariantsKeyboard = Keyboard(one_time=True, inline=False)
SpamVariantsKeyboard.add(
    Text('Рассылка, если расписание поменялось', '{"command": "on_change"}'),
    KeyboardButtonColor.PRIMARY)

SpamVariantsKeyboard.row()
SpamVariantsKeyboard.add(
    Text('Рассылка n раз в день', '{"command": "n_times"}'),
    KeyboardButtonColor.SECONDARY)

SpamVariantsKeyboard.row()
SpamVariantsKeyboard.add(
    Text('Рассылка каждые n часов', '{"command": "every_n_hours"}'),
    KeyboardButtonColor.SECONDARY)

SpamVariantsKeyboard = SpamVariantsKeyboard.get_json()


AmountVariantsKeyboard = Keyboard(one_time=True, inline=False)
AmountVariantsKeyboard.add(Text('Два раза в день', '{"command": "two_times"}'))
AmountVariantsKeyboard.row()
AmountVariantsKeyboard.add(Text('Три раза в день', '{"command": "three_times"}'))
AmountVariantsKeyboard.row()
AmountVariantsKeyboard.add(Text('Четыре раза в день', '{"command": "four_times"}'))
AmountVariantsKeyboard.row()
AmountVariantsKeyboard.add(Text('Пять раз в день', '{"command": "five_times"}'))
AmountVariantsKeyboard = AmountVariantsKeyboard.get_json()


GetScheduleKeyboard = Keyboard(one_time=True, inline=False)
GetScheduleKeyboard.add(Text('Получить расписание', '{"command": "get_schedule"}'),
                        KeyboardButtonColor.PRIMARY)
GetScheduleKeyboard = GetScheduleKeyboard.get_json()
