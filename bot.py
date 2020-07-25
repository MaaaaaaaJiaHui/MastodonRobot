from ananas import PineappleBot, hourly, schedule, reply, html_strip_tags, daily, interval
import logging
import bot_datacenter
from bs4 import BeautifulSoup

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class HelloBot(PineappleBot):

    def start(self):
        """
        Do somethin when start the bot.
        """
        logging.info('Start hello bot ...')
    
    def on_notification(self, notif):
        super().on_notification(notif)

        print('收到消息:')
        print(notif)

        logging.info("Got a {} from {} at {}".format(notif["type"], notif["account"]["username"], notif["created_at"]))
        notif_type = notif["type"]

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
            soup = BeautifulSoup(mention["content"], "html.parser")
            message = soup.find('p').get_text().strip().split(' ')[1:]
            message = "_".join(message)
            print('read message {}'.format(message))

            # check if the sender has saved messages

            # make response based on the message
            if (False == bot_datacenter.select_info(self.mastodon, user, message)):
                bot_datacenter.show_introduction(self.mastodon, user)

