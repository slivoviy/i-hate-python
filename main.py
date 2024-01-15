import news_parser
import schedule
import time
import asyncio
import controller


def main():
    asyncio.run(news_parser.request_news())
    controller.start_bot()
    update_news()


def update_news():
    schedule.every(30).minutes.do(news_parser.update_news)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == '__main__':
    main()

