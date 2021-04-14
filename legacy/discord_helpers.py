from config import DISCORD_TOKEN, DEALIFY_DB_CREDS, DISCORD_NEW_ITEM_HEADER_ROW
import discord
from discord.ext import commands
import logging
import asyncio
from tabulate import tabulate
from database_helpers import read_craigslist_items_by_search_id, connect_dealify_db, disconnect_dealify_db
from core.database.db_helpers import start_pool, read_models
from core.models.craigslist.craigslist_item import CraigslistItem


def format_new_item_row(item):
    item_name = None
    item_location = ""
    item_price = None
    item_url = None
    try:
        item_name = item.item_name
        item_url = item.source_url
        item_price = item.price

    except AttributeError as ae:
        logging.error(
            f"Unable to Format Item for Message - Required Attribute Not Found - Data: {ae}")
        return None

    try:
        item_location = item.item_location
    except AttributeError as ae:
        logging.error(f"Format Item for Message - No Location - Data: {ae}")

    return [item_name, item_price, item_location, item_url]


def count(item):
    try:
        return len(item)
    except TypeError as te:
        print(f"Received Type Error, Type: {type(item)} Has No Length!")
        return 0


def format_embedded_new_item_message(item):
    try:
        embed_item = discord.Embed(
            title=item.item_name, url=item.source_url, color=0x00ff00)

        embed_item.add_field(name="Price", value=f'${item.price}', inline=True)
        if item.item_location:
            embed_item.add_field(
                name="Location", value=f'{item.item_location.capitalize()}', inline=True)
        return embed_item
    except Exception as e:
        print(
            f"Format Embedded New Item Message - Encountered Exception - Data: {e}")
        return None


@commands.command(name="NewItems")
async def new_dealify_items(ctx, search_id: int = None, limit: int = 10):
    if limit == 0:
        logging.info(
            f"All Items Requested for Search - Search ID: {search_id}")
        limit = 1000
    items = await read_models(ctx.db_conn_pool, CraigslistItem, read_craigslist_items_by_search_id, [search_id])

    if not DISCORD_NEW_ITEM_HEADER_ROW:
        logging.error(f"Format Item for Message - Header Row is None")
        return None

    await ctx.send(f'Found {count(items)} New items for {search_id}:')
    # full_item_message = ""
    item_table = [DISCORD_NEW_ITEM_HEADER_ROW]
    for item in items:
        # if len(tabulate(item_table, tablefmt="fancy_grid")) >= 2000:
        #     popped_item = item_table.pop()
        #     await ctx.send(f'``` {tabulate(item_table, tablefmt="fancy_grid")} ```')
        #     item_table = [popped_item]
        if item.is_deleted:
            logging.info(
                f"New Deality Items Command - Skipping Deleted Item - Item ID: {item.item_id}")
            continue
        embedded_item_message = format_embedded_new_item_message(item)
        if embedded_item_message:
            await ctx.send(embed=embedded_item_message)
        else:
            logging.error(
                f"New Dealify Items Command - Received Invalid Item Message for Item - Item: {item}")
    # if item_table:
    #     await ctx.send(f'```{tabulate(item_table, tablefmt="fancy_grid")}```')

    disconnect_dealify_db(conn)


def run_test():
    loop = asyncio.get_event_loop()
    pool = loop.run_until_complete(start_pool(DEALIFY_DB_CREDS))
    bot = commands.Bot(command_prefix='$')
    bot.db_conn_pool = pool
    bot.add_command(new_dealify_items)
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    run_test()
