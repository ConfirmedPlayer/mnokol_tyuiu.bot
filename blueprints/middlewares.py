from vkbottle import BaseMiddleware
from vkbottle.bot import Blueprint, Message
from loguru import logger


bp = Blueprint('Middlewares')


class NoBotMiddleware(BaseMiddleware[Message]):
    async def pre(self):
        if self.event.from_id < 0:
            logger.warning(f"{self.event.from_id} / {self.event.peer_id} tried to use bot. \
                More details:\n\n{self.event}")

            self.stop()


bp.labeler.message_view.register_middleware(NoBotMiddleware)
