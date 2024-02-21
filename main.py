import asyncio
import os
import sqlite3
from datetime import datetime

import aiohttp
from serpapi import GoogleSearch
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv('BOT_TOKEN')
omdb_api_key = os.getenv('OMDB_API_KEY')
kinopoisk_api_key = os.getenv('KINOPOISK_API_KEY')
rapid_api_key = os.getenv('RAPID_API_KEY')
google_custom_search_api_key = os.getenv('GCS_API_KEY')
custom_search_engine_id = os.getenv('CUSTOM_SEARCH_ENGINE_ID')
serpapi_key = os.getenv('SERPAPI_KEY')

conn = sqlite3.connect('data/bot.db')
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS search_history (
        user_id INTEGER,
        film_title TEXT,
        search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS stats (
        user_id INTEGER,
        film_title TEXT,
        count INTEGER DEFAULT 1
    )
""")

bot = Bot(token=bot_token)
dp = Dispatcher()


async def search_google(query):
    params = {
        "q": query,
        "location": "Russia",
        "hl": "ru",
        "gl": "ru",
        "google_domain": "google.ru",
        "api_key": serpapi_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    return results['organic_results'][:3]


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("""
Привет!

🎬Этот бот поможет тебе быстро получить краткое описание любого фильма, \
сериала или мультфильма, а также предоставит несколько ссылок для просмотра.

✉️Для того, чтобы начать достаточно ввести название фильма или сериала, не бойся опечаток - бот с ними справится.

🇷🇺/ 🇺🇸 Пользователь будь бдителен: если ввести название на английском языке или языке оригинала - \
бот выдаст ссылки для просмотра на официальных платформах (таких как prime, hbo или netflix). \
Как известно, бесплатный просмотр кино там невозможен, поэтому, если вы ищете способа посмотреть что-то бесплатно, \
вводите название на русском языке 🤫

На что еще он способен:
📝 Вывести историю запросов /history
📊Отобразить статистику предложенных фильмов /stats

Какую информацию ты получишь:
— Постер
— Название
— Рейтинг
— Год выпуска
— Жанры
— Сюжет
    """)


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("""
🎬️️Использование
Чтобы начать, введи название фильма или сериала, не бойся опечаток - бот с ними справится.

🇷🇺/🇺🇸Платно или бесплатно?
Пользователь будь бдителен: если ввести название на английском языке или языке оригинала - \
бот выдаст ссылки для просмотра на официальных платформах (таких как prime, hbo или netflix). \
Как известно, бесплатный просмотр кино там невозможен, поэтому, если вы ищете способа посмотреть что-то бесплатно, \
вводите название на русском языке 🤫

⚙️Команды
/start - описание бота
/help - помощь
/history - история запросов
/stats - статистика предложенных фильмов
/clear - очищение истории и статистики

⁉️Что делать, если остались вопросы?
Напиши администратору @maki_who
""")


@dp.message(Command('history'))
async def cmd_history(message: types.Message):
    cursor.execute("SELECT film_title, search_time FROM search_history WHERE user_id = ? ORDER BY search_time DESC",
                   (message.from_user.id,))
    history = cursor.fetchall()
    if not history:
        await message.reply("🗑️Истории нет!\nСкорее введи свой запрос и заполни эту пустоту!")
    else:
        response = "*История поиска:* \n\n"
        for film_title, search_time in history:
            dt = datetime.strptime(search_time, "%Y-%m-%d %H:%M:%S")
            response += f"🗓️ {dt.strftime('%d.%m.%Y')} ⏰ {dt.strftime('%H:%M')} 🎬{film_title}\n"
        await message.reply(response, parse_mode='Markdown')


@dp.message(Command('stats'))
async def cmd_stats(message: types.Message):
    cursor.execute("SELECT film_title, count FROM stats WHERE user_id = ? ORDER BY count DESC", (message.from_user.id,))
    stats = cursor.fetchall()
    if not stats:
        await message.reply("🗑️Статистики нет!\nСкорее введи свой запрос и заполни эту пустоту!")
    else:
        response = "*Статистика:*\n\n"
        for film_title, count in stats:
            response += f"🍿 {film_title}: *{count}*\n"
        await message.reply(response, parse_mode='Markdown')


@dp.message(Command('clear'))
async def clear(message: types.Message):
    cursor.execute("DELETE FROM search_history WHERE user_id = ?", (message.from_user.id,))
    cursor.execute("DELETE FROM stats WHERE user_id = ?", (message.from_user.id,))
    conn.commit()
    await message.reply("✅ История поиска и статистика успешно очищены")


@dp.message()
async def echo(message: types.Message):
    film_title = message.text
    cursor.execute("INSERT INTO search_history (user_id, film_title) VALUES (?, ?)", (message.from_user.id, film_title))
    conn.commit()
    cursor.execute("SELECT count FROM stats WHERE user_id = ? AND film_title = ?", (message.from_user.id, film_title))
    result = cursor.fetchone()
    if result is None:
        cursor.execute("INSERT INTO stats (user_id, film_title) VALUES (?, ?)", (message.from_user.id, film_title))
    else:
        cursor.execute("UPDATE stats SET count = count + 1 WHERE user_id = ? AND film_title = ?",
                       (message.from_user.id, film_title))
    conn.commit()

    async with aiohttp.ClientSession() as session:
        params = {'apikey': omdb_api_key, 't': film_title}
        async with session.get('http://www.omdbapi.com/', params=params) as resp:
            film_data = await resp.json()
            if film_data['Response'] == 'False':
                headers = {"X-API-KEY": kinopoisk_api_key}
                params = {'query': film_title}
                async with session.get('https://api.kinopoisk.dev/v1.4/movie/search', headers=headers,
                                       params=params) as resp_kinopoisk:
                    kinopoisk_data = await resp_kinopoisk.json()
                    if not kinopoisk_data['docs']:
                        await message.reply("Фильм не найден")
                        return

                    film_data_kinopoisk = kinopoisk_data['docs'][0]
                    await bot.send_photo(chat_id=message.chat.id, photo=film_data_kinopoisk['poster']['url'])

                    genres = [genre['name'] for genre in film_data_kinopoisk['genres']]

                    response_text = f"*Название*: {film_data_kinopoisk['name']}\n"\
                                    f"*Год*: {film_data_kinopoisk['year']}\n"\
                                    f"*Жанры*: {', '.join(genres)}\n" \
                                    f"*Рейтинг кинопоиска*: {film_data_kinopoisk['rating']['kp']}\n\n" \
                                    f"\n*Сюжет*: {film_data_kinopoisk['description']}\n\n" \
                                    f"🍿 *Где посмотреть?*  \n"

                    links = await search_google(f"{film_title} смотреть онлайн бесплатно")

                    for link in links:
                        redirect_link = link['redirect_link']
                        if redirect_link.startswith('https://www.google.ruhttps://'):
                            redirect_link = redirect_link.replace('https://www.google.ru', '', 1)
                        response_text += f"[Смотреть на {link['source']}]({redirect_link})\n"

                    response_text += "\n\n❗️️️️️️️☠️💸*Что делать, если все ссылки заблокированы?*\n" \
                                     "Иногда такое случается (смотреть фильмы на пиратских сайтах плохо, " \
                                     "но именно на них мы и даем вам ссылки в России из-за санкций). " \
                                     "Вы можете включить VPN и посмотреть этот же \
                                     фильм или сериал на платной платформе, " \
                                     "для этого отправьте боту еще один запрос с оригинальным названием фильма" \
                                     "(скопировать можно ниже 👇)\n\n" \
                                     f"*Title:* {film_data_kinopoisk['alternativeName']}"

                    await bot.send_message(chat_id=message.chat.id, text=response_text, parse_mode='Markdown')
                    return

            headers = {
                'x-rapidapi-host': "streaming-availability.p.rapidapi.com",
                'x-rapidapi-key': rapid_api_key
            }

            await bot.send_photo(chat_id=message.chat.id, photo=film_data['Poster'])
            querystring = {"imdb_id": film_data['imdbID']}
            url = "https://streaming-availability.p.rapidapi.com/get"

            async with session.get(url, headers=headers, params=querystring) as resp_stream:
                stream_data = await resp_stream.json()
                if 'result' in stream_data and 'streamingInfo' in stream_data['result'] and 'us' in \
                        stream_data['result']['streamingInfo']:
                    streaming_links_set = set()
                    for stream_info in stream_data['result']['streamingInfo']['us']:
                        streaming_links_set.add(f"[Watch it on: {stream_info['service']}]({stream_info['link']})")
                    streaming_links = "\n".join(list(streaming_links_set)[:min(3, len(streaming_links_set))])
                else:
                    streaming_links = "No streaming information available"

            genres = [genre['name'] for genre in stream_data['result']['genres']]
            response_text = f"*Title:* {stream_data['result']['title']}\n*Year:* {film_data['Year']}\n" \
                            f"*Genres:* {', '.join(genres)}\n" \
                            f"*Rating:* {film_data['imdbRating']}\n" \
                            f"\n*Plot:* {film_data['Plot']}\n" \
                            f"\n\n🍿 *Where to watch?*\n{streaming_links}" \
                            "\n\n❗️️️️️️️☠️*For free version*\n" \
                            "We strongly discourage you from promoting piracy and watching movies for free," \
                            "but we can't forbid it. To get the desired free links, " \
                            "send another request to the bot with the title of the movie in Russian."
            await bot.send_message(chat_id=message.chat.id, text=response_text, parse_mode='Markdown')


@dp.shutdown()
async def shutdown():
    cursor.close()
    conn.close()


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())