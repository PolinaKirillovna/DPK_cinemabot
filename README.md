# DPK cinemabot Telegram Bot

## Описание

[DPK cinemabot](https://t.me/dpk_cinema_bot) - это асинхронный телеграм-бот, который поможет вам быстро получить краткое описание любого фильма, сериала или мультфильма, а также предоставит несколько ссылок для просмотра. 

## Возможности

- Поиск информации о фильме или сериале по названию
- Вывод истории запросов
- Отображение статистики предложенных фильмов
- Очистка истории и статистики

При поиске вы получите следующую информацию:
- Постер
- Название
- Рейтинг
- Год выпуска
- Жанры
- Сюжет

## Команды

- /start - описание бота
- /help - помощь 
- /history - история запросов
- /stats - статистика предложенных фильмов
- /clear - очищение истории и статистики

## Технологии

Бот написан на Python с использованием следующих библиотек:

- [asyncio](https://docs.python.org/3/library/asyncio.html)
- [os](https://docs.python.org/3/library/os.html)
- [sqlite3](https://docs.python.org/3/library/sqlite3.html)
- [datetime](https://docs.python.org/3/library/datetime.html)
- [aiohttp](https://docs.aiohttp.org/en/stable/)
- [GoogleSearch (serpapi)](https://serpapi.com)
- [aiogram](https://docs.aiogram.dev/en/latest/)
- [dotenv](https://pypi.org/project/python-dotenv/)

Также в работе бота используются следующие API:

- [Kinopoisk API](https://kinopoisk.dev)
- [OMDB API](http://www.omdbapi.com)
- [SerpApi](https://serpapi.com)
- [Streaming Availability API](https://www.movieofthenight.com/about/api)

## Обратная связь

Если у вас остались вопросы, вы можете написать администратору: [@maki_who](https://t.me/maki_who)
