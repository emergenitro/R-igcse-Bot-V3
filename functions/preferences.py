import os
import pymongo
from dotenv import dotenv_values

class GuildPreferencesDB:
    def __init__(self, link: str):
        self.client = pymongo.MongoClient(
            link, server_api=pymongo.server_api.ServerApi('1'))
        self.db = self.client.IGCSEBot
        self.pref = self.db["guild_preferences"]

    def set_pref(self, pref: str, pref_value, guild_id: int):
        """ 'pref' can be 'modlog_channel' or 'rep_enabled'. """
        result = self.pref.update_one({"guild_id": guild_id}, {
                                      "$set": {pref: pref_value}}, upsert=True)
        return result

    def get_pref(self, pref: str, guild_id: int):
        result = self.pref.find_one({"guild_id": guild_id})
        if result is None:
            return None
        else:
            return result.get(pref, None)


LINK = dotenv_values(".env")["MONGO_LINK"]
gpdb = GuildPreferencesDB(LINK)
