from ananas import PineappleBot, hourly, schedule, reply, html_strip_tags, daily, interval
import logging
import pymysql
import importlib
import traceback
from bs4 import BeautifulSoup
import bot_datacenter

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class HelloBot(PineappleBot):

    # the main handler for most of bots
    datacenter = None

    # the connection to database
    connection = None

    is_error = False

    def start(self):
        """
        Do somethin when start the bot.
        """
        logging.info('Start hello bot and init mysql connection ...')
        self.connection = pymysql.connect(host='localhost', user='root',password='',database='mastodon_bot',charset="utf8")

        self.datacenter = bot_datacenter.BotDataCenter(mastodon=self.mastodon, connection=self.connection)
    
    def on_notification(self, notif):
        super().on_notification(notif)

        # print('收到消息:')
        # print(notif)

        # logging.info("Got a {} from {} at {}".format(notif["type"], notif["account"]["username"], notif["created_at"]))
        # notif_type = notif["type"]
    
    @interval(5)
    def test2(self):
        try:
            self.datacenter.check_talks()
            if self.is_error == True:
                raise Exception('error')
        except Exception as e:
            print("============================")
            traceback.print_exc()
            print("============================")
            input("Program stopped because of exceptions. Input anything to restart after bug fixed: ")
            self.is_error = False
            # re import
            importlib.reload(bot_datacenter)
            old_talks = self.datacenter.get_talks()
            self.datacenter = bot_datacenter.BotDataCenter(mastodon=self.mastodon, connection=self.connection, talks=old_talks)


    @reply
    def test(self, mention, user):
        """
        Reply for private message.
        """
        logging.info("Got a mention from {} at {}".format(user["username"], mention["created_at"]))

        # if the notification is direct
        # (private message)
        if mention["visibility"] == "direct":

            try:
                self.datacenter.start_talk(user, mention)
            except Exception as e:
                self.is_error = True
                print("============================")
                traceback.print_exc()
                print("============================")
                input("Program stopped because of exceptions. Input anything to restart after bug fixed: ")
                # re import
                importlib.reload(bot_datacenter)
                old_talks = self.datacenter.get_talks()
                self.datacenter = bot_datacenter.BotDataCenter(mastodon=self.mastodon, connection=self.connection, talks=old_talks)

