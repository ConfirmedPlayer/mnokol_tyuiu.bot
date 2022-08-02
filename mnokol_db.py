from additional import sql_queries

from asyncpg import Pool


class MNOKOL_DB:
    def __init__(self, connection: Pool) -> None:
        self.connection = connection

    async def create_table_if_not_exists(self) -> None:
        await self.connection.fetch(sql_queries.create_table_if_not_exist)

    async def select_group(self, peer_id: int) -> str:
        group = await self.connection.fetch(sql_queries.select_peer_group, peer_id)
        return group[0]['peer_group']

    async def select_url(self, peer_id: int) -> str:
        url = await self.connection.fetch(sql_queries.select_peer_url, peer_id)
        return url[0]['url']

    async def select_method(self, peer_id: int) -> str:
        method = await self.connection.fetch(sql_queries.select_peer_method, peer_id)
        return method[0]['method']

    async def select_hours(self, peer_id: int) -> int:
        hours = await self.connection.fetch(sql_queries.select_peer_hours, peer_id)
        return hours[0]['hours']

    async def select_amount(self, peer_id: int) -> int:
        amount = await self.connection.fetch(sql_queries.select_peer_amount, peer_id)
        return amount[0]['amount']

    async def is_peer_subscribed(self, peer_id: int) -> bool:
        is_subscribed = await self.connection.fetch(sql_queries.is_peer_subscribed, peer_id)
        return is_subscribed[0]['subscribed']

    async def is_peer_in_db(self, peer_id: int) -> bool:
        peer_in_db = await self.connection.fetch(sql_queries.is_peer_in_db, peer_id)
        return peer_in_db[0]['exists']

    async def add_new_peer(self,
                           peer_id: int,
                           peer_group: str,
                           url: str) -> None:
        await self.connection.fetch(sql_queries.add_new_peer, peer_id, peer_group, url)

    async def update_existed_peer(self,
                                  peer_id: int,
                                  peer_group: str,
                                  url: str) -> None:
        await self.connection.fetch(sql_queries.update_existed_peer, peer_group, url, peer_id)

    async def set_peer_method(self,
                              peer_id: int,
                              method: str) -> None:
        await self.connection.fetch(sql_queries.set_peer_method, method, peer_id)

    async def set_peer_hours(self,
                             peer_id: int,
                             hours: int) -> None:
        await self.connection.fetch(sql_queries.set_peer_hours, hours, peer_id)

    async def set_peer_amount(self,
                              peer_id: int,
                              amount: int) -> None:
        await self.connection.fetch(sql_queries.set_peer_amount, amount, peer_id)

    async def set_peer_subscribe_state(self,
                                       peer_id: int,
                                       subscribed: bool) -> None:
        await self.connection.fetch(sql_queries.set_peer_subscribe_state, subscribed, peer_id)

    async def select_subscribed_peers(self) -> list:
        return await self.connection.fetch(sql_queries.select_subscribed_peers)
