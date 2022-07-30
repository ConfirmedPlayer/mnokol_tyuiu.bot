from vkbottle import BaseMiddleware
from vkbottle.bot import Blueprint, Message


bp = Blueprint('Middlewares')


class NoBotMiddleware(BaseMiddleware[Message]):
    async def pre(self):
        if self.event.from_id < 0:
            self.stop()


bp.labeler.message_view.register_middleware(NoBotMiddleware)
