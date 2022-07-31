import additional.chrome_options as chrome_options
import additional.keyboards as keyboards
import additional.message_templates as msg_templates
from blueprints import bps
from config import token, api_link, group_id, admin_user_id, schedule_menu_url

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from ast import literal_eval
from bs4 import BeautifulSoup
from datetime import datetime
from loguru import logger
from pyppeteer import launch
from pytz import timezone
from vkbottle import GroupEventType, GroupTypes, VKAPIError
from vkbottle.bot import Bot, Message, rules
from vkbottle.tools import PhotoMessageUploader
import aiofiles
import aiohttp
import asyncio
import re
import sys


logger.remove()
logger.add('logs.log', format='{time} {level} {message}', level='DEBUG')
logger_format = (
    '<level>{level: <8}</level>| '
    '<cyan>{name}</cyan>:<cyan>{function}</cyan> | '
    '<level>{message}</level>'
)
logger.add(sys.stderr, format=logger_format, level='INFO')


bot = Bot(token=token)
bot.labeler.vbml_ignore_case = True


scheduler = AsyncIOScheduler()


@logger.catch
async def get_group(raw_group: str):
    group = re.findall(pattern=re.escape(raw_group),
                       string=all_groups,
                       flags=re.IGNORECASE)
    if not group or len(group) > 1:
        return

    group = group[0]
    group_tag = soup.find('option', string=group)
    attributes_dict = group_tag.attrs

    sid = attributes_dict.get('sid')
    gr = attributes_dict.get('value')

    if not any((sid, gr)):
        return

    schedule_url = api_link.format(group=group,
                                   sid=sid,
                                   gr=gr)
    return {'URL': schedule_url,
            'group': group}


@logger.catch
async def take_screenshot(URL: str, group: str):
    local_screenshot_options = chrome_options.pyppeteer_screenshot_options
    group_filename = f'{group}.png'
    local_screenshot_options.update(path=f'./temp/{group_filename}')
    try:
        page = await browser.newPage()
        await page.goto(URL, options=chrome_options.pyppeteer_goto_options)
        await page.screenshot(options=local_screenshot_options)
        return await PhotoMessageUploader(bot.api).upload(f'./temp/{group_filename}')
    finally:
        await page.close()


@logger.catch
async def send_schedule_every_n_hours(peer_id: int, hours: int):
    logger.success(f'Send schedule every {hours} hours for {peer_id} was started')

    user_subscribed = db.get(peer_id).get('subscribed')

    while user_subscribed:
        URL = db.get(peer_id).get('URL')
        group = db.get(peer_id).get('group')
        uploaded_screenshot = await take_screenshot(URL, group)

        await bot.api.messages.send(random_id=0,
                                    peer_id=peer_id,
                                    attachment=uploaded_screenshot)

        await asyncio.sleep(hours * 3600)

    logger.info(f'{peer_id} unsubscribed')


@logger.catch
async def send_schedule_n_times_a_day(peer_id: int, amount: int):
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
            user_subscribed = db.get(peer_id).get('subscribed')
            while user_subscribed:
                time_now = datetime.now(time_zone).strftime('%H:%M')
                if time_now in two_times_range:
                    URL = db.get(peer_id).get('URL')
                    group = db.get(peer_id).get('group')
                    uploaded_screenshot = await take_screenshot(URL, group)

                    await bot.api.messages.send(random_id=0,
                                                peer_id=peer_id,
                                                attachment=uploaded_screenshot,
                                                message=time_now)
                    await asyncio.sleep(45900)

                await asyncio.sleep(15)

            logger.info(f'{peer_id} unsubscribed')
        case 3:
            user_subscribed = db.get(peer_id).get('subscribed')
            while user_subscribed:
                time_now = datetime.now(time_zone).strftime('%H:%M')
                if time_now in three_times_range:
                    URL = db.get(peer_id).get('URL')
                    group = db.get(peer_id).get('group')
                    uploaded_screenshot = await take_screenshot(URL, group)

                    await bot.api.messages.send(random_id=0,
                                                peer_id=peer_id,
                                                attachment=uploaded_screenshot,
                                                message=time_now)
                    await asyncio.sleep(20700)

                await asyncio.sleep(15)

            logger.info(f'{peer_id} unsubscribed')
        case 4:
            user_subscribed = db.get(peer_id).get('subscribed')
            while user_subscribed:
                time_now = datetime.now(time_zone).strftime('%H:%M')
                if time_now in four_times_range:
                    URL = db.get(peer_id).get('URL')
                    group = db.get(peer_id).get('group')
                    uploaded_screenshot = await take_screenshot(URL, group)

                    await bot.api.messages.send(random_id=0,
                                                peer_id=peer_id,
                                                attachment=uploaded_screenshot,
                                                message=time_now)
                    await asyncio.sleep(13500)

                await asyncio.sleep(15)

            logger.info(f'{peer_id} unsubscribed')
        case 5:
            user_subscribed = db.get(peer_id).get('subscribed')
            while user_subscribed:
                time_now = datetime.now(time_zone).strftime('%H:%M')
                if time_now in five_times_range:
                    URL = db.get(peer_id).get('URL')
                    group = db.get(peer_id).get('group')
                    uploaded_screenshot = await take_screenshot(URL, group)

                    await bot.api.messages.send(random_id=0,
                                                peer_id=peer_id,
                                                attachment=uploaded_screenshot,
                                                message=time_now)
                    await asyncio.sleep(9900)

                await asyncio.sleep(15)

            logger.info(f'{peer_id} unsubscribed')


@logger.catch
async def send_schedule_on_change(peer_id: int):
    logger.success(f'Send schedule on change for {peer_id} was started')

    URL = db.get(peer_id).get('URL')
    group = db.get(peer_id).get('group')

    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as response:
            html = await response.text()

    first_html = r''.join(html)
    user_subscribed = db.get(peer_id).get('subscribed')

    while user_subscribed:
        async with aiohttp.ClientSession() as session:
            async with session.get(URL) as response:
                html = await response.text()

        new_html = r''.join(html)

        if first_html != new_html:
            first_html = new_html

            uploaded_screenshot = await take_screenshot(URL, group)
            await bot.api.messages.send(random_id=0,
                                        peer_id=peer_id,
                                        attachment=uploaded_screenshot,
                                        message='Изменение в расписании')
            await asyncio.sleep(1000)
        else:
            await asyncio.sleep(1000)

    logger.info(f'{peer_id} unsubscribed')


@bot.on.chat_message(text='/группа <raw_group>')
async def set_group_public(message: Message, raw_group: str):
    global db

    if len(raw_group) not in range(10, 17):
        await message.reply(msg_templates.group_not_found_message)
        return

    group_and_url = await get_group(raw_group)

    if not isinstance(group_and_url, dict):
        await message.reply(msg_templates.group_not_found_message)
        return

    group = group_and_url.get('group')
    URL = group_and_url.get('URL')

    if message.peer_id in db.keys():
        db[message.peer_id].update(group=group,
                                   URL=URL)
    else:
        db[message.peer_id] = {'group': group,
                               'URL': URL}

    async with aiofiles.open('DB.txt', 'w', encoding='UTF-8') as temp:
        await temp.write(str(db))

    await message.reply(msg_templates.set_group_chat_success.format(group=group))

    await message.answer(msg_templates.set_group_success2,
                         keyboard=keyboards.GetScheduleKeyboard)


@bot.on.private_message(text='/группа <raw_group>')
async def set_group_private(message: Message, raw_group: str):
    global db

    if len(raw_group) not in range(10, 17):
        await message.reply(msg_templates.group_not_found_message)
        return

    group_and_url = await get_group(raw_group)

    if not isinstance(group_and_url, dict):
        await message.reply(msg_templates.group_not_found_message)
        return

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
            uploaded_screenshot = await take_screenshot(user.get('URL'),
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

                    await message.reply(msg_templates.subscription_successful,
                                        keyboard=keyboards.GetScheduleKeyboard)
                scheduler.add_job(send_schedule_every_n_hours,
                                  args=(message.peer_id, n))
    else:
        await message.reply(msg_templates.incorrect_number)


@bot.on.message(text='/отписаться')
async def unsubscribe(message: Message):
    global db

    if message.peer_id not in db.keys():
        await message.reply(msg_templates.group_not_set_message)
    else:
        if db.get(message.peer_id).get('subscribed') is None:
            await message.reply(msg_templates.not_subscribed_error)
        else:
            async with aiofiles.open('DB.txt', 'r', encoding='UTF-8') as temp:
                db = await temp.read()
            db = literal_eval(db)

            for key in list(db[message.peer_id].keys()):
                if key not in ('group', 'URL'):
                    del db[message.peer_id][key]

            async with aiofiles.open('DB.txt', 'w', encoding='UTF-8') as temp:
                await temp.write(str(db))

            await message.reply(msg_templates.unsubscription_successful,
                                keyboard=keyboards.GetScheduleKeyboard)


@bot.on.raw_event(GroupEventType.MESSAGE_NEW, GroupTypes.MessageNew)
async def global_handling(event: GroupTypes.MessageNew):
    if payload := event.object.message.payload:
        payload = literal_eval(payload)
        command = payload['command']

        peer_id = event.object.message.peer_id

        match command:
            case 'every_n_hours':
                await bot.api.messages.send(random_id=0,
                                            peer_id=peer_id,
                                            message=msg_templates.every_n_hours_method_template,
                                            keyboard=keyboards.GetScheduleKeyboard)
            case 'n_times':
                await bot.api.messages.send(random_id=0,
                                            peer_id=peer_id,
                                            message=msg_templates.choose_subscription_message,
                                            keyboard=keyboards.AmountVariantsKeyboard)
            case 'two_times':
                db[peer_id]['method'] = 'n_times_a_day'
                db[peer_id]['amount'] = 2
                db[peer_id]['subscribed'] = True

                amount = db.get(peer_id).get('amount')

                async with aiofiles.open('DB.txt', 'w', encoding='UTF-8') as temp:
                    await temp.write(str(db))

                await bot.api.messages.send(random_id=0,
                                            peer_id=peer_id,
                                            message=msg_templates.subscribed_to_2_times,
                                            keyboard=keyboards.GetScheduleKeyboard)
                scheduler.add_job(send_schedule_n_times_a_day,
                                  args=(peer_id, amount))
            case 'three_times':
                db[peer_id]['method'] = 'n_times_a_day'
                db[peer_id]['amount'] = 3
                db[peer_id]['subscribed'] = True

                amount = db.get(peer_id).get('amount')

                async with aiofiles.open('DB.txt', 'w', encoding='UTF-8') as temp:
                    await temp.write(str(db))

                await bot.api.messages.send(random_id=0,
                                            peer_id=peer_id,
                                            message=msg_templates.subscribed_to_3_times,
                                            keyboard=keyboards.GetScheduleKeyboard)
                scheduler.add_job(send_schedule_n_times_a_day,
                                  args=(peer_id, amount))
            case 'four_times':
                db[peer_id]['method'] = 'n_times_a_day'
                db[peer_id]['amount'] = 4
                db[peer_id]['subscribed'] = True

                amount = db.get(peer_id).get('amount')

                async with aiofiles.open('DB.txt', 'w', encoding='UTF-8') as temp:
                    await temp.write(str(db))

                await bot.api.messages.send(random_id=0,
                                            peer_id=peer_id,
                                            message=msg_templates.subscribed_to_4_times,
                                            keyboard=keyboards.GetScheduleKeyboard)
                scheduler.add_job(send_schedule_n_times_a_day,
                                  args=(peer_id, amount))
            case 'five_times':
                db[peer_id]['method'] = 'n_times_a_day'
                db[peer_id]['amount'] = 5
                db[peer_id]['subscribed'] = True

                amount = db.get(peer_id).get('amount')

                async with aiofiles.open('DB.txt', 'w', encoding='UTF-8') as temp:
                    await temp.write(str(db))

                await bot.api.messages.send(random_id=0,
                                            peer_id=peer_id,
                                            message=msg_templates.subscribed_to_5_times,
                                            keyboard=keyboards.GetScheduleKeyboard)
                scheduler.add_job(send_schedule_n_times_a_day,
                                  args=(peer_id, amount))
            case 'on_change':
                db[peer_id]['method'] = 'on_change'
                db[peer_id]['subscribed'] = True

                async with aiofiles.open('DB.txt', 'w', encoding='UTF-8') as temp:
                    await temp.write(str(db))

                await bot.api.messages.send(random_id=0,
                                            peer_id=peer_id,
                                            message=msg_templates.on_change_method_subscribed,
                                            keyboard=keyboards.GetScheduleKeyboard)

                scheduler.add_job(send_schedule_on_change,
                                  args=[peer_id])
            case 'get_schedule':
                user = db.get(peer_id)

                uploaded_screenshot = await take_screenshot(user.get('URL'),
                                                            user.get('group'))
                await bot.api.messages.send(random_id=0,
                                            peer_id=peer_id,
                                            attachment=uploaded_screenshot,
                                            keyboard=keyboards.GetScheduleKeyboard)


@bot.on.chat_message(rules.ChatActionRule("chat_invite_user"))
async def bot_joined(message: Message):
    if message.action.member_id and abs(message.action.member_id) == abs(group_id):
        await bot.api.messages.send(random_id=0,
                                    peer_id=message.peer_id,
                                    message=msg_templates.start_message)

        screenshot = await PhotoMessageUploader(bot.api).upload('additional/media/give_rights.png')
        await asyncio.sleep(5)
        await bot.api.messages.send(random_id=0,
                                    peer_id=message.peer_id,
                                    attachment=screenshot,
                                    message=msg_templates.on_invite_message)

        await bot.api.messages.send(random_id=0,
                                    user_id=admin_user_id,
                                    message=msg_templates.bot_was_added_admin_log.format(message))


async def run_chrome_on_startup():
    global browser

    browser = await launch(options=chrome_options.pyppeteer_options)
    logger.success('Chrome was started')


@scheduler.scheduled_job('interval', days=1)
async def parse_groups_tags():
    global soup
    global all_groups

    try:
        page = await browser.newPage()
        await page.goto(schedule_menu_url, options=chrome_options.pyppeteer_goto_options)
        await asyncio.sleep(10)
        html = await page.content()

        soup = BeautifulSoup(html, 'lxml')
        zero_group = soup.find('option').find_next()
        all_groups = str(zero_group.find_next_siblings())

        logger.success('Groups was parsed')
    finally:
        await page.close()


@scheduler.scheduled_job('interval', hours=4)
async def set_group_status_online():
    try:
        await bot.api.groups.enable_online(group_id)
        logger.success('Group is online now')
    except VKAPIError:
        logger.info('Online is already enabled')


async def load_tasks_from_db_on_startup():
    global db

    async with aiofiles.open('DB.txt', 'r', encoding='UTF-8') as temp:
        db = await temp.read()
    db = literal_eval(db)

    db_peer_ids_keys = list(db.keys())
    for key in db_peer_ids_keys:
        user = db.get(key)
        method = user.get('method')

        match method:
            case 'every_n_hours':
                peer_id = key
                hours = user.get('hours')
                scheduler.add_job(send_schedule_every_n_hours,
                                  args=(peer_id, hours))
            case 'n_times_a_day':
                peer_id = key
                amount = user.get('amount')
                scheduler.add_job(send_schedule_n_times_a_day,
                                  args=(peer_id, amount))

            case 'on_change':
                peer_id = key
                scheduler.add_job(send_schedule_on_change,
                                  args=[peer_id])


async def on_shutdown():
    scheduler.shutdown(wait=False)
    await browser.close()
    logger.success('Scheduler and Chrome was killed')


def main():
    for bp in bps:
        bp.load(bot)

    scheduler.start()

    bot.loop_wrapper.on_startup.extend((run_chrome_on_startup(),
                                       parse_groups_tags(),
                                       load_tasks_from_db_on_startup(),
                                       set_group_status_online()))

    bot.loop_wrapper.on_shutdown.append(on_shutdown())

    bot.run_forever()


if __name__ == '__main__':
    main()
