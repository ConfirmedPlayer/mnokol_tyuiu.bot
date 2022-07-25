from additional.chrome_options import (selenium_args,
                                       pyppeteer_args,
                                       pyppeteer_screenshot_options,
                                       pyppeteer_goto_options)
from additional.keyboards import SpamVariantsKeyboard, AmountVariantsKeyboard, GetScheduleKeyboard
from config import (token,
                    schedule_menu_url,
                    start_message,
                    on_invite_message,
                    message_send_url,
                    admin_user_id,
                    group_id)

from ast import literal_eval
from bs4 import BeautifulSoup
from datetime import datetime
from loguru import logger
from pyppeteer import launch
from pytz import timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from vk_api import VkApi
from vk_api.upload import VkUpload
from vk_api.utils import get_random_id
from vkbottle import GroupEventType, GroupTypes, load_blueprints_from_package
from vkbottle.bot import Bot, Message, rules
from vkbottle.tools import PhotoMessageUploader
import aiofiles
import asyncio
import re
import requests
import sys
import time


logger.remove()
logger.add('logs.log', format='{time} {level} {message}', level='DEBUG')
logger_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "{extra[ip]} {extra[user]} - <level>{message}</level>"
)
logger.configure(extra={"ip": "", "user": ""})
logger.add(sys.stderr, format=logger_format, level='INFO')


bot = Bot(token)
bot.labeler.vbml_ignore_case = True


vk_session = VkApi(token=token)
vk = vk_session.get_api()


tasks = []


@logger.catch
async def get_group(raw_group: str):
    try:
        page = await pyppeteer_browser.newPage()
        await page.goto(schedule_menu_url)
        html = await page.content()

        soup = BeautifulSoup(html, 'lxml')
        zero_group = soup.find('option').find_next()
        all_groups = zero_group.find_next_siblings()

        group = re.findall(pattern=re.escape(raw_group),
                           string=str(all_groups),
                           flags=re.IGNORECASE)
        if not group:
            return False
        else:
            group_tag = soup.find('option', string=group[0])
            attributes_dict = group_tag.attrs

            sid = attributes_dict.get('sid')
            gr = attributes_dict.get('value')

            if any((sid, gr)) is None:
                return False
            else:
                schedule_url = f'https://temnomor.ru/api/groups?group={group}&sid={sid}&gr={gr}'
                return {'URL': schedule_url, 'group': group}
    finally:
        await page.close()


@logger.catch
async def make_screenshot(URL: str, group: str):
    local_screenshot_options = pyppeteer_screenshot_options

    group_filename = group.strip('()') + '.png'
    local_screenshot_options.update(path=group_filename)

    try:
        page = await pyppeteer_browser.newPage()
        await page.goto(URL, options=pyppeteer_goto_options)
        await page.screenshot(options=local_screenshot_options)
        return await PhotoMessageUploader(bot.api).upload(group_filename)
    finally:
        await page.close()


@logger.catch
def sync_get_group(raw_group: str):
    try:
        browser = webdriver.Chrome(options=selenium_args)
        browser.get(schedule_menu_url)
        html = browser.page_source

        soup = BeautifulSoup(html, 'lxml')
        zero_group = soup.find('option').find_next()
        all_groups = zero_group.find_next_siblings()

        group = re.findall(pattern=re.escape(raw_group),
                           string=str(all_groups),
                           flags=re.IGNORECASE)[0]
        group_tag = soup.find('option', string=group)
        attributes_dict = group_tag.attrs

        sid = attributes_dict.get('sid')
        gr = attributes_dict.get('value')

        schedule_url = f'https://temnomor.ru/api/groups?group={group}&sid={sid}&gr={gr}'
        return {'URL': schedule_url, 'group': group}
    finally:
        browser.quit()


@logger.catch
def sync_make_screenshot(URL: str, group: str):
    group_filename = group.strip('()') + '.png'
    try:
        browser = webdriver.Chrome(options=selenium_args)

        S = lambda x: browser.execute_script('return document.body.parentNode.scroll' + x) # noqa

        browser.get(URL)
        browser.set_window_size(S('Width'), S('Height'))
        browser.maximize_window()
        browser.find_element(By.TAG_NAME, 'html').screenshot(group_filename)

        upload = VkUpload(vk)
        photo_obj = upload.photo_messages(group_filename)[0]

        return 'photo{owner_id}_{id}_{access_key}'.format(**photo_obj)
    finally:
        browser.quit()


@logger.catch
def spam_every_n_hours(peer_id: int, hours: int):
    logger.success(f'Spam every {hours} hours for {peer_id} was started')

    while db.get(peer_id).get('subscribed'):
        group_and_url = sync_get_group(db.get(peer_id).get('group'))
        uploaded_screenshot = sync_make_screenshot(group_and_url.get('URL'),
                                                   group_and_url.get('group'))

        requests.get(message_send_url.format(token=token,
                                             peer_id=peer_id,
                                             attachment=uploaded_screenshot,
                                             random_id=get_random_id()))
        time.sleep(hours * 3600)


@logger.catch
def spam_n_times_a_day(peer_id: int, amount: int):
    logger.success(f'Spam {amount} times for {peer_id} was started')

    time_zone = timezone('Asia/Yekaterinburg')

    two_times_range = ('06:00', '06:01',
                       '19:00', '19:01')

    three_times_range = ('06:00', '06:01', '12:00',
                         '12:01', '18:00', '18:01')

    four_times_range = ('06:00', '06:01', '12:00', '12:01',
                        '16:00', '16:01', '20:00', '20:01')

    five_times_range = ('06:00', '06:01', '12:00', '12:01', '15:00',
                        '15:01', '18:00', '18:01', '21:00', '21:01')

    match amount:
        case 2:
            while db.get(peer_id).get('subscribed'):
                time_now = datetime.now().strftime('%H:%M')
                if time_now in two_times_range:
                    group_and_url = sync_get_group(db.get(peer_id).get('group'))
                    uploaded_screenshot = sync_make_screenshot(group_and_url.get('URL'),
                                                               group_and_url.get('group'))
                    requests.get(message_send_url.format(token=token,
                                                         peer_id=peer_id,
                                                         attachment=uploaded_screenshot,
                                                         random_id=get_random_id()) +
                                 f'&message={time_now}')
                    time.sleep(18000)

                time.sleep(15)
        case 3:
            while db.get(peer_id).get('subscribed'):
                time_now = datetime.now().strftime('%H:%M')
                if time_now in three_times_range:
                    group_and_url = sync_get_group(db.get(peer_id).get('group'))
                    uploaded_screenshot = sync_make_screenshot(group_and_url.get('URL'),
                                                               group_and_url.get('group'))
                    requests.get(message_send_url.format(token=token,
                                                         peer_id=peer_id,
                                                         attachment=uploaded_screenshot,
                                                         random_id=get_random_id()) +
                                 f'&message={time_now}')
                    time.sleep(14000)

                time.sleep(15)
        case 4:
            while db.get(peer_id).get('subscribed'):
                time_now = datetime.now().strftime('%H:%M')
                if time_now in four_times_range:
                    group_and_url = sync_get_group(db.get(peer_id).get('group'))
                    uploaded_screenshot = sync_make_screenshot(group_and_url.get('URL'),
                                                               group_and_url.get('group'))
                    requests.get(message_send_url.format(token=token,
                                                         peer_id=peer_id,
                                                         attachment=uploaded_screenshot,
                                                         random_id=get_random_id()) +
                                 f'&message={time_now}')
                    time.sleep(10000)

                time.sleep(15)
        case 5:
            while db.get(peer_id).get('subscribed'):
                time_now = datetime.now().strftime('%H:%M')
                if time_now in five_times_range:
                    group_and_url = sync_get_group(db.get(peer_id).get('group'))
                    uploaded_screenshot = sync_make_screenshot(group_and_url.get('URL'),
                                                               group_and_url.get('group'))
                    requests.get(message_send_url.format(token=token,
                                                         peer_id=peer_id,
                                                         attachment=uploaded_screenshot,
                                                         random_id=get_random_id()) +
                                 f'&message={time_now}')
                    time.sleep(7000)

                time.sleep(15)


@logger.catch
def spam_on_change(peer_id: int):
    group_and_url = sync_get_group(db.get(peer_id).get('group'))

    request = requests.get(group_and_url.get('URL'))
    first_html = r''.join(request.text)

    while db.get(peer_id).get('subscribed'):
        request = requests.get(group_and_url.get('URL'))
        new_html = r''.join(request.text)
        if first_html != new_html and 'lenta_m' in new_html:
            first_html = new_html
            uploaded_screenshot = sync_make_screenshot(group_and_url.get('URL'),
                                                       group_and_url.get('group'))
            requests.get(message_send_url.format(token=token,
                                                 peer_id=peer_id,
                                                 attachment=uploaded_screenshot,
                                                 random_id=get_random_id()) +
                         '&message=Изменение в расписании')
            time.sleep(1000)
        else:
            time.sleep(1000)


@bot.on.chat_message(text='/группа <raw_group>')
async def set_group_public(message: Message, raw_group: str):
    global db

    if len(raw_group) < 9:
        await message.reply('Группа не найдена. \
            Пожалуйста, проверьте написание и повторите попытку')

    group_and_url = await get_group(raw_group)
    if not isinstance(group_and_url, dict):

        await message.reply('Группа не найдена. \
            Пожалуйста, проверьте написание и повторите попытку')
    else:
        group = group_and_url.get('group')

        if message.peer_id in db.keys():
            db[message.peer_id].update(group=group,
                                       URL=group_and_url.get('URL'))
        else:
            db[message.peer_id] = {'group': group,
                                   'URL': group_and_url.get('URL')}

        async with aiofiles.open('DB.txt', 'w', encoding='UTF-8') as temp:
            await temp.write(str(db))

        await message.reply(f'Данной беседе присвоена группа: "{group}". Это значит, что \
            в этом диалоге бот будет выдавать расписание для этой группы.')

        await message.answer('Теперь вы можете получать расписание с помощью клавиатуры бота \
            под полем ввода сообщения.\n\nНо для экономии времени и быстроты получения \
                расписания, рекомендуем выбрать подписку. Отправьте команду:\n/подписка\n \
                    для получения дальнейших инструкций.', keyboard=GetScheduleKeyboard)


@bot.on.private_message(text='/группа <raw_group>')
async def set_group_private(message: Message, raw_group):
    global db

    group_and_url = await get_group(raw_group)
    if not isinstance(group_and_url, dict):

        await message.reply('Группа не найдена. \
            Пожалуйста, проверьте написание и повторите попытку')
    else:
        group = group_and_url.get('group')

        if message.peer_id in db.keys():
            db[message.peer_id].update(group=group,
                                       URL=group_and_url.get('URL'))
        else:
            db[message.peer_id] = {'group': group,
                                   'URL': group_and_url.get('URL')}

        async with aiofiles.open('DB.txt', 'w', encoding='UTF-8') as temp:
            await temp.write(str(db))

        await message.reply(f'Диалогу с пользователем @id{message.peer_id} присвоена \
            группа: "{group}". Это значит, что в этом диалоге бот будет \
                выдавать расписание для этой группы.')

        await message.answer('Теперь вы можете получать расписание с помощью клавиатуры бота \
            под полем ввода сообщения.\n\nНо для экономии времени и быстроты получения \
                расписания, рекомендуем выбрать подписку. Отправьте команду:\n/подписка\n \
                    для получения дальнейших инструкций.', keyboard=GetScheduleKeyboard)


@bot.on.message(text='/расписание')
async def show_schedule(message: Message):
    if user := db.get(message.peer_id) is None:
        await message.reply('Ошибка. Сначала добавьте группу с помощью команды: \
            \n/группа <название>\n\nПример: /группа пкст-20-(9)-2')
    else:
        if user := db.get(message.peer_id):
            uploaded_screenshot = await make_screenshot(user.get('URL'),
                                                        user.get('group'))
            await message.answer(attachment=uploaded_screenshot)


@bot.on.message(text='/подписка')
async def subscription_types(message: Message):
    if message.peer_id in db.keys():
        if not db.get(message.peer_id).get('subscribed'):
            await message.reply('Пожалуйста, выберите тип рассылки.',
                                keyboard=SpamVariantsKeyboard)
        else:
            await message.reply('Вы уже подписаны на рассылку.\nОтписаться можно командой: \
                /отписаться')
    else:
        await message.reply('Ошибка. Сначала добавьте группу с помощью команды: \
            \n/группа <название>\n\nПример: /группа пкст-20-(9)-2')


@bot.on.message(text='/рассылка <digit>')
async def subscribe_to_first_method(message: Message, digit: str):
    global db

    if digit.isdigit():
        n = int(digit)

        if not 100 > n > 0:
            await message.reply('Число должно быть в диапазоне от 1 до 99.')
        else:
            if message.peer_id not in db.keys():
                await message.reply('Ошибка. Сначала добавьте группу с помощью команды:\n \
                    /группа <название>\n\nПример: /группа пкст-20-(9)-2')
            else:
                if db.get(message.peer_id).get('subscribed'):
                    await message.reply('Вы уже подписаны на рассылку.\nОтписаться можно командой: \
                        /отписаться')
                else:
                    db[message.peer_id]['method'] = 'every_n_hours'
                    db[message.peer_id]['hours'] = n
                    db[message.peer_id]['subscribed'] = True

                    async with aiofiles.open('DB.txt', 'w', encoding='UTF-8') as temp:
                        await temp.write(str(db))

                    await message.reply('Вы успешно подписались.')
                    await asyncio.to_thread(spam_every_n_hours, message.peer_id, n)
    else:
        await message.reply('Неверное число.')


@bot.on.message(text='/отписаться')
async def unsubscribe(message: Message):
    global db

    async with aiofiles.open('DB.txt', 'r', encoding='UTF-8') as temp:
        db = await temp.read()
    db = literal_eval(db)

    if message.peer_id not in db.keys():
        await message.reply('Ошибка. Сначала добавьте группу с помощью команды:\n \
                    /группа <название>\n\nПример: /группа пкст-20-(9)-2')
    else:
        if db.get(message.peer_id).get('subscribed') is None:
            await message.reply('Вы не подписаны на рассылку.')
        else:
            for key in list(db[message.peer_id].keys()):
                if key not in ('group', 'URL'):
                    del db[message.peer_id][key]

            async with aiofiles.open('DB.txt', 'w', encoding='UTF-8') as temp:
                await temp.write(str(db))

            await message.reply('Вы успешно отписались от рассылки.')


@bot.on.raw_event(GroupEventType.MESSAGE_NEW, GroupTypes.MessageNew)
async def global_handling(event: GroupTypes.MessageNew):
    if event.object.message.payload:
        payload = literal_eval(event.object.message.payload)
        command = payload['command']

        match command:
            case 'every_n_hours':
                await bot.api.messages.send(random_id=get_random_id(),
                                            peer_id=event.object.message.peer_id,
                                            message='Пожалуйста, отправьте команду \
                                                /рассылка <число>\n\nПример: /рассылка 5 \
                                                    \nЗначит, рассылка каждые 5 часов.')
            case 'n_times':
                await bot.api.messages.send(random_id=get_random_id(),
                                            peer_id=event.object.message.peer_id,
                                            message='Выберите вариант рассылки.',
                                            keyboard=AmountVariantsKeyboard)
            case 'two_times':
                db[event.object.message.peer_id]['method'] = 'n_times_a_day'
                db[event.object.message.peer_id]['amount'] = 2
                db[event.object.message.peer_id]['subscribed'] = True

                async with aiofiles.open('DB.txt', 'w', encoding='UTF-8') as temp:
                    await temp.write(str(db))

                await bot.api.messages.send(random_id=get_random_id(),
                                            peer_id=event.object.message.peer_id,
                                            message='Вы успешно подписались.\nРасписание будет \
                                                отправляться два раза в день: в 06:00 утра и \
                                                    19:00 вечера.')
                await asyncio.to_thread(spam_n_times_a_day,
                                        event.object.message.peer_id,
                                        db.get(event.object.message.peer_id).get('amount'))
            case 'three_times':
                db[event.object.message.peer_id]['method'] = 'n_times_a_day'
                db[event.object.message.peer_id]['amount'] = 3
                db[event.object.message.peer_id]['subscribed'] = True

                async with aiofiles.open('DB.txt', 'w', encoding='UTF-8') as temp:
                    await temp.write(str(db))

                await bot.api.messages.send(random_id=get_random_id(),
                                            peer_id=event.object.message.peer_id,
                                            message='Вы успешно подписались.\nРасписание будет \
                                                отправляться три раза в день: в 06:00 утра, \
                                                    12:00 дня, и 18:00 вечера.')
                await asyncio.to_thread(spam_n_times_a_day,
                                        event.object.message.peer_id,
                                        db.get(event.object.message.peer_id).get('amount'))
            case 'four_times':
                db[event.object.message.peer_id]['method'] = 'n_times_a_day'
                db[event.object.message.peer_id]['amount'] = 4
                db[event.object.message.peer_id]['subscribed'] = True

                async with aiofiles.open('DB.txt', 'w', encoding='UTF-8') as temp:
                    await temp.write(str(db))

                await bot.api.messages.send(random_id=get_random_id(),
                                            peer_id=event.object.message.peer_id,
                                            message='Вы успешно подписались.\nРасписание будет \
                                                отправляться четыре раза в день: в 06:00 утра, \
                                                    12:00 дня, 16:00 и 20:00 вечера.')
                await asyncio.to_thread(spam_n_times_a_day,
                                        event.object.message.peer_id,
                                        db.get(event.object.message.peer_id).get('amount'))
            case 'five_times':
                db[event.object.message.peer_id]['method'] = 'n_times_a_day'
                db[event.object.message.peer_id]['amount'] = 5
                db[event.object.message.peer_id]['subscribed'] = True

                async with aiofiles.open('DB.txt', 'w', encoding='UTF-8') as temp:
                    await temp.write(str(db))

                await bot.api.messages.send(random_id=get_random_id(),
                                            peer_id=event.object.message.peer_id,
                                            message='Вы успешно подписались.\nРасписание будет отправляться \
                                                пять раз в день: в 06:00 утра, 12:00 дня и 15:00 \
                                                    дня, 18:00 вечера и 21:00 вечера.')
                await asyncio.to_thread(spam_n_times_a_day,
                                        event.object.message.peer_id,
                                        db.get(event.object.message.peer_id).get('amount'))
            case 'on_change':
                db[event.object.message.peer_id]['method'] = 'on_change'
                db[event.object.message.peer_id]['subscribed'] = True

                async with aiofiles.open('DB.txt', 'w', encoding='UTF-8') as temp:
                    await temp.write(str(db))

                await bot.api.messages.send(random_id=get_random_id(),
                                            peer_id=event.object.message.peer_id,
                                            message='Вы успешно подписались.\nТеперь вам будет \
                                            отправлено новое расписание при любом его изменении.')

                await asyncio.to_thread(spam_on_change, event.object.message.peer_id)
            case 'get_schedule':
                if user := db.get(event.object.message.peer_id) is None:
                    await bot.api.messages.send(random_id=get_random_id(),
                                                peer_id=event.object.message.peer_id,
                                                message='Ошибка. Сначала добавьте группу с помощью команды: \
                                            \n/группа <название>\n\nПример: /группа пкст-20-(9)-2')
                else:
                    if user := db.get(event.object.message.peer_id):
                        uploaded_screenshot = await make_screenshot(user.get('URL'),
                                                                    user.get('group'))
                        await bot.api.messages.send(random_id=get_random_id(),
                                                    peer_id=event.object.message.peer_id,
                                                    attachment=uploaded_screenshot,
                                                    keyboard=GetScheduleKeyboard)


@bot.on.chat_message(rules.ChatActionRule("chat_invite_user"))
async def bot_joined(message: Message):
    if message.action.member_id == -group_id:
        await bot.api.messages.send(random_id=get_random_id(),
                                    peer_id=message.peer_id,
                                    message=start_message)

        screenshot = await PhotoMessageUploader(bot.api).upload('additional/media/give_rights.png')

        await asyncio.sleep(5)
        await bot.api.messages.send(random_id=get_random_id(),
                                    peer_id=message.peer_id,
                                    attachment=screenshot,
                                    message=on_invite_message)

        await bot.api.messages.send(random_id=get_random_id(),
                                    user_id=admin_user_id,
                                    message=f'Бот был добавлен в беседу {message}')


async def load_tasks_from_db():
    global tasks

    db_peer_ids_keys = list(db.keys())

    for key in db_peer_ids_keys:
        user = db.get(key)
        method = user.get('method')

        match method:
            case 'every_n_hours':
                peer_id = key
                hours = user.get('hours')
                tasks.append(asyncio.create_task(asyncio.to_thread(spam_every_n_hours,
                                                                   peer_id,
                                                                   hours)))
            case 'n_times_a_day':
                peer_id = key
                amount = user.get('amount')
                tasks.append(asyncio.create_task(asyncio.to_thread(spam_n_times_a_day,
                                                                   peer_id,
                                                                   amount)))
            case 'on_change':
                peer_id = key
                tasks.append(asyncio.create_task(asyncio.to_thread(spam_on_change,
                                                                   peer_id)))


async def main():
    global db
    global pyppeteer_browser
    global tasks

    try:
        pyppeteer_browser = await launch(args=pyppeteer_args)

        for bp in load_blueprints_from_package('blueprints'):
            bp.load(bot)

        async with aiofiles.open('DB.txt', 'r', encoding='UTF-8') as temp:
            db = await temp.read()

        db = literal_eval(db)

        tasks.append(asyncio.create_task(load_tasks_from_db()))
        tasks.append(asyncio.create_task(bot.run_polling()))

        await asyncio.gather(*tasks)
    finally:
        await pyppeteer_browser.close()


if __name__ == '__main__':
    asyncio.run(main())
