#!/usr/bin/env python
# pylint: disable=unused-argument,wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

#####################
# IMPORTS
#####################

import os
import logging

from handlers import get_info, search, start
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

#####################
# LOGGER SETTINGS
#####################

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    token = os.getenv("TELEGRAM_TOKEN")
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start.start))
    application.add_handler(CommandHandler("search", search.search_by_number))
    application.add_handler(CommandHandler("s", search.search_by_number))
    application.add_handler(CallbackQueryHandler(get_info.get_route_info))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
