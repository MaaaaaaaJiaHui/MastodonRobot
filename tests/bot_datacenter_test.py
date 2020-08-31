#!/usr/bin/python
# Filename:auto.py

import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import unittest
import pymysql
import bot_datacenter
import datetime

class WidgetTestCase(unittest.TestCase):
    
    connection = None # The link to db
    datacenter = None # We would use this datacenter to run all the test cases.

    @classmethod
    def setUpClass(self):
        # Init connection to db.
        self.connection = pymysql.connect(host='localhost', user='root',password='',database='mastodon_bot',charset="utf8")

        # set basic data
        cursor = self.connection.cursor()
        now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        future_time = (datetime.datetime.now()+datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        sql = ''
        sql += "TRUNCATE `mastodon_bot`.`school_info_coursetemplate`;"
        sql += "TRUNCATE `mastodon_bot`.`school_info_teacher`;"
        sql += "TRUNCATE `mastodon_bot`.`school_info_course`;"
        sql += "TRUNCATE `mastodon_bot`.`school_info_teachingassistant`;"
        sql += "TRUNCATE `mastodon_bot`.`school_info_exam`;"
        sql += "TRUNCATE `mastodon_bot`.`school_info_assignment`;"

        sqls = sql.split(';')
        for sql_command in sqls:
            if sql_command == '':
                continue
            print("running {} ...".format(sql_command[:15]))
            cursor.execute(sql_command)
        
        sql = ''

        sql += "INSERT INTO `school_info_coursetemplate` (`id`, `created_at`, `updated_at`, `deleted_at`, `course_code`, `name`) VALUES (1, '2020-08-10 02:07:42.739913', '2020-08-10 02:07:42.739913', NULL, 'CS12345', 'Computer Science');"
        sql += "INSERT INTO `school_info_teacher` (`id`, `created_at`, `updated_at`, `deleted_at`, `user_name`, `email`) VALUES (1, '2020-08-09 00:49:11.868890', '2020-08-09 00:49:11.868890', NULL, 'jane', 'jane@example.com');"
        sql += "INSERT INTO `school_info_teacher` (`id`, `created_at`, `updated_at`, `deleted_at`, `user_name`, `email`) VALUES (2, '2020-08-09 00:49:53.796138', '2020-08-09 00:49:53.796138', NULL, 'ben', 'ben@example.com');"
        sql += "INSERT INTO `school_info_course` (`id`, `created_at`, `updated_at`, `deleted_at`, `grade`, `teacher_id`, `course_template_id`) VALUES (4, '2020-08-10 02:46:01.292640', '2020-08-10 02:46:01.292640', NULL, '2016', 1, 1);"
        sql += "INSERT INTO `school_info_teachingassistant` (`id`, `created_at`, `updated_at`, `deleted_at`, `user_name`, `email`) VALUES (1, '2020-08-02 12:22:48.000000', '2020-08-02 12:22:48.000000', NULL, 'tom', 'tom@abc.com');"
        sql += "INSERT INTO `school_info_assignment` (`id`, `created_at`, `updated_at`, `deleted_at`, `name`, `description`, `deadline_at`, `url`, `course_id`) VALUES (2, '2020-08-10 03:32:12.427849', '2020-08-10 03:32:12.427849', NULL, 'YiiLib', 'AA', '{}', 'https://youtu.be/R4Nh-EgWjyQ', 4);".format(future_time)
        sql += "INSERT INTO `school_info_exam` (`id`, `created_at`, `updated_at`, `deleted_at`, `name`, `description`, `exam_at`, `exam_type`, `location`, `url`, `course_id`) VALUES (7, '2020-08-10 03:29:53.110262', '2020-08-10 03:30:08.380341', NULL, 'PMS', 'xxxxxxxx', '{}', 0, 'dfdfdf', 'https://youtu.be/SLauY6PpjW4', 4);".format(future_time)

        sqls = sql.split(';')
        for sql_command in sqls:
            if sql_command == '':
                continue
            print("running {} ...".format(sql_command[:30]))
            cursor.execute(sql_command)

        # Init datacenter, we would use it to test all.
        # Because all the unitests would run at local, we don't need connection to mastodon,
        # we set mastodon to None.
        self.datacenter = bot_datacenter.BotDataCenter(mastodon=None, connection=self.connection)

    def test_show_introduction(self):
        """ 
        Test show introduction function.
        """
        # test say hello
        user = {'id':123, 'username':'test_user'}
        result = self.datacenter.show_introduction(user)

        self.assertEqual(
            result['response_function'],
            'send_poll'
        )

        # test after vote
        data = {'selected_option': 'Feedback'}
        self.datacenter.talks[123] = {}
        result = self.datacenter.show_introduction(user, data, is_response=True)
        self.assertEqual(result['response_function'],'feedback')

    def test_school_info_and_query_history(self):

        user = {'id':123, 'username':'test_user'}
        result = self.datacenter.school_info_and_query_history(user)
        self.assertEqual(result['response_function'],'send_poll')
        self.assertEqual(result['parameters']['response_function'],'school_info_and_query_history')

        # test after vote
        data = {'selected_option': 'School Info'}
        self.datacenter.talks[123] = {}
        result = self.datacenter.school_info_and_query_history(user, data, is_response=True)
        self.assertEqual(result['response_function'],'school_info')

        self.datacenter.talks[123] = {}
        data = {'selected_option': 'Query History'}
        result = self.datacenter.school_info_and_query_history(user, data, is_response=True)
        self.assertEqual(result['response_function'],'question_history')

    def test_school_info(self):
        user = {'id':123, 'username':'test_user'}
        result = self.datacenter.school_info(user)
        self.assertEqual(result['response_function'],'status_post')

        result = self.datacenter.school_info(user, data=None, is_response=True)
        self.assertEqual(result['response_function'],'status_post')

    def test_class_info(self):
        user = {'id':123, 'username':'test_user'}
        result = self.datacenter.class_info(user)
        self.assertEqual(result['response_function'],'start_querying')

        # test after vote
        data = {'mention': {'content':'<p>@bot cS1234567</p>'}}
        self.datacenter.talks[123] = {'data':{}}
        result = self.datacenter.class_info(user, data, is_response=True)
        self.assertNotEqual(result['parameters']['message'].find('could you please try again'), -1, 'When input error course code, there should let user try again.')

        data = {'mention': {'content':'<p>@bot cS12345</p>'}}
        self.datacenter.talks[123] = {'data':{}}
        result = self.datacenter.class_info(user, data, is_response=True)
        self.assertEqual(result['parameters']['message'].find('could you please try again'), -1, 'When input correct course code, we won\'t let user try again.')
        self.assertNotEqual(result['parameters']['message'].find('grade'), -1, 'When input correct course code, we should ask user for grade.')
        self.assertEqual(self.datacenter.talks[123]['data']['course_code'], 'CS12345', 'When input correct course code, we save it to talks.')

        data = {'mention': {'content':'<p>@bot 2020</p>'}}
        result = self.datacenter.class_info(user, data, is_response=True)
        self.assertNotEqual(result['parameters']['message'].find('could you please try again'), -1, 'When input error grade, we should let user try again.')
        self.assertNotEqual(result['parameters']['message'].find('grade'), -1, 'When input error grade, we should ask user try again.')

        data = {'mention': {'content':'<p>@bot 2016</p>'}}
        result = self.datacenter.class_info(user, data, is_response=True)
        self.assertEqual(result['response_function'], 'send_poll', 'When input correct grade, we should ask user for grade.')
        
        data = {'selected_option': 'Recent Exam Info'}
        result = self.datacenter.class_info(user, data, is_response=True)
        self.assertEqual(result['response_function'], 'get_recent_exam_info', 'When select recent exam, we should call this function.')

    def test_get_recent_exam_info(self):
        # set data
        self.datacenter.talks[123] = {
            'data': {
                'course_id': 4,
                'course_code': 'CS123456',
                'grade': 2016,
                'poll_configs': [
                    ('Recent Exam Info', 'get_recent_exam_info', None),
                    ('Recent Assignment Info', 'get_recent_assignment_info', None),
                ]
            }
        }
        user = {'id':123, 'username':'test_user'}
        result = self.datacenter.get_recent_exam_info(user)
        self.assertNotEqual(result['parameters']['message'].find('The recent exam:'), -1, 'Could not display exists exam.')

        self.datacenter.talks[123]['data']['course_id'] = 100
        result = self.datacenter.get_recent_exam_info(user)
        self.assertEqual(result['parameters']['message'].find('The recent exam:'), -1, 'When the exam not exists, there should not find anything.')

    def test_get_recent_assignment_info(self):
        # set data
        self.datacenter.talks[123] = {
            'data': {
                'course_id': 4,
                'course_code': 'CS123456',
                'grade': 2016,
                'poll_configs': [
                    ('Recent Exam Info', 'get_recent_exam_info', None),
                    ('Recent Assignment Info', 'get_recent_assignment_info', None),
                ]
            }
        }
        user = {'id':123, 'username':'test_user'}
        result = self.datacenter.get_recent_assignment_info(user)
        print(result)
        self.assertNotEqual(result['parameters']['message'].find('The recent assignment:'), -1, 'Could not display exists assignment.')

        self.datacenter.talks[123]['data']['course_id'] = 100
        result = self.datacenter.get_recent_assignment_info(user)
        self.assertEqual(result['parameters']['message'].find('The recent assignment:'), -1, 'When the assignment not exists, there should not find anything.')


    def test_make_appointment(self):
        user = {'id':123, 'username':'test_user'}
        result = self.datacenter.make_appointment(user)
        self.assertEqual(result['response_function'],'start_querying')

        # test after vote
        data = {'mention': {'content':'<p>@bot abc</p>'}}
        self.datacenter.talks[123] = {'data':{}}
        result = self.datacenter.make_appointment(user, data, is_response=True)
        self.assertNotEqual(result['parameters']['message'].find('could you please try again'), -1, 'When input error name of teaching assistants, there should let user try again.')

        data = {'mention': {'content':'<p>@bot Tom</p>'}}
        self.datacenter.talks[123] = {'data':{}}
        result = self.datacenter.make_appointment(user, data, is_response=True)
        self.assertNotEqual(result['parameters']['message'].find('email'), -1, 'When input correct teaching assistant name, we should display the email correctly.')

    def test_feedback(self):
        user = {'id':123, 'username':'test_user'}
        self.datacenter.talks = {}
        result = self.datacenter.feedback(user)
        self.assertEqual(result['response_function'],'send_poll')

        # test after vote
        data = {'selected_option': 'Teaching Evaluate'}
        self.datacenter.talks[123] = {}
        result = self.datacenter.feedback(user, data, is_response=True)
        self.assertEqual(result['response_function'],'teach_feedback')

    def test_teach_feedback(self):
        # then we should ask for scores
        # input error score
        # input right score
        # input suggestion
        # choose not input suggestion
        # at start, we should ask for course
        user = {'id':123, 'username':'test_user'}
        result = self.datacenter.teach_feedback(user)
        self.assertEqual(result['response_function'],'start_querying')

        data = {'mention': {'content':'<p>@bot cS1234567</p>'}}
        self.datacenter.talks[123] = {'data':{}}
        result = self.datacenter.teach_feedback(user, data, is_response=True)
        self.assertNotEqual(result['parameters']['message'].find('could you please try again'), -1, 'When input error course code, there should let user try again.')
        data = {'mention': {'content':'<p>@bot cS12345</p>'}}
        self.datacenter.talks[123] = {'data':{}}
        result = self.datacenter.teach_feedback(user, data, is_response=True)
        self.assertEqual(result['parameters']['message'].find('could you please try again'), -1, 'When input correct course code, we won\'t let user try again.')
        self.assertNotEqual(result['parameters']['message'].find('grade'), -1, 'When input correct course code, we should ask user for grade.')
        self.assertEqual(self.datacenter.talks[123]['data']['course_code'], 'CS12345', 'When input correct course code, we save it to talks.')

        data = {'mention': {'content':'<p>@bot 2020</p>'}}
        result = self.datacenter.teach_feedback(user, data, is_response=True)
        self.assertNotEqual(result['parameters']['message'].find('could you please try again'), -1, 'When input error grade, we should let user try again.')
        self.assertNotEqual(result['parameters']['message'].find('grade'), -1, 'When input error course code, we should ask user for grade.')

        data = {'mention': {'content':'<p>@bot 2016</p>'}}
        result = self.datacenter.teach_feedback(user, data, is_response=True)
        self.assertEqual(result['response_function'], 'start_querying', 'When input correct grade, we should ask user for scoring.')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(WidgetTestCase("test_show_introduction"))
    suite.addTest(WidgetTestCase("test_school_info_and_query_history"))
    suite.addTest(WidgetTestCase("test_school_info"))
    suite.addTest(WidgetTestCase("test_class_info"))
    suite.addTest(WidgetTestCase("test_get_recent_exam_info"))
    suite.addTest(WidgetTestCase("test_get_recent_assignment_info"))
    suite.addTest(WidgetTestCase("test_make_appointment"))
    suite.addTest(WidgetTestCase("test_feedback"))
    suite.addTest(WidgetTestCase("test_teach_feedback"))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest = 'suite')