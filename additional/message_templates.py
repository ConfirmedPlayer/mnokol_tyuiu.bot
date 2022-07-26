start_message = '''
Привет! Я — бот для получения расписания. С моей помощью можно легко и просто получать расписание пар для своей группы.
Также бот владеет базой данных учителей МПК ТИУ. Зная фамилию преподавателя, можно узнать его полное ФИО.
Команда: /преп <фамилия>


Первоначальная настройка:

Добавьте группу с помощью команды: /группа <название>
Пример: /группа пкст-20-(9)-2


После, отправьте команду:
/подписка
Настроив подписку, вы сможете получать расписание по времени или сразу как его изменили.
'''

on_invite_message = '''
Спасибо, что пригласили меня в беседу!

Для более корректной работы бота рекомендуется дать права администратора или доступ к переписке.
Это требуется для того, чтобы бот беспрепятственно получал доступ к командам.
'''

group_not_found_message = '''
Группа не найдена.
Пожалуйста, проверьте написание и повторите попытку.
'''

set_group_chat_success = '''
Данной беседе присвоена группа: "{group}".
Это значит, что в этом диалоге бот будет выдавать расписание для этой группы.
'''

set_group_private_success = '''
Диалогу с пользователем @id{user_id} присвоена группа: "{group}".
Это значит, что в этом диалоге бот будет выдавать расписание для этой группы.
'''

set_group_success2 = '''
Теперь вы можете получать расписание с помощью клавиатуры бота под полем ввода сообщения или используя команду /расписание.
Но для экономии времени и быстроты получения расписания, рекомендуем выбрать подписку. Отправьте команду:
/подписка
для получения дальнейших инструкций.
'''

group_not_set_message = '''
Ошибка. Сначала добавьте группу с помощью команды:
/группа <название>

Пример: /группа пкст-20-(9)-2
'''

choose_subscription_message = '''
Пожалуйста, выберите тип рассылки.
'''

already_subscribed_message = '''
Вы уже подписаны на рассылку.
Отписаться можно командой:
/отписаться
'''

incorrect_number = '''
Неверное число.
'''

incorrect_number_range = '''
Число должно быть в диапазоне от 1 до 99.
'''

subscription_successful = '''
Вы успешно подписались.
'''

unsubscription_successful = '''
Вы успешно отписались от рассылки.
'''

not_subscribed_error = '''
Вы не подписаны на рассылку.
'''

every_n_hours_method_template = '''
Пожалуйста, отправьте команду
/рассылка <число>

Пример: /рассылка 5
Значит, рассылка каждые 5 часов.
'''

subscribed_to_2_times = '''
Вы успешно подписались.
Расписание будет отправляться два раза в день: в 06:00 утра и 19:00 вечера.
'''

subscribed_to_3_times = '''
Вы успешно подписались.
Расписание будет отправляться три раза в день: в 06:00 утра, 12:00 дня и 18:00 вечера.
'''

subscribed_to_4_times = '''
Вы успешно подписались.
Расписание будет отправляться четыре раза в день: в 06:00 утра, 12:00 дня, 16:00 и 20:00 вечера.
'''

subscribed_to_5_times = '''
Вы успешно подписались.
Расписание будет отправляться пять раз в день: в 06:00 утра, 12:00 и 15:00 дня, 18:00 и 21:00 вечера.
'''

on_change_method_subscribed = '''
Вы успешно подписались.
Теперь вам будет отправлено новое расписание при любом его изменении.
'''

bot_was_added_admin_log = '''
Бот был добавлен в беседу:

{}
'''