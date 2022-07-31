from additional.message_templates import on_group_join_message

from vkbottle import GroupEventType, GroupTypes
from vkbottle.bot import Blueprint


bp = Blueprint('Events')


@bp.on.raw_event(GroupEventType.GROUP_JOIN, GroupTypes.GroupJoin)
async def group_join(event: GroupTypes.GroupJoin):
    await bp.api.messages.send(random_id=0,
                               user_id=event.object.user_id,
                               message=on_group_join_message)
