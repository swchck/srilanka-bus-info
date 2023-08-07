from bs4 import BeautifulSoup
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.constants import CHOOSE_ROUTE, FAILED_TO_GET_ROUTES


async def search_by_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = "https://www.sprpta.lk/searchroute.php"

    if context.args.__len__() > 0:
        data = {"searchword": context.args[0]}
    else:
        await update.message.reply_markdown_v2(
            "Bus number not provided for command, example: `/search 350`",
            reply_markup=None,
        )
        return

    res = requests.post(url, data=data)

    keyboard = []
    if res.status_code == 200:
        html = res.text

        soup = BeautifulSoup(html, "html.parser")
        for div in soup.find_all("div", class_="display_box"):
            route_number = div.text.split()[0]
            route_desc = div.text.split(maxsplit=1)[1]
            keyboard.append(
                [
                    InlineKeyboardButton(
                        rf"{route_number} {route_desc}",
                        callback_data=rf"#find_bus:{route_number}",
                    )
                ]
            )

    await update.message.reply_markdown_v2(
        CHOOSE_ROUTE if keyboard.__len__() > 0 else FAILED_TO_GET_ROUTES,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
