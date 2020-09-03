import asyncio

from datetime import datetime
from tinydb import TinyDB, Query
from utilities import formatting, settings

settings = settings.config("settings.json")

def activity_push(m, d):
    #entered activity_push
    d = str(datetime.now().date())
    for i in m:
        path = settings.DB_PATH + str(i) + '.json'
        db = TinyDB(path)
        member = Query()
        table = db.table('information')
        table.upsert({'last_seen' : d}, member.last_seen != None) #If conditional is True: update. If False: insert.
        formatting.fancify(path) 