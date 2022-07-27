import additional.chrome_options as chrome_options
import additional.keyboards as keyboards
import additional.message_templates as msg_templates
import config

from ast import literal_eval
from bs4 import BeautifulSoup
from datetime import datetime
from loguru import logger
from pyppeteer import launch
from pytz import timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from threading import Thread
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
    '<green>{time}</green> | '
    '<level>{level: <8}</level> | '
    '<cyan>{name}</cyan>:<cyan>{function}</cyan>'
    '<level>{message}</level>'
)
logger.add(sys.stderr, format=logger_format, level='INFO')


bot = Bot(token=config.token)
bot.labeler.vbml_ignore_case = True


vk_session = VkApi(token=config.token)
vk = vk_session.get_api()


@logger.catch
async def get_group(raw_group: str):
    try:
        page = await pyppeteer_browser.newPage()
        await page.goto(config.schedule_menu_url)
        html = await page.content()

        soup = BeautifulSoup(html, 'lxml')
        zero_group = soup.find('option').find_next()
        all_groups = zero_group.find_next_siblings()

        group = re.findall(pattern=re.escape(raw_group),
                           string=str(all_groups),
                           flags=re.IGNORECASE)
        if not group:
            return
        else:
            group = group[0]
            group_tag = soup.find('option', string=group)
            attributes_dict = group_tag.attrs

            sid = attributes_dict.get('sid')
            gr = attributes_dict.get('value')

            if any((sid, gr)) is None:
                return
            else:
                schedule_url = config.api_link.format(group=group,
                                                      sid=sid,
                                                      gr=gr)
                return {'URL': schedule_url,
                        'group': group}
    finally:
        await page.close()


@logger.catch
async def make_screenshot(URL: str, group: str):
    local_screenshot_options = chrome_options.pyppeteer_screenshot_options

    group_filename = group.strip('()') + '.png'
    local_screenshot_options.update(path=group_filename)
    try:
        page = await pyppeteer_browser.newPage()
        await page.goto(URL, options=chrome_options.pyppeteer_goto_options)
        await page.screenshot(options=local_screenshot_options)
        return await PhotoMessageUploader(bot.api).upload(group_filename)
    finally:
        await page.close()


@logger.catch
def sync_get_group(raw_group: str):
    with webdriver.Chrome(options=chrome_options.selenium_args) as browser:
        browser.get(config.schedule_menu_url)
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

        schedule_url = config.api_link.format(group=group,
                                              sid=sid,
                                              gr=gr)
        return {'URL': schedule_url,
                'group': group}


@logger.catch
def sync_make_screenshot(URL: str, group: str):
    group_filename = group.strip('()') + '.png'
    with webdriver.Chrome(options=chrome_options.selenium_args) as browser:
        S = lambda x: browser.execute_script('return document.body.parentNode.scroll' + x) # noqa

        browser.get(URL)
        browser.set_window_size(S('Width'), S('Height'))
        browser.maximize_window()
        browser.find_element(By.TAG_NAME, 'html').screenshot(group_filename)

        upload = VkUpload(vk)
        photo_obj = upload.photo_messages(group_filename)[0]

        return 'photo{owner_id}_{id}_{access_key}'.format(**photo_obj)


@logger.catch
def send_schedule_every_n_hours(peer_id: int, hours: int):
    logger.success(f'Send schedule every {hours} hours for {peer_id} was started')

    while db.get(peer_id).get('subscribed'):
        group_and_url = sync_get_group(db.get(peer_id).get('group'))
        uploaded_screenshot = sync_make_screenshot(group_and_url.get('URL'),
                                                   group_and_url.get('group'))

        requests.get(config.message_send_url.format(token=config.token,
                                                    peer_id=peer_id,
                                                    attachment=uploaded_screenshot,
                                                    random_id=get_random_id()))
        time.sleep(hours * 3600)


@logger.catch
def send_schedule_n_times_a_day(peer_id: int, amount: int):
    logger.success(f'Send schedule {amount} times for {peer_id} was started')

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
                time_now = datetime.now(time_zone).strftime('%H:%M')
                if time_now in two_times_range:
                    group_and_url = sync_get_group(db.get(peer_id).get('group'))
                    uploaded_screenshot = sync_make_screenshot(group_and_url.get('URL'),
                                                               group_and_url.get('group'))
                    requests.get(config.message_send_url.format(token=config.token,
                                                                peer_id=peer_id,
                                                                attachment=uploaded_screenshot,
                                                                random_id=get_random_id())
                                 + f'&message={time_now}')
                    time.sleep(18000)

                time.sleep(15)
        case 3:
            while db.get(peer_id).get('subscribed'):
                time_now = datetime.now(time_zone).strftime('%H:%M')
                if time_now in three_times_range:
                    group_and_url = sync_get_group(db.get(peer_id).get('group'))
                    uploaded_screenshot = sync_make_screenshot(group_and_url.get('URL'),
                                                               group_and_url.get('group'))
                    requests.get(config.message_send_url.format(token=config.token,
                                                                peer_id=peer_id,
                                                                attachment=uploaded_screenshot,
                                                                random_id=get_random_id())
                                 + f'&message={time_now}')
                    time.sleep(14000)

                time.sleep(15)
        case 4:
            while db.get(peer_id).get('subscribed'):
                time_now = datetime.now(time_zone).strftime('%H:%M')
                if time_now in four_times_range:
                    group_and_url = sync_get_group(db.get(peer_id).get('group'))
                    uploaded_screenshot = sync_make_screenshot(group_and_url.get('URL'),
                                                               group_and_url.get('group'))
                    requests.get(config.message_send_url.format(token=config.token,
                                                                peer_id=peer_id,
                                                                attachment=uploaded_screenshot,
                                                                random_id=get_random_id())
                                 + f'&message={time_now}')
                    time.sleep(10000)

                time.sleep(15)
        case 5:
            while db.get(peer_id).get('subscribed'):
                time_now = datetime.now(time_zone).strftime('%H:%M')
                if time_now in five_times_range:
                    group_and_url = sync_get_group(db.get(peer_id).get('group'))
                    uploaded_screenshot = sync_make_screenshot(group_and_url.get('URL'),
                                                               group_and_url.get('group'))
                    requests.get(config.message_send_url.format(token=config.token,
                                                                peer_id=peer_id,
                                                                attachment=uploaded_screenshot,
                                                                random_id=get_random_id())
                                 + f'&message={time_now}')
                    time.sleep(7000)

                time.sleep(15)


@logger.catch
def send_schedule_on_change(peer_id: int):
    logger.success(f'Send schedule on change for {peer_id} was started')

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
            requests.get(config.message_send_url.format(token=config.token,
                                                        peer_id=peer_id,
                                                        attachment=uploaded_screenshot,
                                                        random_id=get_random_id())
                         + '&message=Изменение в расписании')
            time.sleep(1000)
        else:
            time.sleep(1000)


@bot.on.chat_message(text='/группа <raw_group>')
async def set_group_public(message: Message, raw_group: str):
    global db

    if len(raw_group) not in range(10, 17):
        await message.reply(msg_templates.group_not_found_message)

    group_and_url = await get_group(raw_group)
    if not isinstance(group_and_url, dict):
        await message.reply(msg_templates.group_not_found_message)
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

        await message.reply(msg_templates.set_group_chat_success.format(group=group))

        await message.answer(msg_templates.set_group_success2,
                             keyboard=keyboards.GetScheduleKeyboard)


@bot.on.private_message(text='/группа <raw_group>')
async def set_group_private(message: Message, raw_group):
    global db

    if len(raw_group) not in range(10, 17):
        await message.reply(msg_templates.group_not_found_message)

    group_and_url = await get_group(raw_group)
    if not isinstance(group_and_url, dict):
        await message.reply(msg_templates.group_not_found_message)
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

        await message.reply(msg_templates.set_group_private_success.format(user_id=message.peer_id,
                                                                           group=group))
        await message.answer(msg_templates.set_group_success2,
                             keyboard=keyboards.GetScheduleKeyboard)


@bot.on.message(text='/расписание')
async def show_schedule(message: Message):
    if user := db.get(message.peer_id) is None:
        await message.reply(msg_templates.group_not_set_message)
    else:
        if user := db.get(message.peer_id):
            uploaded_screenshot = await make_screenshot(user.get('URL'),
                                                        user.get('group'))
            await message.answer(attachment=uploaded_screenshot,
                                 keyboard=keyboards.GetScheduleKeyboard)


@bot.on.message(text='/подписка')
async def subscription_types(message: Message):
    if message.peer_id in db.keys():
        if not db.get(message.peer_id).get('subscribed'):
            await message.reply(msg_templates.choose_subscription_message,
                                keyboard=keyboards.SpamVariantsKeyboard)
        else:
            await message.reply(msg_templates.already_subscribed_message)
    else:
        await message.reply(msg_templates.group_not_set_message)


@bot.on.message(text='/рассылка <digit>')
async def subscribe_to_first_method(message: Message, digit: str):
    global db

    if digit.isdigit():
        n = int(digit)

        if not 100 > n > 0:
            await message.reply(msg_templates.incorrect_number_range)
        else:
            if message.peer_id not in db.keys():
                await message.reply(msg_templates.group_not_set_message)
            else:
                if db.get(message.peer_id).get('subscribed'):
                    await message.reply(msg_templates.already_subscribed_message)
                else:
                    db[message.peer_id]['method'] = 'every_n_hours'
                    db[message.peer_id]['hours'] = n
                    db[message.peer_id]['subscribed'] = True

                    async with aiofiles.open('DB.txt', 'w', encoding='UTF-8') as temp:
                        await temp.write(str(db))

                    await message.reply(msg_templates.subscription_successful)
                    Thread(target=send_schedule_every_n_hours,
                           args=(message.peer_id, n),
                           daemon=True).start()
    else:
        await message.reply(msg_templates.incorrect_number)


@bot.on.message(text='/отписаться')
async def unsubscribe(message: Message):
    global db

    async with aiofiles.open('DB.txt', 'r', encoding='UTF-8') as temp:
        db = await temp.read()
    db = literal_eval(db)

    if message.peer_id not in db.keys():
        await message.reply(msg_templates.group_not_set_message)
    else:
        if db.get(message.peer_id).get('subscribed') is None:
            await message.reply(msg_templates.not_subscribed_error)
        else:
            for key in list(db[message.peer_id].keys()):
                if key not in ('group', 'URL'):
                    del db[message.peer_id][key]

            async with aiofiles.open('DB.txt', 'w', encoding='UTF-8') as temp:
                await temp.write(str(db))

            await message.reply(msg_templates.unsubscription_successful)


@bot.on.raw_event(GroupEventType.MESSAGE_NEW, GroupTypes.MessageNew)
async def global_handling(event: GroupTypes.MessageNew):
    if payload := event.object.message.payload:
        payload = literal_eval(payload)
        command = payload['command']

        peer_id = event.object.message.peer_id

        match command:
            case 'every_n_hours':
                await bot.api.messages.send(random_id=get_random_id(),
                                            peer_id=peer_id,
                                            message=msg_templates.every_n_hours_method_template,
                                            keyboard=keyboards.GetScheduleKeyboard)
            case 'n_times':
                await bot.api.messages.send(random_id=get_random_id(),
                                            peer_id=peer_id,
                                            message=msg_templates.choose_subscription_message,
                                            keyboard=keyboards.AmountVariantsKeyboard)
            case 'two_times':
                db[peer_id]['method'] = 'n_times_a_day'
                db[peer_id]['amount'] = 2
                db[peer_id]['subscribed'] = True

                async with aiofiles.open('DB.txt', 'w', encoding='UTF-8') as temp:
                    await temp.write(str(db))

                await bot.api.messages.send(random_id=get_random_id(),
                                            peer_id=peer_id,
                                            message=msg_templates.subscribed_to_2_times,
                                            keyboard=keyboards.GetScheduleKeyboard)
                Thread(target=send_schedule_n_times_a_day,
                       args=(peer_id, db.get(peer_id).get('amount')),
                       daemon=True).start()
            case 'three_times':
                db[peer_id]['method'] = 'n_times_a_day'
                db[peer_id]['amount'] = 3
                db[peer_id]['subscribed'] = True

                async with aiofiles.open('DB.txt', 'w', encoding='UTF-8') as temp:
                    await temp.write(str(db))

                await bot.api.messages.send(random_id=get_random_id(),
                                            peer_id=peer_id,
                                            message=msg_templates.subscribed_to_3_times,
                                            keyboard=keyboards.GetScheduleKeyboard)
                Thread(target=send_schedule_n_times_a_day,
                       args=(peer_id, db.get(peer_id).get('amount')),
                       daemon=True).start()
            case 'four_times':
                db[peer_id]['method'] = 'n_times_a_day'
                db[peer_id]['amount'] = 4
                db[peer_id]['subscribed'] = True

                async with aiofiles.open('DB.txt', 'w', encoding='UTF-8') as temp:
                    await temp.write(str(db))

                await bot.api.messages.send(random_id=get_random_id(),
                                            peer_id=peer_id,
                                            message=msg_templates.subscribed_to_4_times,
                                            keyboard=keyboards.GetScheduleKeyboard)
                Thread(target=send_schedule_n_times_a_day,
                       args=(peer_id, db.get(peer_id).get('amount')),
                       daemon=True).start()
            case 'five_times':
                db[peer_id]['method'] = 'n_times_a_day'
                db[peer_id]['amount'] = 5
                db[peer_id]['subscribed'] = True

                async with aiofiles.open('DB.txt', 'w', encoding='UTF-8') as temp:
                    await temp.write(str(db))

                await bot.api.messages.send(random_id=get_random_id(),
                                            peer_id=peer_id,
                                            message=msg_templates.subscribed_to_5_times,
                                            keyboard=keyboards.GetScheduleKeyboard)
                Thread(target=send_schedule_n_times_a_day,
                       args=(peer_id, db.get(peer_id).get('amount')),
                       daemon=True).start()
            case 'on_change':
                db[peer_id]['method'] = 'on_change'
                db[peer_id]['subscribed'] = True

                async with aiofiles.open('DB.txt', 'w', encoding='UTF-8') as temp:
                    await temp.write(str(db))

                await bot.api.messages.send(random_id=get_random_id(),
                                            peer_id=peer_id,
                                            message=msg_templates.on_change_method_subscribed,
                                            keyboard=keyboards.GetScheduleKeyboard)

                Thread(target=send_schedule_on_change,
                       args=[peer_id],
                       daemon=True).start()
            case 'get_schedule':
                if user := db.get(peer_id) is None:
                    await bot.api.messages.send(random_id=get_random_id(),
                                                peer_id=peer_id,
                                                message=msg_templates.group_not_set_message)
                else:
                    if user := db.get(peer_id):
                        uploaded_screenshot = await make_screenshot(user.get('URL'),
                                                                    user.get('group'))
                        await bot.api.messages.send(random_id=get_random_id(),
                                                    peer_id=peer_id,
                                                    attachment=uploaded_screenshot,
                                                    keyboard=keyboards.GetScheduleKeyboard)


@bot.on.chat_message(rules.ChatActionRule("chat_invite_user"))
async def bot_joined(message: Message):
    if message.action.member_id == -config.group_id:
        await bot.api.messages.send(random_id=get_random_id(),
                                    peer_id=message.peer_id,
                                    message=msg_templates.start_message)

        screenshot = await PhotoMessageUploader(bot.api).upload('additional/media/give_rights.png')

        await asyncio.sleep(5)
        await bot.api.messages.send(random_id=get_random_id(),
                                    peer_id=message.peer_id,
                                    attachment=screenshot,
                                    message=msg_templates.on_invite_message)

        await bot.api.messages.send(random_id=get_random_id(),
                                    user_id=config.admin_user_id,
                                    message=msg_templates.bot_was_added_admin_log.format(message))


async def load_tasks_from_db():
    db_peer_ids_keys = list(db.keys())

    for key in db_peer_ids_keys:
        user = db.get(key)
        method = user.get('method')

        match method:
            case 'every_n_hours':
                peer_id = key
                hours = user.get('hours')
                Thread(target=send_schedule_every_n_hours,
                       args=(peer_id, hours),
                       daemon=True).start()

            case 'n_times_a_day':
                peer_id = key
                amount = user.get('amount')
                Thread(target=send_schedule_n_times_a_day,
                       args=(peer_id, amount),
                       daemon=True).start()

            case 'on_change':
                peer_id = key
                Thread(target=send_schedule_on_change,
                       args=[peer_id],
                       daemon=True).start()


async def main():
    global db
    global pyppeteer_browser

    try:
        pyppeteer_browser = await launch(options=chrome_options.pyppeteer_options)

        for bp in load_blueprints_from_package('blueprints'):
            bp.load(bot)

        async with aiofiles.open('DB.txt', 'r', encoding='UTF-8') as temp:
            db = await temp.read()
        db = literal_eval(db)

        await load_tasks_from_db()

        await bot.run_polling()
    finally:
        await pyppeteer_browser.close()


if __name__ == '__main__':
    asyncio.run(main())
