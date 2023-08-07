#!/usr/bin/env python
# pylint: disable=unused-argument,wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

#####################
# IMPORTS
#####################

import os
import logging

from os import getenv
from handlers import get_info, search, start
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler, 
    CallbackQueryHandler,
    Application,
    CommandHandler,
    ContextTypes,
)

# Define a few command handlers.

#####################
# LOGGER SETTINGS
#####################

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def sri_lanka_bot(text: any) -> None:
    # Create Application
    application = (
        Application.builder().token(getenv("TELEGRAM_TOKEN")).build()
    )
    
    # Add Handlers
    application.add_handler(CommandHandler("start", start.start))
    application.add_handler(CommandHandler("search", search.search_by_number))
    application.add_handler(CommandHandler("s", search.search_by_number))
    application.add_handler(CallbackQueryHandler(get_info.get_route_info))

    # Start application
    await application.bot.set_webhook(url=getenv("WEBHOOK"))
    await application.update_queue.put(
        Update.de_json(data=text, bot=application.bot)
    )
    async with application:
        await application.start()
        await application.stop()
