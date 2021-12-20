# (c) @AbirHasan2005

import datetime
import motor.motor_asyncio


class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.black = self.db.blacklist
        self.hour = self.db.hour
        self.db2 = self._client["UserID"]


# ----------------------add ,check or remove user----------------------
    def new_user(self, id):
        return dict(
            id=id,
            join_date=datetime.date.today().isoformat()
        )

    async def add_user(self, id):
        user = self.new_user(id)
        await self.col.insert_one(user)
    
    async def remove_user(self, id):
        await self.col.delete_one({'id': int(id)})

    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})

        return True if user else False

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

# ----------------------ban, check banned or unban user----------------------
    def black_user(self, id):
        return dict(
            id=id,
            ban_date=datetime.date.today().isoformat()
        )

    async def ban_user(self, id):
        user = self.black_user(id)
        await self.black.insert_one(user)

    async def unban_user(self, id):
        await self.black.delete_one({'id': int(id)})

    async def is_user_banned(self, id):
        user = await self.black.find_one({'id': int(id)})
        return True if user else False

    async def total_banned_users_count(self):
        count = await self.black.count_documents({})
        return count

# ----------------------Add users File Data----------------------

    def sent_data(self, id, message_id , filename, filesize):
        return dict(
            message_id=message_id,
            file_name=filename,
            file_size=filesize,
            sent_date=datetime.date.today().isoformat()
        )

    async def user_data(self, id, message_id , filename, filesize):
        self.add = self.db2[str(id)]
        user_data = self.sent_data(id, message_id , filename, filesize)
        await self.add.insert_one(user_data)

# ----------------------Add or remove user from 24 Link----------------------

    async def is_user_in_24hour(self, id):
        user = await self.hour.find_one({'id': int(id)})
        return True if user else False

    def new_user_in_24(self, id):
        return dict(
            id=id
        )

    async def add_user_in_24(self, id):
        user = self.new_user_in_24(id)
        await self.hour.insert_one(user)

    async def remove_user_from_24(self, id):
        await self.hour.delete_one({'id': int(id)})