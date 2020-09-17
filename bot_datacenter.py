from bs4 import BeautifulSoup
import inspect
import datetime

class BotDataCenter(object):

    ACTION_TYPE_POLL = 0
    ACTION_TYPE_QUERY = 1

    QUERY_HISTORY_SCHOOL_INFO = 'School Info'
    QUERY_HISTORY_ASSIGNMENT_INFO = 'Assignment Info'
    QUERY_HISTORY_EXAM_INFO = 'Exam Info'
    QUERY_HISTORY_TEACHING_ASSISTANT_INFO = 'Teaching assistant Info'

    SPECIAL_SELECTION_QUIT_SEARCHING = 'Quit searching.'
    SPECIAL_SELECTION_BACK_TO_ROOT = 'Back to First Question.'

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
        self.connection = connection
        self.mastodon = mastodon
        self.talks = talks

    def check_talks(self):
        """
        look each talk and reply the answers
        """
        # remove expired talk
        self.clean_expired_talks()

        # if len(self.talks) > 0:

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

                selected_option = None
                for poll_option in target_poll["options"]:
                    if poll_option["votes_count"] > 0:
                        selected_option = poll_option["title"]
                        break

                # if no voted, just continue
                if selected_option is None:
                    continue


                # call response function

                # handle special selection
                if selected_option == self.SPECIAL_SELECTION_QUIT_SEARCHING:
                    self.talks.pop(user['id'])
                    self.quit_searching(user)
                    return None
                if selected_option == self.SPECIAL_SELECTION_BACK_TO_ROOT:
                    self.talks.pop(user['id'])
                    self.show_introduction(user)
                    return None

                    
                data = {
                    'post': talk['data']['post'],
                    'selected_option': selected_option
                }
                result = getattr(self, response_function)(user=user, data=data, is_response=True)
                self.call_the_function_by_result(result)

        return None
    
    def start_talk(self, user, mention):
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
                self.quit_searching(user)
                result = self.show_introduction(user)
                self.call_the_function_by_result(result)
            elif action is self.ACTION_TYPE_QUERY:
                response_function = current_talk['response_function']
                result = getattr(self, response_function)(user=user,data={'mention':mention},is_response=True)
                self.call_the_function_by_result(result)
            else:
                # TODO: search course info
                pass
        else:
            # start talking from the question root
            # send a poll
            # record it to the talks
            result = self.show_introduction(user)
            self.call_the_function_by_result(result)
        return None

    def call_the_function_by_result(self, result):
        while True:
            response_function = result['response_function']
            parameters = result['parameters']

            # if the call function is status post, just break
            # if the call function is send poll, just break
            # if the call function is start querying, just break
            # if the call function is quit searching, just break
            # else, continue
            if response_function == 'status_post':
                self.status_post(
                    user=parameters['user'], 
                    message=parameters['message'], 
                    poll_options=parameters['poll_options'], 
                )
                break
            elif response_function == 'send_poll':
                self.send_poll(
                    user=parameters['user'], 
                    message=parameters['message'], 
                    poll_configs=parameters['poll_configs'], 
                    response_function=parameters['response_function'],
                    keep_current_talk=parameters['keep_current_talk']
                )
                break
            elif response_function == 'start_querying':
                self.start_querying(
                    user=parameters['user'], 
                    message=parameters['message'], 
                    response_function=parameters['response_function'],
                    keep_current_talk=parameters['keep_current_talk']
                )
                break
            elif response_function == 'quit_searching':
                self.quit_searching(
                    user=parameters['user'], 
                    data=parameters['data'], 
                    is_response=parameters['is_response']
                )
                break
            else:
                result = getattr(self, response_function)(
                    user=parameters['user'], 
                    data=parameters['data'], 
                    is_response=parameters['is_response']
                )
        return None


    # remove expired talk
    def clean_expired_talks(self):
        if len(self.talks) <= 0:
            return None
        
        talk_keys = self.talks.keys()
        for user_id in talk_keys:
            # get expired time
            expired_time = datetime.datetime.strptime(self.talks[user_id]['expired'], "%Y-%m-%d %H:%M:%S")

            # if expired, just remove talk record
            if datetime.datetime.now() > expired_time:
                self.talks.pop(user_id)
        return None
    
    def status_post(self, user, message, poll_options = None):
        """
        Send only message
        """
        full_message = "@{} ".format(user["acct"]) + message

        # make poll
        poll = None
        if poll_options != None:
            poll = self.mastodon.make_poll(options=poll_options, expires_in=5000)


        return self.mastodon.status_post(status=full_message, visibility="direct", poll=poll)

    def send_poll(self, user, message, poll_configs, response_function, keep_current_talk=False):
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
        """
        send a poll and update the talk record
        """

        # adding exit option
        poll_configs = [
            (self.SPECIAL_SELECTION_QUIT_SEARCHING, 'quit_searching', None),
            (self.SPECIAL_SELECTION_BACK_TO_ROOT, 'show_introduction', None),
        ]
        message += "(If you want to end the searching, just select the following option.)"

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
        message = "Talk end, thanks for talking with me :)"
        self.status_post(user, message)
        return None

    # ------------------ talk detail functions --------------
    # all the talk detail functions paras should be: user, data=None, is_response=False
    # =======================================================
    def show_introduction(self, user, data=None, is_response=False):
        """
        Introduce the bot functions.
        """
        poll_configs = [
            ('School Info & Fast Query', 'school_info_and_query_history', None),
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
                    # getattr(self, response_function)(user=user, data=data, is_response=False)
                    call_the_function = {
                        'response_function': response_function,
                        'parameters': {
                            'user': user,
                            'data': data,
                            'is_response': False
                        }
                    }
                    return call_the_function
            
            # error

        else:
            message = "Hello, I'm School Bot, nice to meet you! What do want to know?"
            call_the_function = {
                'response_function': 'send_poll',
                'parameters': {
                    'user': user,
                    'message': message,
                    'poll_configs': poll_configs,
                    'response_function': 'show_introduction',
                    'keep_current_talk': False
                }
            }
            return call_the_function

        return None

    def school_info_and_query_history(self, user, data=None, is_response=False):
        """
        Introduce the bot functions.
        """
        poll_configs = [
            ('School Info', 'school_info', None),
            ('Query History', 'question_history', None),
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
                    call_the_function = {
                        'response_function': response_function,
                        'parameters': {
                            'user': user,
                            'data': data,
                            'is_response': False
                        }
                    }
                    return call_the_function
            
            # error

        else:
            message = "You could check school basic info by select first option."
            message += "\nOr check your latest 10 query history."
            call_the_function = {
                'response_function': 'send_poll',
                'parameters': {
                    'user': user,
                    'message': message,
                    'poll_configs': poll_configs,
                    'response_function': 'school_info_and_query_history',
                    'keep_current_talk': False
                }
            }
            return call_the_function

        return None

    def school_info(self, user, data=None, is_response=False):
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
            school_info_dict[info_name] = info_value

        message = "What do you want to know about school? You can check the following links:"
        message += "\n1. school official website: "+school_info_dict["school_official_website"]
        message += "\n2. school contact info: "+school_info_dict["school_contact_info"]
        message += "\n3. school newbee info: "+school_info_dict["school_newbie_info"]
        message += "\n4. school F&Q: "+school_info_dict["school_f_and_q"]

        # save query history
        self.save_history(user['id'], self.QUERY_HISTORY_SCHOOL_INFO, message)

        call_the_function = {
            'response_function': 'status_post',
            'parameters': {
                'user': user,
                'message': message,
                'poll_configs': None
            }
        }
        return call_the_function

    def class_info(self, user, data=None, is_response=False):
        """
        Display info, let students choose options
        """
        poll_configs = [
            ('Recent Exam Info', 'get_recent_exam_info', None),
            ('Recent Assignment Info', 'get_recent_assignment_info', None),
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


            if course_code is None:

                # get course code from message
                # search course code in database
                words = received_message.split()
                for word in words:
                    # check if word is @xxxxx
                    if word[0] == '@':
                        continue
    
                    cursor = self.connection.cursor()
                    sql = "SELECT id, name from school_info_coursetemplate WHERE course_code like '%{}%' AND deleted_at is NULL;".format(word.upper())
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    for id, name in result:
                        course_code = word.upper()
                        break
                    if course_code != None:
                        break

                # find, save it to talk data
                # ask for grade
                if course_code != None:
                    talk['data']['course_code'] = course_code

                    message = "For searching what you want, could you tell me what grade you want ?"
                    # call the function
                    call_the_function = {
                        'response_function': 'start_querying',
                        'parameters': {
                            'user': user,
                            'message': message,
                            'response_function': 'class_info',
                            'keep_current_talk': True
                        }
                    }
                    return call_the_function

                # not found, ask for course code again
                message = "Sorry we can't find any course by your input {}, could you please try again ?".format(received_message)
                call_the_function = {
                    'response_function': 'start_querying',
                    'parameters': {
                        'user': user,
                        'message': message,
                        'response_function': 'class_info',
                        'keep_current_talk': False
                    }
                }
                return call_the_function
            elif grade is None:

                # get grade from message
                # search grade in database
                course_id = None
                words = received_message.split()
                for word in words:
                    # check if word is @xxxxx
                    if word[0] == '@':
                        continue
    
                    cursor = self.connection.cursor()
                    sql = "SELECT id from school_info_course WHERE course_template_id IN (SELECT id from school_info_coursetemplate WHERE course_code like '%{}%' AND deleted_at is NULL) AND grade = '{}' AND deleted_at is NULL;".format(course_code.upper(), word)
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    for id in result:
                        id = id[0]
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
                    call_the_function = {
                        'response_function': 'send_poll',
                        'parameters': {
                            'user': user,
                            'message': message,
                            'poll_configs': poll_configs,
                            'response_function': 'class_info',
                            'keep_current_talk': True
                        }
                    }
                    return call_the_function

                # not found, ask for course id again
                message = "For searching what you want, could you tell me what grade you want ?"
                message = "Sorry we can't find any course({}) by grade in your input {}, could you please try again ?".format(course_code, received_message)

                call_the_function = {
                    'response_function': 'start_querying',
                    'parameters': {
                        'user': user,
                        'message': message,
                        'response_function': 'class_info',
                        'keep_current_talk': True
                    }
                }
                return call_the_function
            else:
                return None
        elif is_response is True and 'selected_option' in data and course_code != None and grade != None:
            # get selection
            selected_option = data['selected_option']


            # response
            for option, response_function, parameters in poll_configs:
                if selected_option == option:

                    self.talks[user['id']]['data']['poll_configs'] = poll_configs

                    # call the function
                    call_the_function = {
                        'response_function': response_function,
                        'parameters': {
                            'user': user,
                            'data': data,
                            'is_response': True
                        }
                    }
                    return call_the_function

            # error
            return None

        else:
            message = "For searching what you want, could you tell me what course code of course you want ?"

            call_the_function = {
                'response_function': 'start_querying',
                'parameters': {
                    'user': user,
                    'message': message,
                    'response_function': 'class_info',
                    'keep_current_talk': False
                }
            }
            return call_the_function

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
        cursor.execute(sql)
        result = cursor.fetchone()

        if result is None:
            # display result and ask again
            message = "Sorry, not found {}({}) recent exam.".format(course_code, grade)
            message += "\nWhat do you want to know about {}({}), please select following option.".format(course_code, grade)
            call_the_function = {
                'response_function': 'send_poll',
                'parameters': {
                    'user': user,
                    'message': message,
                    'poll_configs': poll_configs,
                    'response_function': 'class_info',
                    'keep_current_talk': True
                }
            }
            return call_the_function

        else:
            # display result and ask again
            name, description,exam_at, exam_type, location, url = result

            message = "The recent exam:"
            message += "\n{}".format(name)
            message += "\n{}".format(description)
            message += "\ntime: {}".format(exam_at)

            if exam_type == 0:
                message += "\ntype: offline"
                message += "\nlocation: {}".format(location)
            else:
                message += "\ntype: online"

            # save query history
            title = self.QUERY_HISTORY_EXAM_INFO+" Of {}({})".format(course_code, grade)
            self.save_history(user['id'], title, message)

            message += "\nmore info: {}".format(url)
            message += "\n"
            message += "\nWhat do you want to know about {}({}), please select following option.".format(course_code, grade)
            call_the_function = {
                'response_function': 'send_poll',
                'parameters': {
                    'user': user,
                    'message': message,
                    'poll_configs': poll_configs,
                    'response_function': 'class_info',
                    'keep_current_talk': True
                }
            }
            return call_the_function

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
        cursor.execute(sql)
        result = cursor.fetchone()

        if result is None:
            # display result and ask again
            message = "Sorry, not found {}({}) recent assignment.".format(course_code, grade)
            message += "\nWhat do you want to know about {}({}), please select following option.".format(course_code, grade)
            call_the_function = {
                'response_function': 'send_poll',
                'parameters': {
                    'user': user,
                    'message': message,
                    'poll_configs': poll_configs,
                    'response_function': 'class_info',
                    'keep_current_talk': True
                }
            }
            return call_the_function

        else:
            # display result and ask again
            name, description, deadline_at, url = result

            message = "The recent assignment:"
            message += "\n{}".format(name)
            message += "\n{}".format(description)
            message += "\ndeadline: {}".format(deadline_at)

            # save query history
            title = self.QUERY_HISTORY_ASSIGNMENT_INFO+" Of {}({})".format(course_code, grade)
            self.save_history(user['id'], title, message)

            message += "\nmore info: {}".format(url)
            message += "\n"
            message += "\nWhat do you want to know about {}({}), please select following option.".format(course_code, grade)
            call_the_function = {
                'response_function': 'send_poll',
                'parameters': {
                    'user': user,
                    'message': message,
                    'poll_configs': poll_configs,
                    'response_function': 'class_info',
                    'keep_current_talk': True
                }
            }
            return call_the_function

        return None
    
    def make_appointment(self, user, data=None, is_response=False):
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


            # get course code from message
            # search course code in database
            words = received_message.split()
            for word in list(words):
                # check if word is @xxxxx
                if word[0] == '@':
                    words.remove(word)
            
            input_user_name = " ".join(words)
            search_name = "%".join(words)
            search_name = search_name.lower()

            cursor = self.connection.cursor()
            sql = "SELECT user_name, email from school_info_teachingassistant WHERE user_name like '%{}%' AND deleted_at is NULL;".format(search_name.lower())
            cursor.execute(sql)
            result = cursor.fetchone()
            
            if result is None:
                # not found, ask for name again
                message = "Sorry we can't find any teaching assistant who's name is {}, could you please try again ?".format(input_user_name)
                call_the_function = {
                    'response_function': 'start_querying',
                    'parameters': {
                        'user': user,
                        'message': message,
                        'response_function': 'make_appointment',
                        'keep_current_talk': True
                    }
                }
                return call_the_function

            else:
                # clean current talk
                self.talks.pop(user['id'])
                # display the info
                teaching_assistant_name, email = result
                message = "{} email is:".format(teaching_assistant_name)
                message += "\n{}".format(email)

                # save query history
                title = self.QUERY_HISTORY_TEACHING_ASSISTANT_INFO+": {}".format(teaching_assistant_name)
                self.save_history(user['id'], title, message)
                call_the_function = {
                    'response_function': 'status_post',
                    'parameters': {
                        'user': user,
                        'message': message,
                        'poll_options': None
                    }
                }
                return call_the_function

        else:
            message = "Please tell me the teaching assistant name who you want to make an appointment."
            call_the_function = {
                'response_function': 'start_querying',
                'parameters': {
                    'user': user,
                    'message': message,
                    'response_function': 'make_appointment',
                    'keep_current_talk': False
                }
            }
            return call_the_function

        return None

    def feedback(self, user, data=None, is_response=False):
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
                    call_the_function = {
                        'response_function': response_function,
                        'parameters': {
                            'user': user,
                            'data': data,
                            'is_response': False
                        }
                    }
                    return call_the_function

            # error
        else:
            message = "You can select teaching evaluate and scoring for the class and make some suggestions!"
            message += "\nIf you have some questions, but just can't find answer by our bot, you can select other questions option and tell us."
            call_the_function = {
                'response_function': 'send_poll',
                'parameters': {
                    'user': user,
                    'message': message,
                    'poll_configs': poll_configs,
                    'response_function': 'feedback',
                    'keep_current_talk': False
                }
            }
            return call_the_function


        return None

    def teach_feedback(self, user, data=None, is_response=False):
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


            if course_code is None:

                # get course code from message
                # search course code in database
                words = received_message.split()
                for word in words:
                    # check if word is @xxxxx
                    if word[0] == '@':
                        continue
    
                    cursor = self.connection.cursor()
                    sql = "SELECT id, name from school_info_coursetemplate WHERE course_code like '{}%' AND deleted_at is NULL;".format(word.upper())
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    for id, name in result:
                        course_code = word.upper()
                        break
                    if course_code != None:
                        break

                # find, save it to talk data
                # ask for grade
                if course_code != None:
                    talk['data']['course_code'] = course_code

                    message = "Please relying grade."
                    call_the_function = {
                        'response_function': 'start_querying',
                        'parameters': {
                            'user': user,
                            'message': message,
                            'response_function': 'teach_feedback',
                            'keep_current_talk': True
                        }
                    }
                    return call_the_function


                # not found, ask for course code again
                message = "Sorry we can't find any course by your input {}, could you please try again ?".format(received_message)
                call_the_function = {
                    'response_function': 'start_querying',
                    'parameters': {
                        'user': user,
                        'message': message,
                        'response_function': 'teach_feedback',
                        'keep_current_talk': True
                    }
                }
                return call_the_function


            elif grade is None:

                # get grade from message
                # search grade in database
                course_id = None
                words = received_message.split()
                for word in words:
                    # check if word is @xxxxx
                    if word[0] == '@':
                        continue
    
                    cursor = self.connection.cursor()
                    sql = "SELECT id from school_info_course WHERE course_template_id IN (SELECT id from school_info_coursetemplate WHERE course_code like '%{}%' AND deleted_at is NULL) AND grade = '{}' AND deleted_at is NULL;".format(course_code.upper(), word)
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    for id in result:
                        id = id[0]
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
                    call_the_function = {
                        'response_function': 'start_querying',
                        'parameters': {
                            'user': user,
                            'message': message,
                            'response_function': 'teach_feedback',
                            'keep_current_talk': True
                        }
                    }
                    return call_the_function

                # not found, ask for course id again
                message = "Sorry we can't find any course({}) by grade in your input {}, could you please try again ?".format(course_code, received_message)
                call_the_function = {
                    'response_function': 'start_querying',
                    'parameters': {
                        'user': user,
                        'message': message,
                        'response_function': 'teach_feedback',
                        'keep_current_talk': True
                    }
                }
                return call_the_function

            elif score is None:

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
                    call_the_function = {
                        'response_function': 'start_querying',
                        'parameters': {
                            'user': user,
                            'message': message,
                            'response_function': 'teach_feedback',
                            'keep_current_talk': True
                        }
                    }
                    return call_the_function
                
                # save score
                self.talks[user['id']]['data']['score'] = score

                message = "If you have any suggestions, you can reply me. If not, just reply -1."
                call_the_function = {
                    'response_function': 'start_querying',
                    'parameters': {
                        'user': user,
                        'message': message,
                        'response_function': 'teach_feedback',
                        'keep_current_talk': True
                    }
                }
                return call_the_function
            
            elif suggestion is None:

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
                call_the_function = {
                    'response_function': 'status_post',
                    'parameters': {
                        'user': user,
                        'message': message,
                        'poll_options': None
                    }
                }
                return call_the_function
            else:
                call_the_function = {
                    'response_function': 'start_querying',
                    'parameters': {
                        'user': user,
                        'message': message,
                        'response_function': 'teach_feedback',
                        'keep_current_talk': True
                    }
                }
                return call_the_function

        else:
            message = "Please tell me which course you want to scoring by relying the course code."
            call_the_function = {
                'response_function': 'start_querying',
                'parameters': {
                    'user': user,
                    'message': message,
                    'response_function': 'teach_feedback',
                    'keep_current_talk': False
                }
            }
            return call_the_function

    def question_history(self, user, data=None, is_response=False):
        """
        If can't find query history, display there are no query history.
        If not, display latest 10 query history..
        """

        latest_10_query_history = None
        if user['id'] in self.talks:
            talk = self.talks[user['id']]
            if 'query_history' in talk['data']:
                latest_10_query_history = talk['data']['query_history']

        if is_response == True and 'mention' in data:

            # read history
            if latest_10_query_history is None:
                cursor = self.connection.cursor()
                sql = "SELECT query_title, query_content from school_info_queryhistory WHERE user_id = '{}' AND deleted_at is NULL ORDER BY updated_at DESC LIMIT 10;".format(user['id'])
                cursor.execute(sql)
                result = cursor.fetchall()
                latest_10_query_history = []
                for title, content in result:
                    latest_10_query_history.append((title, content))

                # save the query history to the talks record
                self.talks[user['id']]['data']['query_history'] = latest_10_query_history

            # get response from data
            mention = data['mention']
            soup = BeautifulSoup(mention["content"], "html.parser")
            received_message = soup.find('p').get_text().strip()


            # get course code from message
            # search course code in database
            try:
                words = received_message.split()
                for word in list(words):
                    # check if word is @xxxxx
                    if word[0] == '@':
                        words.remove(word)

                query_index = int(" ".join(words))
                query_index -= 1 # the real index is from 0
            except Exception as err:
                message = "Please input 1~{} number :)".format(len(latest_10_query_history))
                call_the_function = {
                    'response_function': 'start_querying',
                    'parameters': {
                        'user': user,
                        'message': message,
                        'response_function': 'question_history',
                        'keep_current_talk': True
                    }
                }
                return call_the_function


            # debug
            # debug

            # check if input illegal, let user try again
            if query_index < 0 or query_index > len(latest_10_query_history)-1:
                message = "Sorry, we can't find question history based on your input."
                message += "\nPlease try again."
                message += "\nYour recent query history is:"
                index = 1
                for title, content in latest_10_query_history:
                    message += "\n{}. {}".format(index, title)
                    index += 1
                message += "\nPlease reply the id of which query history you want to view."
                call_the_function = {
                    'response_function': 'start_querying',
                    'parameters': {
                        'user': user,
                        'message': message,
                        'response_function': 'question_history',
                        'keep_current_talk': True
                    }
                }
                return call_the_function

            # display the query result
            title, content = latest_10_query_history[query_index]
            message = "The query history you want is:"
            message += "\n{}".format(title)
            message += "\n{}".format(content)

            # clean current talk
            self.talks.pop(user['id'])
            call_the_function = {
                'response_function': 'status_post',
                'parameters': {
                    'user': user,
                    'message': message,
                    'poll_options': None
                }
            }
            return call_the_function

        else:
            cursor = self.connection.cursor()
            sql = "SELECT query_title, query_content from school_info_queryhistory WHERE user_id = {} AND deleted_at is NULL ORDER BY updated_at DESC LIMIT 10;".format(user['id'])
            cursor.execute(sql)
            result = cursor.fetchall()

            # 1. Not find history, just display no query history
            if result is None:
                self.talks.pop(user['id'])
                message = "Sorry, you don't have query history."
                call_the_function = {
                    'response_function': 'status_post',
                    'parameters': {
                        'user': user,
                        'message': message,
                        'poll_options': None
                    }
                }
                return call_the_function

            # 2. Find History, just leave selection
            message = "Your recent query history is:"
            latest_10_query_history = []
            index = 1
            for title, content in result:
                latest_10_query_history.append((title, content))
                message += "\n{}. {}".format(index, title)
                index += 1
            message += "\nPlease reply the id of which query history you want to view."
            call_the_function = {
                'response_function': 'start_querying',
                'parameters': {
                    'user': user,
                    'message': message,
                    'response_function': 'question_history',
                    'keep_current_talk': False
                }
            }
            return call_the_function

        return None

    def other_questions(self, user, data=None, is_response=False):
        """
        Ask for record new questions.
        """

        if is_response == True and 'mention' in data:

            # get response from data
            mention = data['mention']
            soup = BeautifulSoup(mention["content"], "html.parser")
            received_message = soup.find('p').get_text().strip()


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
            call_the_function = {
                'response_function': 'status_post',
                'parameters': {
                    'user': user,
                    'message': message,
                    'poll_options': None
                }
            }
            return call_the_function

        else:
            message = "Please input your question, we would answer it later."
            call_the_function = {
                'response_function': 'start_querying',
                'parameters': {
                    'user': user,
                    'message': message,
                    'response_function': 'other_questions',
                    'keep_current_talk': False
                }
            }
            return call_the_function

        return None
    
    def save_history(self, user_id, title, message):
        """
        1. try to get query history by user_id and title
        2. if no history, just insert new one
        3. if history exists and the message is the same, just update the update time
        4. if history exists and the message is updated, just update the message
        """
        now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. try to get query history by user_id and title
        cursor = self.connection.cursor()
        sql = "SELECT id, query_content from school_info_queryhistory WHERE user_id = '{}' AND query_title = '{}' AND deleted_at is NULL;".format(user_id, title)
        cursor.execute(sql)
        result = cursor.fetchone()

        # 2. if no history, just insert new one
        if result is None:
            sql = "INSERT INTO `school_info_queryhistory` (`id`, `created_at`, `updated_at`, `deleted_at`, `user_id`, `query_content`, `query_title`) VALUES (NULL, '{}', '{}', NULL, '{}', '{}', '{}');".format(now_time, now_time, user_id, message, title)
            cursor.execute(sql)
            return None

        id, old_message = result
        # 3. if history exists and the message is the same, just update the update time
        if old_message == message:
            sql = "UPDATE `school_info_queryhistory` SET `updated_at` = '{}' WHERE `school_info_queryhistory`.`id` = {};".format(now_time, id)
            cursor.execute(sql)
            return None

        # 4. if history exists and the message is updated, just update the message
        sql = "UPDATE `school_info_queryhistory` SET `updated_at` = '{}', `query_content` = '{}' WHERE `school_info_queryhistory`.`id` = {};".format(now_time, message, id)
        cursor.execute(sql)
        return None
