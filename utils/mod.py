from typing import List, Iterable, Union
import discord
import asyncio


async def mass_purge(messages: List[discord.Message],
                     channel: discord.TextChannel):
    while messages:
        if len(messages) > 1:
            await channel.delete_messages(messages[:100])
            messages = messages[100:]
        else:
            await messages[0].delete()
            messages = []
        await asyncio.sleep(1.5)


async def slow_deletion(messages: Iterable[discord.Message]):
    for message in messages:
        try:
            await message.delete()
        except discord.HTTPException:
            pass