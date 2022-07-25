from config import admin_user_id

from vkbottle.bot import Blueprint, Message, rules


bp = Blueprint("Admin Commands")
bp.labeler.auto_rules = [rules.FromPeerRule(admin_user_id)]


@bp.on.message(text='/eval <code>')
async def evaluate_from_bot(message: Message, code: str):
    await message.reply('Выполняю...')
    evaluated_expression = eval(code)
    await message.reply(f'Результат:\n\n{evaluated_expression}')
