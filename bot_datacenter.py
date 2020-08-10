from bs4 import BeautifulSoup
import inspect
import datetime
class BotDataCenter(object):

    ACTION_TYPE_POLL = 0
    # ACTION_TYPE_POLL = 0

    # save talk with different users
    # key-value structure
    # key: user_id
    # value:
    # - action: denotes the talk type with the user(e.g. poll)
    # - expired_time: denotes the talk expired time, if talk expired, just remove this talk
    # - data: denotes the details for each action, it would contains different structures 
    #         for different actions
    talks = {}

    # denotes the connection handle to mysql
    # we can read information from database
    connection = None

    # denotes the mastodon object, we need this to send message
    mastodon = None

    def whoami(self):
        return inspect.stack()[1][3]

    def __init__(self, mastodon, connection):
        print('call function {} ...'.format(self.whoami()))
        self.connection = connection
        self.mastodon = mastodon

    def check_talks(self):
        print('call function {} ...'.format(self.whoami()))
        """
        look each talk and reply the answers
        """
        # remove expired talk
        self.clean_expired_talks()

        print('current talks:', self.talks)

        # check polls
        # call the response function if poll was voted
        talking_user_ids = list(self.talks.keys())
        for user_id in talking_user_ids:
            talk = self.talks[user_id]
            action = talk['action']

            if action is self.ACTION_TYPE_POLL:
                # get parameters from talk
                poll_id = talk['data']['post']['poll']['id']
                response_function = talk['response_function']

                # read user by user_id
                user = self.mastodon.account(user_id)
                print('get user :', user)

                # read poll
                target_poll = self.mastodon.poll(poll_id)

                # print voted result
                print('-----------current poll is:----------')
                print(target_poll)
                selected_option = 'None'
                for poll_option in target_poll["options"]:
                    if poll_option["votes_count"] > 0:
                        selected_option = poll_option["title"]
                        break

                # if no voted, just continue
                if selected_option is None:
                    continue

                # call response function
                print('select {}'.format(selected_option))
                data = {
                    'post': talk['data']['post'],
                    'selected_option': selected_option
                }
                getattr(self, response_function)(user=user, data=data, is_response=True)

        return None
    
    def start_talk(self, user, mention):
        print('call function {} ...'.format(self.whoami()))
        """
        if there are no continue talk, just start a new talk
        if there is a talk for the current user, just do something depends on the action
        """

        # remove expired talk
        self.clean_expired_talks()

        # get user id
        user_id = user['id']

        if user_id in self.talks:
            # do something follow the previous
            current_talk = self.talks[user_id]
            action = current_talk['action']

            # if current talk is poll, all we need answer should be a selection
            # but here is a talk, we just need stop the poll, and start from a new talk
            if action is self.ACTION_TYPE_POLL:
                self.show_introduction(user)
            else:
                # TODO: search course info
                pass
        else:
            # start talking from the question root
            # send a poll
            # record it to the talks
            self.show_introduction(user)
        return None

    # TODO: remove expired talk
    def clean_expired_talks(self):
        print('call function {} ...'.format(self.whoami()))
        pass
    # ------------------ talk detail functions --------------
    # all the talk detail functions paras should be: user, data=None, is_response=False
    # =======================================================
    def select_info(self, user, message, conn=None):
        print('call function {} ...'.format(self.whoami()))
        if message == 'hello':
            show_introduction(self, user)
        elif message == 'school_info':
            school_info(self, user, conn)
        elif message == 'school_official_website':
            school_official_website()
        elif message == 'school_contact_info':
            school_contact_info()
        elif message == 'school_newbee_info':
            school_newbee_info()
        elif message == 'school_f_and_q':
            school_f_and_q()
        elif message == 'class_info':
            class_info()
        elif message == 'meeting_book':
            meeting_book()
        elif message == 'teach_feedback':
            teach_feedback()
        elif message == 'question_history':
            question_history()
        elif message == 'other_questions':
            other_questions()
        else:
            # if don't understand what he/she say, just display function introduction message
            # show_introduction(self, user)
            return False
        return True

    def status_post(self, user, message, poll_options = None):
        print('call function {} ...'.format(self.whoami()))
        """
        Send only message
        """
        full_message = "@{} ".format(user["acct"]) + message

        # make poll
        poll = None
        if poll_options != None:
            poll = self.mastodon.make_poll(options=poll_options, expires_in=5000)

        print('status post :', full_message)

        return self.mastodon.status_post(status=full_message, visibility="direct", poll=poll)

    def send_poll(self, user, message, poll_configs):
        print('call function {} ...'.format(self.whoami()))
        """
        send a poll and update the talk record
        """
        # make poll options
        poll_options = []
        for option, response_function, parameters in poll_configs:
            poll_options.append(option)
        
        # send poll
        post = self.status_post(user, message, poll_options)

        # update talk record
        talk = {
            'action': self.ACTION_TYPE_POLL,
            'data': {
                'post': post
            },
            'expired': (datetime.datetime.now()+datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            'response_function': 'show_introduction',
        }

        self.talks[user['id']] = talk
        return None

    def show_introduction(self, user, data=None, is_response=False):
        print('call function {} ...'.format(self.whoami()))
        """
        Introduce the bot functions.
        """
        poll_configs = [
            ('School Info', 'school_info', None),
            ('School Contact Info', 'school_contact_info', None),
            ('Newbee Info', 'school_newbee_info', None),
            ('F & Q', 'school_f_and_q', None),
        ]

        if is_response == True:
            # get response from data
            selected_option = data['selected_option']
            # response
            for option, response_function, parameters in poll_configs:
                if selected_option == option:
                    # call the function
                    getattr(self, response_function)(user=user, data=data, is_response=True)
                    # clean talk record
                    self.talks.pop(user['id'])
                    break
            
            # error
            print('response to show introduction error! info:')
            print(data)

        else:
            message = "Hello, I'm School Bot, nice to meet you! What do want to know?"
            print(message)
            self.send_poll(user, message, poll_configs)

        return None

    def school_info(self, user, data=None, is_response=False):
        print('call function {} ...'.format(self.whoami()))
        """
        Display school info, let students choose options
        """

        # read information websites
        school_info_dict = {}
        cursor = self.connection.cursor()
        sql = "SELECT id, info_name, info_value from school_info_schoolinfo WHERE deleted_at is NULL;"
        cursor.execute(sql)
        result = cursor.fetchall()
        for id, info_name, info_value in result:
            print("info: id is {},name in {}，value is {}".format(id, info_name, info_value))
            school_info_dict[info_name] = info_value

        message = "What do you want to know about school? You can check the following links:"
        message += "\n1. school official website: "+school_info_dict["school_official_website"]
        message += "\n2. school contact info: "+school_info_dict["school_contact_info"]
        message += "\n3. school newbee info: "+school_info_dict["school_newbie_info"]
        message += "\n4. school F&Q: "+school_info_dict["school_f_and_q"]
        return self.status_post(user, message)

    def school_official_website(self, user, data=None, is_response=False):
        print('call function {} ...'.format(self.whoami()))
        """
        Display info, let students choose options
        """
        message = "This function is developing"
        print(message)

    def school_contact_info(self, user, data=None, is_response=False):
        print('call function {} ...'.format(self.whoami()))
        """
        Display info, let students choose options
        """
        message = "This function is developing"
        print(message)

    def school_newbee_info(self, user, data=None, is_response=False):
        print('call function {} ...'.format(self.whoami()))
        """
        Display info, let students choose options
        """
        message = "This function is developing"
        print(message)

    def school_f_and_q(self, user, data=None, is_response=False):
        print('call function {} ...'.format(self.whoami()))
        """
        Display info, let students choose options
        """
        message = "This function is developing"
        print(message)






    def class_info(self, user, data=None, is_response=False):
        print('call function {} ...'.format(self.whoami()))
        """
        Display info, let students choose options
        """
        message = "This function is developing"
        print(message)

    def meeting_book(self, user, data=None, is_response=False):
        print('call function {} ...'.format(self.whoami()))
        """
        Display info, let students choose options
        """
        message = "This function is developing"
        print(message)

    def teach_feedback(self, user, data=None, is_response=False):
        print('call function {} ...'.format(self.whoami()))
        """
        Display info, let students choose options
        """
        message = "This function is developing"
        print(message)

    def question_history(self, user, data=None, is_response=False):
        print('call function {} ...'.format(self.whoami()))
        """
        Display info, let students choose options
        """
        message = "This function is developing"
        print(message)

    def other_questions(self, user, data=None, is_response=False):
        print('call function {} ...'.format(self.whoami()))
        """
        Display info, let students choose options
        """
        message = "This function is developing"
        print(message)