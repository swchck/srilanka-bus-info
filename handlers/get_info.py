from bs4 import BeautifulSoup
import re
import requests

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from urllib.parse import urljoin
from telegram.helpers import escape_markdown

from constants import BUS_INFORMATION_MESSAGE, BASE_PATH, DATA_NOT_PROVIDED


class RouteInfo:
    def __init__(
        self,
        route_number,
        travel_time: str,
        distance: str,
        timings: dict,
        schedule_link: str,
        route_map_link: str,
        fare_stages_link: str,
    ) -> None:
        self.route_number = route_number
        self.travel_time = travel_time if travel_time is not None else DATA_NOT_PROVIDED
        self.distance = distance if distance is not None else DATA_NOT_PROVIDED
        self.timings = timings if timings is not None else DATA_NOT_PROVIDED
        self.schedule_link = schedule_link
        self.route_map_link = route_map_link
        self.fare_stages_link = fare_stages_link

    def get_timetable_str(self) -> str:
        # TODO: Move to Markdown table or to WebApp
        timetable = [
            rf'*{name}*: {", ".join(value)}' for name, value in self.timings.items()
        ]
        timetable = "\t\n".join(timetable)
        return timetable

    def get_human_time(self) -> str:
        if self.travel_time is DATA_NOT_PROVIDED:
            return DATA_NOT_PROVIDED
        minutes = int(self.travel_time)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}"

    def get_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = [
            [
                InlineKeyboardButton(
                    r"📅 Full Schedule", url=urljoin(BASE_PATH, self.schedule_link)
                )
            ],
            [
                InlineKeyboardButton(
                    r"🗺️ Route Map", url=urljoin(BASE_PATH, self.route_map_link)
                )
            ],
            [
                InlineKeyboardButton(
                    r"💵 Fare Stages", url=urljoin(BASE_PATH, self.fare_stages_link)
                )
            ],
        ]
        return InlineKeyboardMarkup(keyboard)

    @classmethod
    def from_html(cls, html_text: str):
        soup = BeautifulSoup(html_text, "html.parser")

        obj = dict()

        # Extract the route number
        route_number = soup.find("h2").text.split()[0]

        # Extract key-value pairs
        for span in soup.find_all("span", class_="text-left text-muted"):
            text = span.text  #  type: str
            text.strip()

            if text.__contains__(","):
                text_arr = text.split(", ")
                key = text_arr[0].lower().replace(" ", "_")
                value = text_arr[1]

            if text.__contains__(":"):
                text_arr = text.split(":")
                key = text_arr[0].lower().replace(" ", "_")
                value = text_arr[1]

            obj[key] = r"{}".format(value)

        # Extract bus timings
        timings = {}

        for div in soup.find_all("div", class_="timedisplaybox"):
            location = div.find("strong").text.lower()
            timings[location] = []
            for h1 in div.find_all("h1"):
                timings[location].append(h1.text.strip())

        # Extract links to external pages
        schedule_link = soup.find("a", {"title": "Complete Schedule"})["href"]
        route_map_link = soup.find("a", {"title": "Route on map"})["href"]
        fare_stages_link = soup.find("a", {"title": "Fare Stages"})["href"]

        return cls(
            route_number,
            obj.get("travel_time(minutes)"),
            obj.get("distance(km)"),
            timings,
            re.sub(r"&width=[^&]*&height=[^&]*&iframe=true", "", schedule_link),
            re.sub(r"&width=[^&]*&height=[^&]*&iframe=true", "", route_map_link),
            re.sub(r"&width=[^&]*&height=[^&]*&iframe=true", "", fare_stages_link),
        )


async def get_route_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bus_number = update.callback_query.data.split(":")[1]
    get_route = rf"schedulebyroute.php?routenumber={bus_number}"
    url = urljoin(BASE_PATH, get_route)

    response = requests.post(url)

    if response.status_code == 200:
        html = response.text
        route_info = RouteInfo.from_html(html)

        text = BUS_INFORMATION_MESSAGE.format(
            route_number=escape_markdown(route_info.route_number, version=2),
            travel_time=escape_markdown(route_info.travel_time, version=2),
            human_time=route_info.get_human_time(),
            distance=escape_markdown(route_info.distance, version=2),
            bus_timings=escape_markdown(route_info.get_timetable_str(), version=2),
        )

    await update.callback_query.edit_message_text(
        text=text,
        reply_markup=route_info.get_keyboard(),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
