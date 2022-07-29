from additional.message_templates import start_message
from additional.teachers_db import teachers

from vkbottle.bot import Blueprint, Message
import re


bp = Blueprint('Other Functionality')


@bp.on.message(payload={"command": "start"})
async def payload_start(_):
    return start_message


@bp.on.message(text=['/start', '/help'])
async def command_start(_):
    return start_message


@bp.on.message(text='/преп <teacher>')
async def get_teacher_full_name(message: Message, teacher: str):
    regex = rf'(?<=<tr>\s<td width=\"\d\d\d\">){teacher}(.*?)(?=</td>)'
    matched_regex = re.findall(pattern=regex, string=teachers, flags=re.IGNORECASE)
    all_results = ''
    if matched_regex:
        for teacher_next_name in matched_regex:
            all_results += teacher.capitalize() + teacher_next_name + '\n\n'

        await message.reply(all_results)
    else:
        await message.reply('Преподаватель не найден.\nВозможно, его нет в базе ТИУ.')
