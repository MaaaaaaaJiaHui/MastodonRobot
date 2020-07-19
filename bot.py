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
            if message == 'hello':
                bot_datacenter.show_introduction(self.mastodon, user)

            elif message == 'school_info':
                bot_datacenter.school_info(self.mastodon, user)
            elif message == 'school_official_website':
                bot_datacenter.school_official_website()
            elif message == 'school_info':
                bot_datacenter.school_info()
            elif message == 'school_official_website':
                bot_datacenter.school_official_website()
            elif message == 'school_contact_info':
                bot_datacenter.school_contact_info()
            elif message == 'school_newbee_info':
                bot_datacenter.school_newbee_info()
            elif message == 'school_f_and_q':
                bot_datacenter.school_f_and_q()
            elif message == 'class_info':
                bot_datacenter.class_info()
            elif message == 'meeting_book':
                bot_datacenter.meeting_book()
            elif message == 'teach_feedback':
                bot_datacenter.teach_feedback()
            elif message == 'question_history':
                bot_datacenter.question_history()
            elif message == 'other_questions':
                bot_datacenter.other_questions()
            else:
                # if don't understand what he/she say, just display function introduction message
                bot_datacenter.show_introduction(self.mastodon, user)

