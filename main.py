from additional import chrome_options
from additional import message_templates as msg_templates
from blueprints import bps
from config import token, api_link, group_id, admin_user_id, schedule_menu_url, db_credentials
from keyboards import schedule_keyboards
from mnokol_db import MNOKOL_DB
from states.schedule_states import ScheduleStates

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bs4 import BeautifulSoup
from datetime import datetime
from loguru import logger
from pyppeteer import launch
from pytz import timezone
from vkbottle import AiohttpClient, VKAPIError
from vkbottle.bot import Bot, Message, rules
from vkbottle.tools import PhotoMessageUploader
import asyncio
import asyncpg
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

    schedule_url = api_link.format(group=group,
                                   sid=sid,
                                   gr=gr)
    return {'URL': schedule_url,
            'group': group}


@logger.catch
async def take_screenshot(URL: str, group: str):
    local_screenshot_options = chrome_options.screenshot_options
    group_filename = f'{group}.png'
    local_screenshot_options.update(path=f'./temp/{group_filename}')
    try:
        page = await browser.newPage()
        await page.goto(URL, options=chrome_options.goto_options)
        await page.screenshot(options=local_screenshot_options)
        return await PhotoMessageUploader(bot.api).upload(f'./temp/{group_filename}')
    finally:
        await page.close()


@logger.catch
async def send_schedule_every_n_hours(peer_id: int, hours: int):
    logger.success(f'Send schedule every {hours} hours for {peer_id} was started')

    peer_subscribed = await DB.is_peer_subscribed(peer_id)

    while peer_subscribed:
        peer_subscribed = await DB.is_peer_subscribed(peer_id)

        while datetime.now().minute != 0:
            await asyncio.sleep(0)

        URL = await DB.select_url(peer_id)
        group = await DB.select_group(peer_id)

        uploaded_screenshot = await take_screenshot(URL, group)

        await bot.api.messages.send(random_id=0,
                                    peer_id=peer_id,
                                    attachment=uploaded_screenshot)

        await asyncio.sleep(hours * 3300)

    logger.info(f'{peer_id} unsubscribed')


@logger.catch
async def send_schedule_n_times_a_day(peer_id: int, amount: int):
    logger.success(f'Send schedule {amount} times for {peer_id} was started')

    time_zone = timezone('Asia/Yekaterinburg')

    two_times_range = ('06:00', '19:00')
    three_times_range = ('06:00', '12:00', '18:00')
    four_times_range = ('06:00', '12:00', '16:00', '20:00')
    five_times_range = ('06:00', '12:00', '15:00', '18:00', '21:00')

    peer_subscribed = await DB.is_peer_subscribed(peer_id)

    match amount:
        case 2:
            while peer_subscribed:
                peer_subscribed = await DB.is_peer_subscribed(peer_id)

                time_now = datetime.now(time_zone).strftime('%H:%M')

                if time_now in two_times_range:
                    URL = await DB.select_url(peer_id)
                    group = await DB.select_group(peer_id)

                    uploaded_screenshot = await take_screenshot(URL, group)

                    await bot.api.messages.send(random_id=0,
                                                peer_id=peer_id,
                                                attachment=uploaded_screenshot,
                                                message=time_now)
                    await asyncio.sleep(39300)

                await asyncio.sleep(0)

            logger.info(f'{peer_id} unsubscribed')
        case 3:
            while peer_subscribed:
                peer_subscribed = await DB.is_peer_subscribed(peer_id)

                time_now = datetime.now(time_zone).strftime('%H:%M')

                if time_now in three_times_range:
                    URL = await DB.select_url(peer_id)
                    group = await DB.select_group(peer_id)

                    uploaded_screenshot = await take_screenshot(URL, group)

                    await bot.api.messages.send(random_id=0,
                                                peer_id=peer_id,
                                                attachment=uploaded_screenshot,
                                                message=time_now)
                    await asyncio.sleep(21300)

                await asyncio.sleep(0)

            logger.info(f'{peer_id} unsubscribed')
        case 4:
            while peer_subscribed:
                peer_subscribed = await DB.is_peer_subscribed(peer_id)

                time_now = datetime.now(time_zone).strftime('%H:%M')

                if time_now in four_times_range:
                    URL = await DB.select_url(peer_id)
                    group = await DB.select_group(peer_id)

                    uploaded_screenshot = await take_screenshot(URL, group)

                    await bot.api.messages.send(random_id=0,
                                                peer_id=peer_id,
                                                attachment=uploaded_screenshot,
                                                message=time_now)
                    await asyncio.sleep(14100)

                await asyncio.sleep(0)

            logger.info(f'{peer_id} unsubscribed')
        case 5:
            while peer_subscribed:
                peer_subscribed = await DB.is_peer_subscribed(peer_id)

                time_now = datetime.now(time_zone).strftime('%H:%M')

                if time_now in five_times_range:
                    URL = await DB.select_url(peer_id)
                    group = await DB.select_group(peer_id)

                    uploaded_screenshot = await take_screenshot(URL, group)

                    await bot.api.messages.send(random_id=0,
                                                peer_id=peer_id,
                                                attachment=uploaded_screenshot,
                                                message=time_now)
                    await asyncio.sleep(10500)

                await asyncio.sleep(0)

            logger.info(f'{peer_id} unsubscribed')


@logger.catch
async def send_schedule_on_change(peer_id: int):
    logger.success(f'Send schedule on change for {peer_id} was started')

    URL = await DB.select_url(peer_id)

    async with AiohttpClient() as session:
        html = await session.request_text(URL)
    first_html = r''.join(html)

    peer_subscribed = await DB.is_peer_subscribed(peer_id)

    while peer_subscribed:
        peer_subscribed = await DB.is_peer_subscribed(peer_id)

        URL = await DB.select_url(peer_id)
        group = await DB.select_group(peer_id)

        async with AiohttpClient() as session:
            html = await session.request_text(URL)
        new_html = r''.join(html)

        if first_html != new_html:
            first_html = new_html
            uploaded_screenshot = await take_screenshot(URL, group)
            await bot.api.messages.send(random_id=0,
                                        peer_id=peer_id,
                                        attachment=uploaded_screenshot,
                                        message='Изменение в расписании')
        await asyncio.sleep(300)

    logger.info(f'{peer_id} unsubscribed')


@bot.on.chat_message(text='/группа <raw_group>')
async def set_group_public(message: Message, raw_group: str):
    if len(raw_group) not in range(10, 17):
        await message.reply(msg_templates.group_not_found_message)
        return

    group_and_url = await get_group(raw_group)

    if not isinstance(group_and_url, dict):
        await message.reply(msg_templates.group_not_found_message)
        return

    group = group_and_url.get('group')
    URL = group_and_url.get('URL')

    peer_already_exists = await DB.is_peer_in_db(message.peer_id)

    if peer_already_exists:
        await DB.update_existed_peer(peer_id=message.peer_id,
                                     peer_group=group,
                                     url=URL)
    else:
        await DB.add_new_peer(peer_id=message.peer_id,
                              peer_group=group,
                              url=URL)

    await message.reply(msg_templates.set_group_chat_success.format(group=group))

    await message.answer(msg_templates.set_group_success2,
                         keyboard=schedule_keyboards.GetScheduleKeyboard)


@bot.on.private_message(text='/группа <raw_group>')
async def set_group_private(message: Message, raw_group: str):
    if len(raw_group) not in range(10, 17):
        await message.reply(msg_templates.group_not_found_message)
        return

    group_and_url = await get_group(raw_group)

    if not isinstance(group_and_url, dict):
        await message.reply(msg_templates.group_not_found_message)
        return

    group = group_and_url.get('group')
    URL = group_and_url.get('URL')

    peer_already_exists = await DB.is_peer_in_db(message.peer_id)

    if peer_already_exists:
        await DB.update_existed_peer(peer_id=message.peer_id,
                                     peer_group=group,
                                     url=URL)
    else:
        await DB.add_new_peer(peer_id=message.peer_id,
                              peer_group=group,
                              url=URL)

    await message.reply(msg_templates.set_group_private_success.format(user_id=message.peer_id,
                                                                       group=group))
    await message.answer(msg_templates.set_group_success2,
                         keyboard=schedule_keyboards.GetScheduleKeyboard)


@bot.on.message(text='/расписание')
async def show_schedule(message: Message):
    peer_in_db = await DB.is_peer_in_db(message.peer_id)

    if not peer_in_db:
        await message.reply(msg_templates.group_not_set_message)
    else:
        URL = await DB.select_url(message.peer_id)
        group = await DB.select_group(message.peer_id)

        uploaded_screenshot = await take_screenshot(URL, group)

        await message.answer(attachment=uploaded_screenshot,
                             keyboard=schedule_keyboards.GetScheduleKeyboard)


@bot.on.chat_message(text='/рассылка <digit>')
async def subscribe_to_first_method_public(message: Message, digit: str):
    if not digit.isdigit():
        return await message.reply(msg_templates.incorrect_number)

    n = int(digit)

    if not 100 > n > 0:
        return await message.reply(msg_templates.incorrect_number_range)

    peer_in_db = await DB.is_peer_in_db(message.peer_id)

    if not peer_in_db:
        return await message.reply(msg_templates.group_not_set_message)

    peer_subscribed = await DB.is_peer_subscribed(message.peer_id)

    if peer_subscribed:
        return await message.reply(msg_templates.already_subscribed_message)

    await DB.set_peer_method(peer_id=message.peer_id, method='every_n_hours')
    await DB.set_peer_hours(peer_id=message.peer_id, hours=n)
    await DB.set_peer_subscribe_state(peer_id=message.peer_id, subscribed=True)

    await message.reply(msg_templates.subscription_successful,
                        keyboard=schedule_keyboards.GetScheduleKeyboard)

    scheduler.add_job(send_schedule_every_n_hours,
                      args=(message.peer_id, n))


@bot.on.private_message(state=ScheduleStates.WAITING_A_NUMBER)
async def subscribe_to_first_method_private(message: Message):
    if not message.text.isdigit():
        return await message.reply(msg_templates.incorrect_number)

    n = int(message.text)

    if not 100 > n > 0:
        return await message.reply(msg_templates.incorrect_number_range)

    peer_in_db = await DB.is_peer_in_db(message.peer_id)

    if not peer_in_db:
        await bot.state_dispenser.delete(message.peer_id)
        return await message.reply(msg_templates.group_not_set_message)

    peer_subscribed = await DB.is_peer_subscribed(message.peer_id)

    if peer_subscribed:
        await bot.state_dispenser.delete(message.peer_id)
        return await message.reply(msg_templates.already_subscribed_message)

    await DB.set_peer_method(peer_id=message.peer_id, method='every_n_hours')
    await DB.set_peer_hours(peer_id=message.peer_id, hours=n)
    await DB.set_peer_subscribe_state(peer_id=message.peer_id, subscribed=True)

    await message.reply(msg_templates.subscription_successful,
                        keyboard=schedule_keyboards.GetScheduleKeyboard)

    await bot.state_dispenser.delete(message.peer_id)

    scheduler.add_job(send_schedule_every_n_hours,
                      args=(message.peer_id, n))


@bot.on.message(text='/подписка')
async def subscription_types(message: Message):
    peer_in_db = await DB.is_peer_in_db(message.peer_id)

    if peer_in_db:
        peer_subscribed = await DB.is_peer_subscribed(message.peer_id)

        if not peer_subscribed:
            await message.reply(msg_templates.choose_subscription_message,
                                keyboard=schedule_keyboards.SpamVariantsKeyboard)
        else:
            await message.reply(msg_templates.already_subscribed_message)
    else:
        await message.reply(msg_templates.group_not_set_message)


@bot.on.message(text='/отписаться')
async def unsubscribe(message: Message):
    peer_in_db = await DB.is_peer_in_db(message.peer_id)

    if not peer_in_db:
        await message.reply(msg_templates.group_not_set_message)
    else:
        peer_subscribed = await DB.is_peer_subscribed(message.peer_id)

        if not peer_subscribed:
            await message.reply(msg_templates.not_subscribed_error)
        else:
            await DB.set_peer_subscribe_state(peer_id=message.peer_id, subscribed=False)

            await message.reply(msg_templates.unsubscription_successful,
                                keyboard=schedule_keyboards.GetScheduleKeyboard)


@bot.on.chat_message(payload={"command": "every_n_hours"})
async def every_n_hours_payload_public(message: Message):
    return await message.reply(msg_templates.every_n_hours_method_template_public)


@bot.on.private_message(payload={"command": "every_n_hours"})
async def every_n_hours_payload_private(message: Message):
    await bot.state_dispenser.set(message.peer_id, ScheduleStates.WAITING_A_NUMBER)
    return await message.reply(msg_templates.every_n_hours_method_template_private)


@bot.on.message(payload={"command": "n_times"})
async def n_times_payload(message: Message):
    return await message.reply(msg_templates.choose_subscription_message,
                               keyboard=schedule_keyboards.AmountVariantsKeyboard)


@bot.on.message(payload={"command": "two_times"})
async def two_times_payload(message: Message):
    await DB.set_peer_method(peer_id=message.peer_id, method='every_n_hours')
    await DB.set_peer_amount(peer_id=message.peer_id, amount=2)
    await DB.set_peer_subscribe_state(peer_id=message.peer_id, subscribed=True)

    await message.reply(msg_templates.subscribed_to_2_times,
                        keyboard=schedule_keyboards.GetScheduleKeyboard)

    scheduler.add_job(send_schedule_n_times_a_day,
                      args=(message.peer_id, 2))


@bot.on.message(payload={"command": "three_times"})
async def three_times_payload(message: Message):
    await DB.set_peer_method(peer_id=message.peer_id, method='every_n_hours')
    await DB.set_peer_amount(peer_id=message.peer_id, amount=3)
    await DB.set_peer_subscribe_state(peer_id=message.peer_id, subscribed=True)

    await message.reply(msg_templates.subscribed_to_3_times,
                        keyboard=schedule_keyboards.GetScheduleKeyboard)

    scheduler.add_job(send_schedule_n_times_a_day,
                      args=(message.peer_id, 3))


@bot.on.message(payload={"command": "four_times"})
async def four_times_payload(message: Message):
    await DB.set_peer_method(peer_id=message.peer_id, method='every_n_hours')
    await DB.set_peer_amount(peer_id=message.peer_id, amount=4)
    await DB.set_peer_subscribe_state(peer_id=message.peer_id, subscribed=True)

    await message.reply(msg_templates.subscribed_to_4_times,
                        keyboard=schedule_keyboards.GetScheduleKeyboard)

    scheduler.add_job(send_schedule_n_times_a_day,
                      args=(message.peer_id, 4))


@bot.on.message(payload={"command": "five_times"})
async def five_times_payload(message: Message):
    await DB.set_peer_method(peer_id=message.peer_id, method='every_n_hours')
    await DB.set_peer_amount(peer_id=message.peer_id, amount=5)
    await DB.set_peer_subscribe_state(peer_id=message.peer_id, subscribed=True)

    await message.reply(msg_templates.subscribed_to_5_times,
                        keyboard=schedule_keyboards.GetScheduleKeyboard)

    scheduler.add_job(send_schedule_n_times_a_day,
                      args=(message.peer_id, 5))


@bot.on.message(payload={"command": "on_change"})
async def on_change_payload(message: Message):
    await DB.set_peer_method(peer_id=message.peer_id, method='on_change')
    await DB.set_peer_subscribe_state(peer_id=message.peer_id, subscribed=True)

    await message.reply(msg_templates.on_change_method_subscribed,
                        keyboard=schedule_keyboards.GetScheduleKeyboard)

    scheduler.add_job(send_schedule_on_change, args=[message.peer_id])


@bot.on.message(payload={"command": "get_schedule"})
async def get_schedule_payload(message: Message):
    URL = await DB.select_url(message.peer_id)
    group = await DB.select_group(message.peer_id)

    uploaded_screenshot = await take_screenshot(URL, group)

    await message.answer(attachment=uploaded_screenshot,
                         keyboard=schedule_keyboards.GetScheduleKeyboard)


@bot.on.chat_message(rules.ChatActionRule("chat_invite_user"))
async def bot_joined(message: Message):
    if message.action.member_id and abs(message.action.member_id) == group_id:
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

    browser = await launch(options=chrome_options.browser_options)
    logger.success('Chrome was started')


@scheduler.scheduled_job('interval', days=1)
async def parse_groups_tags():
    global soup
    global all_groups

    try:
        page = await browser.newPage()
        await page.goto(schedule_menu_url, options=chrome_options.goto_options)
        await asyncio.sleep(10)
        html = await page.content()

        soup = BeautifulSoup(html, 'lxml')
        zero_group = soup.find('option').find_next()
        all_groups = str(zero_group.find_next_siblings())

        logger.success('Groups was parsed')
    finally:
        await page.close()


@scheduler.scheduled_job('interval', hours=3)
async def set_group_status_online():
    try:
        await bot.api.groups.enable_online(group_id)
        logger.success('Group is online now')
    except VKAPIError:
        logger.info('Online is already enabled')


async def load_tasks_from_db_on_startup():
    subscribed_peers = await DB.select_subscribed_peers()

    for peer in subscribed_peers:
        peer_id = peer['peer_id']
        method = await DB.select_method(peer_id)

        match method:
            case 'every_n_hours':
                hours = await DB.select_hours(peer_id)

                scheduler.add_job(send_schedule_every_n_hours,
                                  args=(peer_id, hours))
            case 'n_times_a_day':
                amount = await DB.select_amount(peer_id)

                scheduler.add_job(send_schedule_n_times_a_day,
                                  args=(peer_id, amount))

            case 'on_change':
                scheduler.add_job(send_schedule_on_change,
                                  args=[peer_id])


async def run_db_connect_on_startup():
    global conn
    global DB

    conn = await asyncpg.create_pool(**db_credentials)
    DB = MNOKOL_DB(conn)
    await DB.create_table_if_not_exists()


async def on_shutdown():
    scheduler.shutdown(wait=False)
    await browser.close()
    await conn.close()
    logger.success('Scheduler, Chrome and postgresql was killed')


def main():
    for bp in bps:
        bp.load(bot)

    bot.loop_wrapper.on_startup = [run_chrome_on_startup(),
                                   run_db_connect_on_startup(),
                                   parse_groups_tags(),
                                   load_tasks_from_db_on_startup(),
                                   set_group_status_online()]

    bot.loop_wrapper.on_shutdown = [on_shutdown()]

    scheduler.start()

    bot.run_forever()


if __name__ == '__main__':
    main()
