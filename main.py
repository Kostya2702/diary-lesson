from flask import Flask, render_template
import asyncio
import datetime
from netschoolapi import NetSchoolAPI
import collections
import os

app = Flask(__name__)

class Lesson:
    def __init__(
            self,
            day: datetime.datetime,
            start: datetime.date,
            end: datetime.date,
            room: str,
            number: int,
            subject: str
        ):
            self.day = day
            self.start = start
            self.end = end
            self.room = room
            self.number = number
            self.subject = subject

day_names = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

async def fetch_lessons():
    # Проверяем, есть ли сохраненная сессия
    ns = NetSchoolAPI('https://sgo.edu-74.ru/')
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    await ns.login(
        username,
        password,
        'МОУ "СОШ №13"',
    )

    diary = await ns.diary()
    lessons_by_weekday = {}

    for day in diary.schedule:
        for less in day.lessons:
            weekday = less.day.weekday()

            if weekday not in lessons_by_weekday:
                lessons_by_weekday[weekday] = []

            lessons_by_weekday[weekday].append(Lesson(
                less.day,
                less.start,
                less.end,
                less.room,
                less.number,
                less.subject
            ).__dict__)

    print(lessons_by_weekday)
    # asdf = dict(sorted(lessons_by_weekday.items(), key=lambda item: item[1]))
    # print(asdf)

    return collections.OrderedDict(
        (day_names[weekday], lessons) for weekday, lessons in sorted(lessons_by_weekday.items())
    )


@app.route("/")
def home():
    lessons_by_weekday = asyncio.run(fetch_lessons())
    return render_template("diary.html", lessons_by_weekday=lessons_by_weekday)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))