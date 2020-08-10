from ananas import PineappleBot, hourly, schedule, reply, html_strip_tags, daily, interval
import logging
import pymysql
from bot_datacenter import *
from bs4 import BeautifulSoup

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class HelloBot(PineappleBot):

    # the main handler for most of bots
    datacenter = None

    def start(self):
        """
        Do somethin when start the bot.
        """
        logging.info('Start hello bot and init mysql connection ...')
        connection = pymysql.connect(host='localhost', user='root',password='',database='mastodon_bot',charset="utf8")
        self.datacenter = BotDataCenter(mastodon=self.mastodon, connection=connection)
    
    def on_notification(self, notif):
        super().on_notification(notif)

        print('收到消息:')
        print(notif)

        logging.info("Got a {} from {} at {}".format(notif["type"], notif["account"]["username"], notif["created_at"]))
        notif_type = notif["type"]
    
    @interval(5)
    def test2(self):
        self.datacenter.check_talks()

    @reply
    def test(self, mention, user):
        """
        Reply for private message.
        """
        logging.info('it aaa')
        print(mention)
        print(user)
        logging.info("Got a mention from {} at {}".format(user["username"], mention["created_at"]))

        # if the notification is direct
        # (private message)
        if mention["visibility"] == "direct":

            # get sender

            # get message
            # soup = BeautifulSoup(mention["content"], "html.parser")
            self.datacenter.start_talk(user, mention)

            # message = soup.find('p').get_text().strip().split(' ')[1:]
            # message = "_".join(message)

            # print('read message {}'.format(message))

            # # check if the sender has saved messages
            # print('conn is ', self.conn)

            # # make response based on the message
            # if (False == bot_datacenter.select_info(self.mastodon, user, message, conn=self.conn)):
            #     bot_datacenter.show_introduction(self.mastodon, user)

