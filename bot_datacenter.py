def status_post(mastodon, user, message):
    full_message = "@{} ".format(user["acct"]) + message
    mastodon.status_post(status=full_message, visibility="direct")
    print('status post :', full_message)
    return True

def show_introduction(mastodon, user):
    """
    Introduce the bot functions.
    """
    message = "Hello, I'm School Bot, nice to meet you! What do want to know?"
    print(message)
    return status_post(mastodon, user, message)

def school_info(mastodon, user):
    """
    Display school info, let students choose options
    """
    message = "What do you want to konw about school? You can check the following links:"
    message += "\n1. school official website: http://google.com/"
    message += "\n2. school contact info: http://google.com/"
    message += "\n3. school newbee info: http://google.com/"
    message += "\n4. school F&Q: http://google.com/"
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