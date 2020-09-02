from tinydb import TinyDB, Query
from utilities import formatting

settings = settings.config("settings.json")
db = TinyDB(settings.DB_PATH)
member = Query()

def activity_push(m, d):
    d = str(d)
    for i in m:
        table = db.table(i)
        table.upsert({'last_seen' : d}, member.id == i)
    formatting.fancify(settings.DB_PATH)

    