def select_info(mastodon, user, message, conn=None):
    if message == 'hello':
        show_introduction(mastodon, user)
    elif message == 'school_info':
        school_info(mastodon, user, conn)
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
        # show_introduction(mastodon, user)
        return False
    return True

def status_post(mastodon, user, message, poll_options = None):
    """
    Send only message
    """
    full_message = "@{} ".format(user["acct"]) + message

    # make poll
    poll = None
    if poll_options != None:
        poll = mastodon.make_poll(options=poll_options, expires_in=5000)

    post = mastodon.status_post(status=full_message, visibility="direct", poll=poll)

    print('status post :', full_message)
    if poll != None:
        print('polls are:', poll_options)
        print('-----------post:------------')
        print(post)

        # wait 8 s
        import time
        for sec in range(15):
            time.sleep(1)
            print('wait {}s ...'.format(sec+1))

        # check poll
        poll_id = post["poll"]["id"]
        target_poll = mastodon.poll(poll_id)

        # print voted result
        print('-----------current poll is:----------')
        print(target_poll)
        selected_option = ''
        for poll_option in target_poll["options"]:
            if poll_option["votes_count"] > 0:
                selected_option = poll_option["title"]
                break
        
        if selected_option != None:
            print('select {}'.format(select_info))
            select_info(mastodon, user, selected_option)

    return True

def show_introduction(mastodon, user):
    """
    Introduce the bot functions.
    """
    message = "Hello, I'm School Bot, nice to meet you! What do want to know?"
    print(message)

    poll_options = [
        'school_info',
        'school_contact_info',
        'school_newbee_info',
        'school_f_and_q',
    ]

    return status_post(mastodon, user, message, poll_options)

def school_info(mastodon, user, conn):
    """
    Display school info, let students choose options
    """

    # read information websites
    school_info_dict = {}
    cursor = conn.cursor()
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
    return status_post(mastodon, user, message)

def school_official_website():
    """
    Display info, let students choose options
    """
    message = "This function is developing"
    print(message)

def school_contact_info():
    """
    Display info, let students choose options
    """
    message = "This function is developing"
    print(message)

def school_newbee_info():
    """
    Display info, let students choose options
    """
    message = "This function is developing"
    print(message)

def school_f_and_q():
    """
    Display info, let students choose options
    """
    message = "This function is developing"
    print(message)






def class_info():
    """
    Display info, let students choose options
    """
    message = "This function is developing"
    print(message)

def meeting_book():
    """
    Display info, let students choose options
    """
    message = "This function is developing"
    print(message)

def teach_feedback():
    """
    Display info, let students choose options
    """
    message = "This function is developing"
    print(message)

def question_history():
    """
    Display info, let students choose options
    """
    message = "This function is developing"
    print(message)

def other_questions():
    """
    Display info, let students choose options
    """
    message = "This function is developing"
    print(message)