from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = rf"""
*Hello {update.effective_user.mention_markdown_v2()}\!*

You could search any route by number, just type `/search <any_bus_number>`
"""
    await update.message.reply_markdown_v2(
        text,
        reply_markup=None,
    )
