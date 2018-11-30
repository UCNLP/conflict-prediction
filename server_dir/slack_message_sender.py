from slacker import Slacker
import os
from pathlib import Path
import random
import configparser
from datetime import datetime, timedelta
from server_dir.conflict_flag_enum import Conflict_flag
from server_dir.user_database import user_database
from chat_bot_server_dir.work_database import work_database
from chat_bot_server_dir.constants import *


def get_slack():
    token = ''
    file_path = os.path.join(Path(os.getcwd()).parent, "all_server_config.ini")
    if not os.path.isfile(file_path):
        print("ERROR :: There is no server_config.ini")
        exit(2)
    else:
        config = configparser.ConfigParser()
        config.read(file_path)
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


def get_message(shell_file):
    shell_list = make_shell_list(os.path.join(Path(os.getcwd()).parent, "situation_shell", shell_file))
    message = random.choice(shell_list)
    return message


def get_git_diff_code(user_name, project_name, file_name):
    w_db = work_database()
    git_diff_code = w_db.get_git_diff_code(user_name, project_name, file_name)
    if not git_diff_code:
        git_diff_code = ""
    git_diff_code = git_diff_code.replace("|||", "\n")
    print("get_git_diff_code", git_diff_code)
    print("hi")
    return git_diff_code


# Get user slack id
def get_user_slack_id_and_code(git_id):
    u_db = user_database("parent")
    return u_db.search_user_slack_id_and_code(git_id)


def send_lock_message(lock_file_list, user_name):
    w_db = work_database()
    user_slack_id_code = get_user_slack_id_and_code(user_name)
    message = ""
    for lfl in lock_file_list:
        # lock_user = w_db.convert_slack_code_to_slack_id(lfl[2])
        lock_user =lfl[2]

        end_time = lfl[4] + timedelta(hours=lfl[3])
        remain_time = end_time - datetime.now()
        remain_time_str = str(int(remain_time.seconds / 3600)).zfill(2) + " : " + str(int((remain_time.seconds % 3600) / 60)).zfill(2) + " : " + str(int(remain_time.seconds % 60)).zfill(2)

        message += get_message('feat_lock_alarm.txt').format(user2=lock_user,
                                                             filename=str(lfl[1]),
                                                             remaining_time=remain_time_str)
    send_direct_message(user_slack_id_code[1], message)
    w_db.close()


def send_direct_conflict_message(conflict_flag, conflict_project, conflict_file, conflict_logic, user1_name,
                                 user2_name, user1_percentage=0, user2_percentage=0, previous_percentage=0,
                                 current_severity=0, severity_flag=0):

    if conflict_logic == "in":
        conflict_logic = ""

    # Get user slack nickname
    user1_slack_id_code = get_user_slack_id_and_code(user1_name)
    user2_slack_id_code = get_user_slack_id_and_code(user2_name)
    print("user1_slack_id_code", user1_slack_id_code)
    print("user2_slack_id_code", user2_slack_id_code)

    current_percentage = round((user1_percentage + user2_percentage) / 2, 2)

    w_db = work_database()
    direct_ignore_flag = w_db.read_direct_ignore(conflict_project, user1_slack_id_code[1])

    approve_set = w_db.read_approved_list(user1_slack_id_code[1])
    print("approve_set : ", approve_set)
    print("conflict_file : ", conflict_file)
    w_db.close()

    if direct_ignore_flag == 1:
        print("IGNORE MESSAGE BY DIRECT")
        return
    elif conflict_file in approve_set:
        print("IGNORE MESSAGE BY FILE")
        return

    message = ""

    # Already conflict
    if conflict_flag == Conflict_flag.getting_severity_percentage.value \
        or conflict_flag == Conflict_flag.lower_severity_percentage.value \
        or conflict_flag == Conflict_flag.same_severity_percentage.value:

        if conflict_flag == Conflict_flag.getting_severity_percentage.value:
            # get severity_percentage

            message += get_message('get_severe_percentage.txt').format(user2=user2_slack_id_code[1],
                                                                       filename=conflict_file,
                                                                       severity=current_percentage,
                                                                       old_severity=previous_percentage,
                                                                       severity_subtraction=round(
                                                                           current_percentage - previous_percentage, 2))

            message += "\n"

            if severity_flag == Conflict_flag.getting_severity.value:
                # get severity
                message += get_message('adverb2.txt') + " "

                if current_severity == 2:
                    message += get_message('get_severe2_add.txt').format(user2=user2_slack_id_code[1])

                elif current_severity == 3:
                    message += get_message('get_severe3_add.txt').format(user2=user2_slack_id_code[1])

            elif severity_flag == Conflict_flag.same_severity.value:
                # same severity
                message += get_message('adverb1.txt') + " "

                if current_severity == 1:
                    message += get_message('same_severity1_add.txt').format(user2=user2_slack_id_code[1])

                elif current_severity == 2:
                    message += get_message('same_severity2_add.txt').format(user2=user2_slack_id_code[1])

                elif current_severity == 3:
                    message += get_message('same_severity3_add.txt').format(user2=user2_slack_id_code[1])

            elif severity_flag == Conflict_flag.lower_severity.value:
                # lower severity
                message += get_message('adverb1.txt') + " "

                if current_severity == 1:
                    message += get_message('alleviated1_add.txt').format(user2=user2_slack_id_code[1])

                elif current_severity == 2:
                    message += get_message('alleviated2_add.txt').format(user2=user2_slack_id_code[1])

        elif conflict_flag == Conflict_flag.lower_severity_percentage.value:
            # lower_severity_percentage
            message = get_message('alleviated_percentage.txt').format(user2=user2_slack_id_code[1],
                                                                      filename=conflict_file,
                                                                      severity=current_percentage,
                                                                      old_severity=previous_percentage,
                                                                      severity_subtraction=round(
                                                                          previous_percentage - current_percentage, 2))

            message += "\n"

            if severity_flag == Conflict_flag.getting_severity.value:
                # get severity
                message += get_message('adverb1.txt') + " "

                if current_severity == 2:
                    message += get_message('get_severe2_add.txt').format(user2=user2_slack_id_code[1])

                elif current_severity == 3:
                    message += get_message('get_severe3_add.txt').format(user2=user2_slack_id_code[1])

            elif severity_flag == Conflict_flag.same_severity.value:
                # same severity
                message += get_message('adverb1.txt') + " "

                if current_severity == 1:
                    message += get_message('same_severity1_add.txt').format(user2=user2_slack_id_code[1])

                elif current_severity == 2:
                    message += get_message('same_severity2_add.txt').format(user2=user2_slack_id_code[1])

                elif current_severity == 3:
                    message += get_message('same_severity3_add.txt').format(user2=user2_slack_id_code[1])

            elif severity_flag == Conflict_flag.lower_severity.value:
                # lower severity
                message += get_message('adverb2.txt') + " "

                if current_severity == 1:
                    message += get_message('alleviated1_add.txt').format(user2=user2_slack_id_code[1])

                elif current_severity == 2:
                    message += get_message('alleviated2_add.txt').format(user2=user2_slack_id_code[1])

        elif conflict_flag == Conflict_flag.same_severity_percentage.value:
            # lower_severity_percentage
            message = ""
            if severity_flag == Conflict_flag.getting_severity.value:
                # get severity
                if current_severity == 2:
                    message += get_message('get_severe2.txt').format(user2=user2_slack_id_code[1])

                elif current_severity == 3:
                    message += get_message('get_severe3.txt').format(user2=user2_slack_id_code[1])

            elif severity_flag == Conflict_flag.same_severity.value:
                # same severity
                message += ""

            elif severity_flag == Conflict_flag.lower_severity.value:
                # lower severity
                if current_severity == 1:
                    message += get_message('alleviated1.txt').format(user2=user2_slack_id_code[1])

                elif current_severity == 2:
                    message += get_message('alleviated2.txt').format(user2=user2_slack_id_code[1])

    # First conflict
    elif conflict_flag == Conflict_flag.same_function.value:
        # same function
        message = get_message('direct_conflict.txt').format(user1=user1_slack_id_code[1],
                                                            user2=user2_slack_id_code[1],
                                                            filename=conflict_logic)

        message += " " + get_message('direct_conflict_init_severity_2.txt').format(user2=user2_slack_id_code[1])

    elif conflict_flag == Conflict_flag.same_class.value:
        # same class
        logic_list = conflict_logic.split(':')[:-1]
        con_logic_for_class = ""
        for logic in logic_list:
            con_logic_for_class = con_logic_for_class + logic + ' '
        print(con_logic_for_class)

        message = get_message('direct_conflict.txt').format(user1=user1_slack_id_code[1],
                                                            user2=user2_slack_id_code[1],
                                                            filename=con_logic_for_class)
        message += " " + get_message('direct_conflict_init_severity_1.txt').format(user2=user2_slack_id_code[1])

    elif conflict_flag == Conflict_flag.file_in.value:
        # just in
        message = get_message('direct_conflict.txt').format(user1=user1_slack_id_code[1],
                                                            user2=user2_slack_id_code[1],
                                                            filename=conflict_file)

    elif conflict_flag == Conflict_flag.direct_conflict_finished.value:
        # direct conflict solved
        if user2_slack_id_code[1] == user1_slack_id_code[1]:
            pass
        else:
            message = get_message('direct_conflict_finished.txt').format(user1=user1_slack_id_code[1],
                                                                         user2=user2_slack_id_code[1],
                                                                         filename=conflict_file)

    if message != "":
        if conflict_flag == Conflict_flag.direct_conflict_finished.value:
            send_direct_message(user1_slack_id_code[1], message, "good")
        else:
            send_conflict_button_message(user1_slack_id_code[1], message, user2_name, conflict_project, conflict_file)

    return


def send_indirect_conflict_message(conflict_flag, conflict_project, conflict_file1="", conflict_file2="", conflict_logic1="", conflict_logic2="", user1_name="", user2_name="", type = None):

    # Get user slack nickname
    user1_slack_id_code = get_user_slack_id_and_code(user1_name)
    user2_slack_id_code = get_user_slack_id_and_code(user2_name)
    print("user1_slack_id_code", user1_slack_id_code)
    print("user2_slack_id_code", user2_slack_id_code)

    w_db = work_database()
    indirect_ignore_flag = w_db.read_indirect_ignore(conflict_project, user1_slack_id_code[1])

    approve_set = w_db.read_approved_list(user1_slack_id_code[1])
    print("approve_set : ", approve_set)
    print("conflict_file : ", conflict_file1)
    w_db.close()

    if conflict_file1 in approve_set:
        print("IGNORE MESSAGE BY FILE")
        return

    if indirect_ignore_flag == 1:
        print("IGNORE MESSAGE BY INDIRECT")
        return

    message = ""

    if conflict_flag == Conflict_flag.indirect_conflict_finished.value:
        # indirect conflict solved
        if user2_slack_id_code[1] == user1_slack_id_code[1]:
            pass
        else:
            message = get_message('indirect_conflict_finished.txt').format(user1=user1_slack_id_code[1],
                                                                           filename1=conflict_file1,
                                                                           logic1=conflict_logic1,
                                                                           user2=user2_slack_id_code[1],
                                                                           filename2=conflict_file2,
                                                                           logic2=conflict_logic2)
    elif conflict_flag == Conflict_flag.indirect_conflict.value:
        # indirect conflict
        if type == 'user_call':
            if conflict_logic1 == conflict_logic2:
                message = get_message('indirect_conflict_calling_no_length.txt')
            else:
                message = get_message('indirect_conflict_calling_length.txt')
        elif type == 'user_work':
            message = get_message('indirect_conflict_working.txt')

        message = message.format(filename1=conflict_file1,
                                 filename2=conflict_file2,
                                 function1=conflict_logic1,
                                 function2=conflict_logic2,
                                 user1=user1_slack_id_code[1],
                                 user2=user2_slack_id_code[1])

    if message != "":
        if conflict_flag == Conflict_flag.indirect_conflict_finished.value:
            send_direct_message(user1_slack_id_code[1], message, "good")
        else:
            send_conflict_button_message(user1_slack_id_code[1], message, user2_name, conflict_project, conflict_file2)

    return


def send_prediction_message(project_name, user_name, probability_dict, whole_predicted_file_set):
    user_slack_id_code = get_user_slack_id_and_code(user_name)

    w_db = work_database()
    prediction_ignore_flag = w_db.read_prediction_ignore(project_name, user_slack_id_code[1])

    if prediction_ignore_flag == 1:
        print("IGNORE MESSAGE BY PREDICTION")
        return

    user_list = list(probability_dict.keys())
    user_name_list = []
    for i, user_temp in enumerate(user_list):
        slack_code, slack_id = w_db.convert_git_id_to_slack_code_id(user_temp)
        user_list[i] = "<@" + slack_code + ">"
        user_name_list[i] = slack_id

    percentage_list = list(probability_dict.values())
    file_list = list(whole_predicted_file_set)
    message = get_message('prediction_direct_conflict.txt')
    message = message.format(userlist=user_list,
                             percentagelist=percentage_list,
                             filelist=file_list)

    send_prediction_button_message(user_slack_id_code[1], message, project_name, user_name_list)


# def send_conflict_message_channel(conflict_file, conflict_logic, user1_name, user2_name):
#     user1_slack_id_code = get_user_slack_id_and_code(user1_name)
#     user2_slack_id_code = get_user_slack_id_and_code(user2_name)
#     message = ""
#
#     # same server
#     if conflict_logic == "in":
#         message = get_message('direct_conflict_channel.txt').format(user1_slack_id_code[1],
#                                                                     user2_slack_id_code[1],
#                                                                     conflict_file,
#                                                                     '')
#     else:
#         message = get_message('direct_conflict_channel.txt').format(user1_slack_id_code[1],
#                                                                     user2_slack_id_code[1],
#                                                                     conflict_file,
#                                                                     conflict_logic)
#     send_channel_message("code-conflict-chatbot", message)
#
#     return


def send_remove_lock_channel(channel, lock_file_list):
    message = get_message('feat_send_all_user_auto_unlock.txt').format(file_name=", ".join(lock_file_list)) + "\n"
    # for file_name in lock_file_list:
    #     message += "{} is unlocked from now on.\n".format(file_name)
    # send_channel_message(channel, message)
    send_all_user_message(message=message)


def channel_join_check(channel):
    slack = get_slack()

    channel_idx = -1
    channels_list_res = slack.channels.list()
    channels_list = channels_list_res.body["channels"]

    for cl_idx, cl in enumerate(channels_list):
        if cl.get("name") == channel:
            channel_idx = cl_idx

    if channel_idx == -1:
        #Do not implement yet
        print("Channel is not in Slack")
        return CHANNEL_NONEXISTENCE
    else:
        is_member = channels_list[channel_idx].get("is_member")
        if not is_member:
            print("Sayme is not join in {} Channel".format(channel))
            return CHANNEL_WITHOUT_SAYME
        else:
            return CHANNEL_WITH_SAYME


# Put channel name and message for sending chatbot message
# def send_channel_message(channel, message):
#     if message == "":
#         return
#     slack = get_slack()
#     ret_cjc = channel_join_check(channel)
#
#     if ret_cjc == CHANNEL_WITH_SAYME:
#         attachments_dict = dict()
#         attachments_dict['text'] = "%s" % (message)
#         attachments_dict['mrkdwn_in'] = ["text", "pretext"]
#         attachments = [attachments_dict]
#         slack.chat.post_message(channel="#" + channel, text=None, attachments=attachments, as_user=True)
#
#     return ret_cjc


# Send a message to everyone in the project
def send_all_user_message(message, slack_code=""):
    if message == "":
        return
    slack = get_slack()

    u_db = user_database("parent")
    all_user = u_db.search_all_slack_code(slack_code)
    u_db.close()

    for user in all_user:
        attachments_dict = dict()
        attachments_dict['text'] = "%s" % (message)
        attachments_dict['mrkdwn_in'] = ["text", "pretext"]
        attachments = [attachments_dict]
        slack.chat.post_message(channel="" + user[0], text=None, attachments=attachments, as_user=True)

    return


# Put user slack id and message for sending chatbot message
def send_direct_message(slack_code, message, color="#D3D3D3"):
    if message == "":
        return
    slack = get_slack()
    attachments_dict = dict()
    attachments_dict['text'] = "%s" % (message)
    attachments_dict['mrkdwn_in'] = ["text", "pretext"]
    attachments_dict['color'] = color
    attachments = [attachments_dict]
    slack.chat.post_message(channel="" + slack_code, text=None, attachments=attachments, as_user=True)
    return


# Lock request button message
def send_lock_request_button_message(slack_code, lock_file, lock_time):
    slack = get_slack()

    actions = [{'name': "YES", 'text': "YES", 'type': "button", 'value': lock_time},
               {'name': "NO", 'text': "NO", 'type': "button", 'value': lock_time}]

    attachments_dict = dict()
    attachments_dict['title'] = "Lock Request"
    attachments_dict['text'] = "*{}* is just unlocked. Do you want me to lock it for {} hours?".format(lock_file, lock_time)
    attachments_dict['fallback'] = "Lock Request Button Message"
    attachments_dict['callback_id'] = lock_file
    attachments_dict['actions'] = actions
    attachments_dict['color'] = "#3AA3E3"
    attachments = [attachments_dict]
    slack.chat.post_message(channel=slack_code, text=None, attachments=attachments, as_user=True)


# File selection button message
def send_file_selection_button_message(slack_code, called_same_named_dict, sentence, intent_type):
    slack = get_slack()
    attachments_dict = dict()

    for csnd_idx, (file_name, file_abs_path_list) in enumerate(called_same_named_dict.items()):
        message = ""
        actions = []

        for fapl_idx, file_abs_path in enumerate(file_abs_path_list):
            message += "%d. %s\n" % (fapl_idx + 1, file_abs_path)
            actions_dict = dict()
            actions_dict['name'] = sentence
            actions_dict['text'] = fapl_idx + 1
            actions_dict['type'] = "button"
            actions_dict['value'] = file_abs_path
            actions.append(actions_dict)

        attachments_dict['title'] = "Which file do you mean?"
        attachments_dict['text'] = "%s" % (message)
        attachments_dict['fallback'] = "File Selection Button Message"
        attachments_dict['callback_id'] = intent_type
        # attachments_dict['attachment_type'] = "warning"
        attachments_dict['actions'] = actions
        attachments_dict['color'] = "#3AA3E3"
        attachments = [attachments_dict]

        slack.chat.post_message(channel="" + slack_code, text=None, attachments=attachments, as_user=True)

    # slack = Slacker("SLACK_BOT_TOKEN")
    # response = slack.rtm.start()
    # endpoint = response.body['url']
    # ws2 = websocket.create_connection("ws://localhost:4000")
    # print("start loop")
    # while True:
    #     event = json.loads(ws2.recv())
    #     print("event", event)
    #     if event.get('type') != "message" or event.get('user') != slack_code:
    #         continue
    #     ws2.close()
    #     break


# Typo error file selection button message
def send_typo_error_button_message(slack_code,error_file_name, file_name, sentence, intent_type):
    slack = get_slack()
    attachments_dict = dict()

    message = ""

    actions = [{'name': sentence.replace(error_file_name, file_name), 'text': "YES", 'type': "button", 'value': "YES"},
               {'name': sentence, 'text': "NO", 'type': "button", 'value': "NO"}]

    attachments_dict['title'] = "I think you have typo error."
    attachments_dict['text'] = "Do you mean%s file?" % (file_name)
    attachments_dict['fallback'] = "Typo Error Button Message"
    attachments_dict['callback_id'] = intent_type
    attachments_dict['attachment_type'] = "warning"
    attachments_dict['actions'] = actions
    attachments_dict['color'] = "#3AA3E3"
    attachments = [attachments_dict]

    slack.chat.post_message(channel="" + slack_code, text=None, attachments=attachments, as_user=True)


# Git diff button message
def send_conflict_button_message(slack_code, message, user2_name, project_name, file_name):
    slack = get_slack()
    attachments_dict = dict()

    actions = [{'name': user2_name, 'text': "git diff", 'type': "button", 'value': file_name}]

    attachments_dict['title'] = ""
    attachments_dict['text'] = "%s" % (message)
    attachments_dict['fallback'] = "Git Diff Code Button Message"
    attachments_dict['callback_id'] = project_name
    attachments_dict['actions'] = actions
    attachments_dict['color'] = "warning"
    attachments = [attachments_dict]

    slack.chat.post_message(channel=slack_code, text=None, attachments=attachments, as_user=True)


# Git diff message after click a button
def send_git_diff_message(user1_name, user2_name, project_name, file_name):
    slack = get_slack()
    git_diff_code = "```" + get_git_diff_code(user2_name, project_name, file_name) + "```"
    print("send_git_diff_message", git_diff_code)

    slack.chat.post_message(channel=user1_name, text=git_diff_code, as_user=True)


# Prediction button message
def send_prediction_button_message(slack_code, message, project_name, user_list):
    slack = get_slack()
    attachments_dict = dict()

    actions = []
    actions.append({'name': 'All', 'text': 'All', 'type': "button", 'value': 'All', 'style': 'danger'})
    for user_name in user_list:
        actions_dict = dict()
        actions_dict['name'] = user_name
        actions_dict['text'] = user_name
        actions_dict['type'] = "button"
        actions_dict['value'] = user_name
        actions.append(actions_dict)

    attachments_dict['title'] = ""
    attachments_dict['text'] = "%s" % (message)
    attachments_dict['fallback'] = "Prediction Button Message"
    attachments_dict['callback_id'] = project_name
    attachments_dict['actions'] = actions
    attachments_dict['color'] = "#3AA3E3"
    attachments = [attachments_dict]

    slack.chat.post_message(channel=slack_code, text=None, attachments=attachments, as_user=True)


# Prediction list message after click a button
def send_prediction_list_message(user1_name, user2_name, project_name):
    slack = get_slack()

    # prediction_list = ["80%  Sun            counting_triangle.py",
    #                    "50%  Kathryn Choi   SquareMatrix.py",
    #                    "17%  Kathryn Choi   conflict_test/ClassAofA.py",
    #                    " 8%  Sun            conflict_test/ClassAofA.py"]
    # 띄어쓰기 formatting 해주기!

    prediction_list = []

    # Show all of prediction lists
    if user2_name == "All":
        prediction_list = ["80%  Sun            counting_triangle.py",
                           "50%  Kathryn Choi   SquareMatrix.py",
                           "17%  Kathryn Choi   conflict_test/ClassAofA.py",
                           " 8%  Sun            conflict_test/ClassAofA.py"]

    # Show prediction list of user2
    else:
        prediction_list = ["80%  Sun            counting_triangle.py",
                           " 8%  Sun            conflict_test/ClassAofA.py"]

    message = ""
    for idx, prediction in enumerate(prediction_list):
        message += "%d. %s\n" % (idx + 1, prediction)

    attachments = [{'title': user2_name, 'text': message, 'color': "#3AA3E3" }]
    slack.chat.post_message(channel=user1_name, attachments=attachments, as_user=True)