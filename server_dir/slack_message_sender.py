from slacker import Slacker
import json
import os
from pathlib import Path
import random
import configparser
from server_dir.conflict_flag_enum import Conflict_flag
from server_dir.user_database import user_database

def get_slack():
    token = ''
    if not os.path.isfile("server_config.ini"):
        print("ERROR :: There is no server_config.ini")
        exit(2)
    else:
        config = configparser.ConfigParser()
        config.read("server_config.ini")
        try:
            token = config["SLACK"]["TOKEN"]
        except:
            print("ERROR :: It is server_config.ini")
            exit(2)
    slack = Slacker(token)
    return slack


def make_shell_list(file):
    f = open(file, "r", encoding="UTF8")
    text = f.read()
    text = text.split("\n")
    return text


def make_go_to_same_file_shell_list():
    go_to_same_file_shell_list = make_shell_list(os.path.join(Path(os.getcwd()).parent, "situation_shell", "go_to_same_file.txt"))
    return go_to_same_file_shell_list

def make_same_file_shell_list():
    go_to_same_file_shell_list = make_shell_list(os.path.join(Path(os.getcwd()).parent, "situation_shell", "same_file.txt"))
    return go_to_same_file_shell_list

def make_server_shell_list():
    get_server_shell_list = make_shell_list(os.path.join(Path(os.getcwd()).parent, "situation_shell", "get_severe.txt"))
    return get_server_shell_list

def make_conflict_finished_list():
    conflict_finished = make_shell_list(os.path.join(Path(os.getcwd()).parent, "situation_shell", "conflict_finished.txt"))
    return conflict_finished

def make_get_closer_list():
    get_closer_list = make_shell_list(os.path.join(Path(os.getcwd()).parent, "situation_shell", "get_closer.txt"))
    return get_closer_list

def make_lower_severity_list():
    lower_severity = make_shell_list(os.path.join(Path(os.getcwd()).parent, "situation_shell", "conflict_alleviated.txt"))
    return lower_severity

# Get user slack id
def get_user_slack_id(git_id):
    u_db = user_database()
    return u_db.search_user_slack_id_code(git_id)


def send_conflict_message(conflict_flag, conflict_project, conflict_file, conflict_logic, user1_name, user2_name):

    user1_slack_id_code = get_user_slack_id(user1_name)
    user2_slack_id_code = get_user_slack_id(user2_name)
    message = ""

    # Already conflict
    if(conflict_flag == Conflict_flag.getting_severity.value):
        # get server
        server_shell = make_server_shell_list()
        message = server_shell[random.randint(0, len(server_shell) - 1)]

    elif(conflict_flag == Conflict_flag.same_severity.value):
        # same server
        same_shell = make_same_file_shell_list()
        message = same_shell[random.randint(0, len(same_shell) - 1)] % (str(user1_slack_id_code[0]), str(user2_slack_id_code[0]), str(conflict_file), str(conflict_logic))

    elif(conflict_flag == Conflict_flag.lower_severity.value):
        # lower serverity
        lower_severity = make_lower_severity_list()
        message = lower_severity[random.randint(0, len(lower_severity) - 1)] % (user1_slack_id_code[0], user2_slack_id_code[0])

    # First conflict
    elif(conflict_flag == Conflict_flag.same_function.value):
        # same function
        same_shell = make_same_file_shell_list()
        message = same_shell[random.randint(0, len(same_shell) - 1)] % (user1_slack_id_code[0], user2_slack_id_code[0], conflict_file, conflict_logic)

    elif(conflict_flag == Conflict_flag.same_class.value):
        # same class
        same_shell = make_same_file_shell_list()
        message = same_shell[random.randint(0, len(same_shell) - 1)] % (user1_slack_id_code[0], user2_slack_id_code[0], conflict_file, conflict_logic)

    elif(conflict_flag == Conflict_flag.file_in.value):
        # just in
        get_closer = make_same_file_shell_list()
        message = get_closer[random.randint(0, len(get_closer) - 1)] % (user1_slack_id_code[0], user2_slack_id_code[0], conflict_file, " ")

    elif(conflict_flag == Conflict_flag.conflict_finished.value):
        # conflict solved
        conflict_finished = make_conflict_finished_list()
        message = conflict_finished[random.randint(0, len(conflict_finished) - 1)] % ('you', user2_slack_id_code[0])

    elif(conflict_flag == Conflict_flag.indirect_conflict.value):
        message = "indirect conflict : your name : %s / your file : %s / your logic : %s " \
                  "/ other name : %s / other file: %s / other logic : %s " \
                  "" %(user1_slack_id_code[0], conflict_file[0], conflict_file[1],
                       user2_slack_id_code[0], conflict_logic[0], conflict_logic[1])

    send_direct_message(user1_slack_id_code[1], message)
    print(message)

    return


def send_conflict_message_channel(conflict_project, conflict_file, conflict_logic, user1_name, user2_name):
    user1_slack_id_code = get_user_slack_id(user1_name)
    user2_slack_id_code = get_user_slack_id(user2_name)
    message = ""

    # same server
    same_shell = make_same_file_shell_list()
    message = same_shell[random.randint(0, len(same_shell) - 1)] % (
    user1_slack_id_code[0], user2_slack_id_code[0], conflict_file, conflict_logic)
    send_channel_message("code-conflict-chatbot", message)
    return


def send_lock_file_message(slack_code, lock_file_list):
    pass


# Put channel name and message for sending chatbot message
def send_channel_message(channel, message):
    slack = get_slack()
    attachments_dict = dict()
    attachments_dict['text'] = "%s" % (message)
    attachments_dict['mrkdwn_in'] = ["text", "pretext"]
    attachments = [attachments_dict]
    slack.chat.post_message(channel="#" + channel, text=None, attachments=attachments, as_user=True)
    return


# Put user slack id and message for sending chatbot message
def send_direct_message(user_id, message):
    slack = get_slack()
    attachments_dict = dict()
    attachments_dict['text'] = "%s" % (message)
    attachments_dict['mrkdwn_in'] = ["text", "pretext"]
    attachments = [attachments_dict]
    slack.chat.post_message(channel="" + user_id, text=None, attachments=attachments, as_user=True)
    return