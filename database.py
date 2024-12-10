import sqlite3, asyncio

globalLock = asyncio.Lock()

class DataBase:
    def __init__(self):
        pass

    async def getTable(self, attribute):
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        tables = list(c.execute("SELECT name FROM sqlite_schema"))
        
        compiled = {}
        
        for table in tables:
            compiled[table[0]] = []

        for table in compiled:
            columns = c.execute("PRAGMA table_info({0})".format(table))
            columns = list(columns)
            for column in columns:
                compiled[table].append(column[1])
    
        conn.close()

        for table in compiled:
            if attribute in compiled[table]:
                return table
        
        return None

    async def getValue(self, id, attribute):
        table = await self.getTable(attribute)
        if table is None:
            print("Attribute does not exist in any table")
            return False

        conn = sqlite3.connect('data.db')
        c = conn.cursor()

        data = c.execute("SELECT {0} FROM {1} WHERE id = {2}".format(attribute, table, id))
        data = list(data)
        conn.close()
        return data[0][0]


    async def changeValue(self, id, value, attribute):
        table = await self.getTable(attribute)
        if table is None:
            print("Attribute does not exist in any table")
            return False
        
        current = await self.getValue(id, attribute)

        if value < 0 and current < abs(value):
            if attribute == "balance":
                return False
        
        await globalLock.acquire()

        conn = sqlite3.connect('data.db')
        c = conn.cursor()

        c.execute("UPDATE {0} SET {1} = {2} WHERE id = {3}".format(table, attribute, current + value, id))

        conn.commit()
        conn.close()
        globalLock.release()
        return True

    async def setValue(self, id, value, attribute):
        table = await self.getTable(attribute)
        if table is None:
            print("Attribute does not exist in any table")
            return False
        
        await globalLock.acquire()
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
    
        c.execute("UPDATE {0} SET {1} = {2} WHERE id = {3}".format(table, attribute, value, id))
        
        conn.commit()
        conn.close()
        globalLock.release()
        return True
    
    async def setup(self, bot, GUILD, startingCurrency):
        try:
            guild = bot.get_guild(GUILD)
            conn = sqlite3.connect('data.db')
            c = conn.cursor()
            profileCommands = []
            result = c.execute("SELECT id FROM profile")
            data = list(result.fetchall())
            data = [item[0] for item in data]
            for member in guild.members:
                if member.id not in data:
                    profileCommands.append((member.id, startingCurrency))
            if (len(profileCommands) > 0):
                c.executemany("INSERT INTO profile VALUES (?, ?)", profileCommands)
            conn.commit()
            conn.close()
            print("DB Setup Done")
        except Exception as e:
            print("Error Connecting to data.db : " + str(e))
