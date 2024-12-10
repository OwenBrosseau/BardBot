# File for general functions that are used in multiple scripts

import os
import datetime
import asyncio

messagingUsers = []

async def checkUser(ctx):
    if (ctx.author.id not in messagingUsers):
        print("User is not currently messaging")
        messagingUsers.append(ctx.author.id)
        print(messagingUsers)
        return True
    else:
        print("User is currently messaging")
        print(messagingUsers)
        return False

def valPrint(value : int):
    # Format: 1,000,000
    valString = str(value)
    valString = valString[::-1]
    valString = ','.join(valString[i:i+3] for i in range(0, len(valString), 3))
    valString = valString[::-1]

    return valString


