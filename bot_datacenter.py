from bs4 import BeautifulSoup
import inspect
import datetime

class BotDataCenter(object):

    ACTION_TYPE_POLL = 0
    ACTION_TYPE_QUERY = 1

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

    def get_talks(self):
        return self.talks

    def whoami(self):
        return inspect.stack()[1][3]

    def __init__(self, mastodon, connection, talks={}):
        print('call function {} ...'.format(self.whoami()))
        self.connection = connection
        self.mastodon = mastodon
        self.talks = talks

    def check_talks(self):
        # print('call function {} ...'.format(self.whoami()))
        """
        look each talk and reply the answers
        """
        # remove expired talk
        self.clean_expired_talks()

        if len(self.talks) > 0:
            print('current exists {} talks.'.format(len(self.talks)))

        # check polls
        # call the response function if poll was voted
        talking_user_ids = list(self.talks.keys())
        for user_id in talking_user_ids:
            talk = self.talks[user_id]
            action = talk['action']

            if action in [self.ACTION_TYPE_POLL, self.ACTION_TYPE_QUERY]:
                # get parameters from talk
                poll_id = talk['data']['post']['poll']['id']
                response_function = talk['response_function']

                # read user by user_id
                user = self.mastodon.account(user_id)

                # read poll
                target_poll = self.mastodon.poll(poll_id)

                # print voted result
                selected_option = None
                for poll_option in target_poll["options"]:
                    if poll_option["votes_count"] > 0:
                        selected_option = poll_option["title"]
                        break

                # if no voted, just continue
                if selected_option is None:
                    continue

                print('get user(id:{}) {}'.format(str(user['id']), user['username']))
                print('talk action:', action)
                print('talk response function:', response_function)

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
            elif action is self.ACTION_TYPE_QUERY:
                response_function = current_talk['response_function']
                getattr(self, response_function)(user=user,data={'mention':mention},is_response=True)
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
        # print('call function {} ...'.format(self.whoami()))
        pass
    
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

    def send_poll(self, user, message, poll_configs, response_function, keep_current_talk=False):
        print('call function {} ...'.format(self.whoami()))
        """
        send a poll and update the talk record
        """
        # make poll options
        poll_options = []
        for option, _, parameters in poll_configs:
            poll_options.append(option)
        
        # send poll
        post = self.status_post(user, message, poll_options)

        # update talk record
        if keep_current_talk == True:
            self.talks[user['id']]['data']['post'] = post
            self.talks[user['id']]['expired'] = (datetime.datetime.now()+datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        else:
            talk = {
                'action': self.ACTION_TYPE_POLL,
                'data': {
                    'post': post
                },
                'expired': (datetime.datetime.now()+datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
                'response_function': response_function,
            }
            self.talks[user['id']] = talk
        return None
    
    def start_querying(self, user, message, response_function, keep_current_talk=False):
        """
        start querying something by continue asking
        we would add a exit option for end this asking
        """
        print('call function {} ...'.format(self.whoami()))
        """
        send a poll and update the talk record
        """

        # adding exit option
        poll_configs = [
            ('Quit searching.', 'quit_searching', None),
            ('Back to last question.', 'show_introduction', None),
        ]
        message += "(If you don't want to end the searching, just select the following option.)"
        print('query:', message)

        # make poll options
        poll_options = []
        for option, _, _ in poll_configs:
            poll_options.append(option)
        
        # send poll
        post = self.status_post(user, message, poll_options)

        # update talk record
        if keep_current_talk == True:
            self.talks[user['id']]['data']['post'] = post
            self.talks[user['id']]['expired'] = (datetime.datetime.now()+datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        else:
            talk = {
                'action': self.ACTION_TYPE_QUERY,
                'data': {
                    'post': post
                },
                'expired': (datetime.datetime.now()+datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
                'response_function': response_function,
            }
            self.talks[user['id']] = talk
        return None
    
    def quit_searching(self, user, data=None, is_response=False):
        """
        let user exit from current asking
        just remove current talk
        """
        if is_response == True:
            self.talks.pop(user['id'])
            print('quit from current talk!')
        return None

    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            pass
        return False

    # ------------------ talk detail functions --------------
    # all the talk detail functions paras should be: user, data=None, is_response=False
    # =======================================================
    def show_introduction(self, user, data=None, is_response=False):
        print('call function {} ...'.format(self.whoami()))
        """
        Introduce the bot functions.
        """
        poll_configs = [
            ('School Info', 'school_info', None),
            ('Course Info', 'class_info', None),
            ('Feedback', 'feedback', None),
            ('Make Appointment', 'make_appointment', None),
        ]

        if is_response == True:
            # get response from data
            selected_option = data['selected_option']
            # response
            for option, response_function, parameters in poll_configs:
                if selected_option == option:
                    # clean talk record
                    self.talks.pop(user['id'])

                    # call the function
                    getattr(self, response_function)(user=user, data=data, is_response=False)
                    return None
            
            # error
            print('response to show introduction error! info:')
            print(data['selected_option'])

        else:
            message = "Hello, I'm School Bot, nice to meet you! What do want to know?"
            print(message)
            self.send_poll(user, message, poll_configs, 'show_introduction')

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


    def class_info(self, user, data=None, is_response=False):
        print('call function {} ...'.format(self.whoami()))
        """
        Display info, let students choose options
        """
        poll_configs = [
            ('Recent Exam Info', 'get_recent_exam_info', None),
            ('Recent Assignment Info', 'get_recent_assignment_info', None),
            ('Rate & Suggestion', 'rate_and_suggestion', None),
        ]

        # check current course_id and grade
        course_code = None
        grade = None
        course_id = None

        if user['id'] in self.talks:
            talk = self.talks[user['id']]
            if 'course_code' in talk['data']:
                course_code = talk['data']['course_code']
            if 'grade' in talk['data']:
                grade = talk['data']['grade']
            if 'course_id' in talk['data']:
                course_id = int(talk['data']['course_id'])

        if is_response == True and 'mention' in data and (course_code is None or grade is None):

            # get response from data
            mention = data['mention']
            soup = BeautifulSoup(mention["content"], "html.parser")
            received_message = soup.find('p').get_text().strip()

            print('reading answers for class info, in current talk, course code is {}, grade is {}, course id is {}'.format(course_code, grade, str(course_id)))

            if course_code is None:
                print('reading answers as course code')

                # get course code from message
                # search course code in database
                words = received_message.split()
                for word in words:
                    # check if word is @xxxxx
                    if word[0] == '@':
                        continue
    
                    cursor = self.connection.cursor()
                    sql = "SELECT id, name from school_info_coursetemplate WHERE course_code = '{}' AND deleted_at is NULL;".format(word)
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    for id, name in result:
                        print("find course info: id is {}, name is {}, course code is {}".format(id, name, word))
                        course_code = word
                        break
                    if course_code != None:
                        break

                # find, save it to talk data
                # ask for grade
                if course_code != None:
                    talk['data']['course_code'] = course_code
                    print('change talk:', self.talks[user['id']])

                    message = "For searching what you want, could you tell me what grade you want ?"
                    self.start_querying(user, message, 'class_info', keep_current_talk=True)

                    # debug print talk
                    talk = self.talks[user['id']]
                    course_code = None
                    grade = None
                    course_id = None

                    if 'course_code' in talk['data']:
                        course_code = talk['data']['course_code']
                    if 'grade' in talk['data']:
                        grade = talk['data']['grade']
                    if 'course_id' in talk['data']:
                        course_id = int(talk['data']['course_id'])

                    print('reading answers for class info, in current talk, course code is {}, grade is {}, course id is {}'.format(course_code, grade, str(course_id)))
                    print('change talk:', self.talks[user['id']])
                    return None

                # not found, ask for course code again
                message = "Sorry we can't find any course by your input {}, could you please try again ?".format(received_message)
                self.start_querying(user, message, 'class_info')
                return None
            elif grade is None:
                print('reading answers as course code')

                # get grade from message
                # search grade in database
                course_id = None
                words = received_message.split()
                for word in words:
                    # check if word is @xxxxx
                    if word[0] == '@':
                        continue
    
                    cursor = self.connection.cursor()
                    sql = "SELECT id from school_info_course WHERE course_template_id IN (SELECT id from school_info_coursetemplate WHERE course_code = '{}' AND deleted_at is NULL) AND grade = '{}' AND deleted_at is NULL;".format(course_code, word)
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    for id in result:
                        id = id[0]
                        print("find course info: id is {}".format(id))
                        grade = word
                        course_id = id
                        break
                    if grade != None:
                        break

                # find, save it to talk data
                # ask for polls
                if grade != None:
                    self.talks[user['id']]['data']['grade'] = grade
                    self.talks[user['id']]['data']['course_id'] = course_id

                    message = "What do you want to know about {}({}), please select following option.".format(course_code, grade)
                    self.send_poll(user, message, poll_configs, 'class_info', keep_current_talk=True)
                    return None

                # not found, ask for course id again
                message = "For searching what you want, could you tell me what grade you want ?"
                message = "Sorry we can't find any course({}) by grade in your input {}, could you please try again ?".format(course_code, received_message)

                self.start_querying(user, message, 'class_info', keep_current_talk=True)
                return None
            else:
                print('this input is illegal!')
                return None
        elif is_response is True and 'selected_option' in data and course_code != None and grade != None:
            # get selection
            selected_option = data['selected_option']

            print('now we know course code and grade, reading selected option {} query'.format(selected_option))

            # response
            for option, response_function, parameters in poll_configs:
                if selected_option == option:

                    self.talks[user['id']]['data']['poll_configs'] = poll_configs

                    # call the function
                    getattr(self, response_function)(user=user, data=data, is_response=True)
                    return None

            # error
            print('this selected option is illegal!')
            return None

        else:
            message = "For searching what you want, could you tell me what course code of course you want ?"
            self.start_querying(user, message, 'class_info')

        return None

    def get_recent_exam_info(self, user, data=None, is_response=False):
        # get course_id from data
        talk = self.talks[user['id']]
        course_id = talk['data']['course_id']
        course_code = talk['data']['course_code']
        grade = talk['data']['grade']
        poll_configs = talk['data']['poll_configs']

        cursor = self.connection.cursor()
        sql = "SELECT name, description,exam_at, exam_type, location, url from school_info_exam WHERE course_id = {} AND exam_at >= '{}' AND deleted_at is NULL ORDER BY exam_at ASC;".format(course_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print('SQL:{}'.format(sql))
        cursor.execute(sql)
        result = cursor.fetchone()
        print('result:',result)

        if result is None:
            # display result and ask again
            message = "Sorry, not found {}({}) recent exam.".format(course_code, grade)
            message += "\nWhat do you want to know about {}({}), please select following option.".format(course_code, grade)
            self.send_poll(user, message, poll_configs, 'class_info', keep_current_talk=True)
        else:
            # display result and ask again
            name, description,exam_at, exam_type, location, url = result
            print("find recent exam is {} {} {} {} {} {}".format(name, description,exam_at, exam_type, location, url))

            message = "The recent exam:"
            message += "\n{}".format(name)
            message += "\n{}".format(description)
            message += "\ntime: {}".format(exam_at)

            if exam_type == 0:
                message += "\ntype: offline"
                message += "\nlocation: {}".format(location)
            else:
                message += "\ntype: online"
            message += "\nmore info: {}".format(url)
            message += "\n"
            message += "\nWhat do you want to know about {}({}), please select following option.".format(course_code, grade)
            self.send_poll(user, message, poll_configs, 'class_info', keep_current_talk=True)

        return None
    def get_recent_assignment_info(self, user, data=None, is_response=False):
        """
        display recent assignment info and send poll
        """
        # get course_id from data
        talk = self.talks[user['id']]
        course_id = talk['data']['course_id']
        course_code = talk['data']['course_code']
        grade = talk['data']['grade']
        poll_configs = talk['data']['poll_configs']

        cursor = self.connection.cursor()
        sql = "SELECT name, description, deadline_at, url from school_info_assignment WHERE course_id = {} AND deadline_at >= '{}' AND deleted_at is NULL ORDER BY deadline_at ASC;".format(course_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print('SQL:{}'.format(sql))
        cursor.execute(sql)
        result = cursor.fetchone()
        print('result:',result)

        if result is None:
            # display result and ask again
            message = "Sorry, not found {}({}) recent assignment.".format(course_code, grade)
            message += "\nWhat do you want to know about {}({}), please select following option.".format(course_code, grade)
            self.send_poll(user, message, poll_configs, 'class_info', keep_current_talk=True)
        else:
            # display result and ask again
            name, description, deadline_at, url = result
            print("find recent assignment is {} {} {} {}".format(name, description, deadline_at, url))

            message = "The recent assignment:"
            message += "\n{}".format(name)
            message += "\n{}".format(description)
            message += "\ndeadline: {}".format(deadline_at)
            message += "\nmore info: {}".format(url)
            message += "\n"
            message += "\nWhat do you want to know about {}({}), please select following option.".format(course_code, grade)
            self.send_poll(user, message, poll_configs, 'class_info', keep_current_talk=True)

        return None
    def rate_and_suggestion(self, user, data=None, is_response=False):
        pass
    
    def make_appointment(self, user, data=None, is_response=False):
        print('call function {} ...'.format(self.whoami()))
        """
        Ask for teaching assistant's name and display the contact info.
        """
        # check current course_id and grade
        teaching_assistant_name = None

        if is_response == True and 'mention' in data and teaching_assistant_name is None:

            # get response from data
            mention = data['mention']
            soup = BeautifulSoup(mention["content"], "html.parser")
            received_message = soup.find('p').get_text().strip()

            print('reading answers for making appointment ...')

            # get course code from message
            # search course code in database
            words = received_message.split()
            for word in list(words):
                # check if word is @xxxxx
                if word[0] == '@':
                    words.remove(word)
            
            input_user_name = " ".join(words)
            search_name = "%".join(words)

            cursor = self.connection.cursor()
            sql = "SELECT user_name, email from school_info_teachingassistant WHERE user_name like '%{}%' AND deleted_at is NULL;".format(search_name)
            cursor.execute(sql)
            result = cursor.fetchone()
            
            if result is None:
                # not found, ask for name again
                message = "Sorry we can't find any teaching assistant who's name is {}, could you please try again ?".format(input_user_name)
                self.start_querying(user, message, 'make_appointment', keep_current_talk=True)
                return None
            else:
                # clean current talk
                self.talks.pop(user['id'])
                # display the info
                message = "{} email is:".format(result[0])
                message += "\n{}".format(result[1])
                return self.status_post(user, message)
        else:
            message = "Please tell me the teaching assistant name who you want to make an appointment."
            self.start_querying(user, message, 'make_appointment')

        return None

    def feedback(self, user, data=None, is_response=False):
        print('call function {} ...'.format(self.whoami()))
        """
        Display info, let students choose options
        """
        poll_configs = [
            ('Teaching Evaluate', 'teach_feedback', None),
            ('Other Question', 'other_questions', None),
        ]

        if is_response == True:
            # get response from data
            selected_option = data['selected_option']
            # response
            for option, response_function, parameters in poll_configs:
                if selected_option == option:
                    # clean talk record
                    self.talks.pop(user['id'])

                    # call the function
                    getattr(self, response_function)(user=user, data=data)
                    return None

            # error
            print('response to feedback error! info:')
            print(data['selected_option'])
        else:
            message = "You can select teaching evaluate and scoring for the class and make some suggestions!"
            message += "\nIf you have some questions, but just can't find answer by our bot, you can select other questions option and tell us."
            self.send_poll(user, message, poll_configs, 'feedback')

        return None

    def teach_feedback(self, user, data=None, is_response=False):
        print('call function {} ...'.format(self.whoami()))
        """
        1. Ask for scoring from 1~10.
        2. Ask for suggestion.
        """
        # read current course_id and grade
        course_code = None
        grade = None
        course_id = None
        score = None
        suggestion = None
        if user['id'] in self.talks:
            talk = self.talks[user['id']]
            if 'course_code' in talk['data']:
                course_code = talk['data']['course_code']
            if 'grade' in talk['data']:
                grade = talk['data']['grade']
            if 'course_id' in talk['data']:
                course_id = int(talk['data']['course_id'])
            if 'score' in talk['data']:
                score = int(talk['data']['score'])
            if 'suggestion' in talk['data']:
                suggestion = talk['data']['suggestion']

        if is_response == True and 'mention' in data and (course_code is None or grade is None or course_id is None or score is None or suggestion is None):
            # get response from data
            mention = data['mention']
            soup = BeautifulSoup(mention["content"], "html.parser")
            received_message = soup.find('p').get_text().strip()

            print('reading answers for teaching feedback, in current talk, course code is {}, grade is {}, course id is {}'.format(course_code, grade, str(course_id)))

            if course_code is None:
                print('reading answers as course code')

                # get course code from message
                # search course code in database
                words = received_message.split()
                for word in words:
                    # check if word is @xxxxx
                    if word[0] == '@':
                        continue
    
                    cursor = self.connection.cursor()
                    sql = "SELECT id, name from school_info_coursetemplate WHERE course_code = '{}' AND deleted_at is NULL;".format(word)
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    for id, name in result:
                        print("find course info: id is {}, name is {}, course code is {}".format(id, name, word))
                        course_code = word
                        break
                    if course_code != None:
                        break

                # find, save it to talk data
                # ask for grade
                if course_code != None:
                    talk['data']['course_code'] = course_code
                    print('change talk:', self.talks[user['id']])

                    message = "Please relying grade."
                    self.start_querying(user, message, 'teach_feedback', keep_current_talk=True)
                    return None

                # not found, ask for course code again
                message = "Sorry we can't find any course by your input {}, could you please try again ?".format(received_message)
                self.start_querying(user, message, 'teach_feedback', keep_current_talk=True)
                return None
            elif grade is None:
                print('reading answers as course code')

                # get grade from message
                # search grade in database
                course_id = None
                words = received_message.split()
                for word in words:
                    # check if word is @xxxxx
                    if word[0] == '@':
                        continue
    
                    cursor = self.connection.cursor()
                    sql = "SELECT id from school_info_course WHERE course_template_id IN (SELECT id from school_info_coursetemplate WHERE course_code = '{}' AND deleted_at is NULL) AND grade = '{}' AND deleted_at is NULL;".format(course_code, word)
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    for id in result:
                        id = id[0]
                        print("find course info: id is {}".format(id))
                        grade = word
                        course_id = id
                        break
                    if grade != None:
                        break

                # find, save it to talk data
                # ask for polls
                if grade != None:
                    self.talks[user['id']]['data']['grade'] = grade
                    self.talks[user['id']]['data']['course_id'] = course_id

                    message = "Please scoring {}({}) from 0~10.".format(course_code, grade)
                    self.start_querying(user, message, 'teach_feedback', keep_current_talk=True)
                    return None

                # not found, ask for course id again
                message = "Sorry we can't find any course({}) by grade in your input {}, could you please try again ?".format(course_code, received_message)

                self.start_querying(user, message, 'teach_feedback', keep_current_talk=True)
                return None
            elif score is None:
                print('reading answers as score')

                # get score from message
                score = None
                words = received_message.split()
                for word in list(words):
                    # check if word is @xxxxx
                    if word[0] == '@':
                        words.remove(word)
                score = int("".join(words))

                # check score whether is correct
                if score < 0 or score > 10:
                    message = "Score must be 0~10 number, please try again."
                    self.start_querying(user, message, 'teach_feedback', keep_current_talk=True)
                    return None
                
                # save score
                self.talks[user['id']]['data']['score'] = score

                message = "If you have any suggestions, you can rely me. If not, just rely -1."
                self.start_querying(user, message, 'teach_feedback', keep_current_talk=True)
            
            elif suggestion is None:
                print('reading answers as suggestion')

                # get suggestion from message
                suggestion = None
                words = received_message.split()
                for word in list(words):
                    # check if word is @xxxxx
                    if word[0] == '@':
                        words.remove(word)
                suggestion = " ".join(words)

                # check suggestion whether is correct
                if suggestion == '-1':
                    suggestion = ''

                # save result to db
                now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor = self.connection.cursor()
                sql = "INSERT INTO `school_info_score` (`id`, `created_at`, `updated_at`, `deleted_at`, `user_id`, `score`, `suggestion`, `course_id`) VALUES (NULL, '{}', '{}', NULL, '{}', '{}', '{}', '{}');".format(now_time, now_time, user['id'], score, suggestion, course_id)
                cursor.execute(sql)

                # clean current talk
                self.talks.pop(user['id'])
                # display the info
                message = "Submit success! Thank for your feedback very much :)"
                return self.status_post(user, message)

            else:
                print('this input is illegal!')
                self.start_querying(user, message, 'teach_feedback', keep_current_talk=True)
                return None

        else:
            message = "Please tell me which course you want to scoring by relying the course code."
            self.start_querying(user, message, 'teach_feedback')

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
        Ask for record new questions.
        """

        if is_response == True and 'mention' in data:

            # get response from data
            mention = data['mention']
            soup = BeautifulSoup(mention["content"], "html.parser")
            received_message = soup.find('p').get_text().strip()

            print('reading question which we need to save ...')

            # get course code from message
            # search course code in database
            words = received_message.split()
            for word in list(words):
                # check if word is @xxxxx
                if word[0] == '@':
                    words.remove(word)

            question = " ".join(words)
            now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor = self.connection.cursor()
            sql = "INSERT INTO `school_info_question` (`id`, `created_at`, `updated_at`, `deleted_at`, `user_id`, `user_name`, `question_content`) VALUES (NULL, '{}', '{}', NULL, {}, '{}', '{}');".format(now_time, now_time, user['id'], user['username'], question)
            cursor.execute(sql)

            # clean current talk
            self.talks.pop(user['id'])
            # display the info
            message = "Submit success! Thank for your feedback very much :)"
            return self.status_post(user, message)
        else:
            message = "Please input your question, we would answer it later."
            self.start_querying(user, message, 'other_questions')

        return None
