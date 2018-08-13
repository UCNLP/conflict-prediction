from slacker import Slacker
import websocket
import time
import json
import random
import _thread
import os
import configparser
from chat_bot_server_dir.punctuator2.play_with_model import punctuator
from chat_bot_server_dir.punctuator2.play_with_model import model_loading
from chat_bot_server_dir.user_intent_classifier.intent_classifier import require_something_sentence
from chat_bot_server_dir.project_parser import project_parser
import nltk.data

add_ignore = []
project_structure = project_parser('UCNLP', 'client')

def make_shell_list(file):
    f = open(file,"rt",encoding="UTF8")
    text = f.read()
    text = text.split("\n")

    return text

add_ignore = make_shell_list(os.path.join(os.path.pardir,"situation_shell","add_ignore.txt"))

# Slack Definition
channel = '#code-conflict-chatbot'

user_git = dict()
user_slack = dict()

# User List Data
user_list = list()

# find slack user's name
def get_slack_display_name(id):
    try:
        slack = Slacker(token)

        # Get users list
        response = slack.users.list()
        users = response.body['members']
        for user in users:
            if not user['deleted'] and user['id'] == id:
                # print(user)
                # print(user['id'], user['name'], user['is_admin'], user['profile']['display_name'])
                return user.get('profile').get('display_name')
    except KeyError as ex:
        print('Invalid key : %s' % str(ex))

# Message Entered on Slack
def on_message(ws, message):

    # JSON Data To Message
    msg = json.loads(message)

    # Import User Data

    # Message Type is message
    if msg['type'] == 'message':
        # Message Content Convert

        rand_text = str(punctuator(msg['text'], model_list[0], model_list[1], model_list[2], model_list[3]))
        # Detect Hash Number
        if(rand_text.isdigit() and (len(rand_text) == 5)):
            with open(os.path.join(os.path.pardir, "user_data", "user_git.json"), 'r') as f1, open(os.path.join(os.path.pardir, "user_data", "user_slack.json"), 'r') as f2:
                user_git = json.load(f1)
                user_slack = json.load(f2)

                # Search User Register
                for git_user in user_git.keys():
                    # Slack id == RandomNumber ####
                    if str(user_git[git_user]) == rand_text:
                        # random number convert user id
                        # user_list[count]['slack_id'] = msg['user']
                        # user_name = list_slack(msg['user'])
                        # user_slack[msg['user']] = user_name
                        # user_git[git_user] = user_name

                        user_name = get_slack_display_name(msg['user'])
                        user_slack[user_name] = msg['user']
                        user_git[git_user] = user_name

                #
                #         # Save User Data Json file
            with open(os.path.join(os.path.pardir, "user_data", "user_git.json"), 'w') as make_file1, open(os.path.join(os.path.pardir, "user_data", "user_slack.json"), 'w') as make_file2:
                json.dump(user_git, make_file1)
                json.dump(user_slack, make_file2)

        elif '.py' in rand_text:
            for py_file in rand_text.split(' '):
                if '.py' in py_file:
                    approved_list = []
                    with open('../user_data/approved_list.json', 'r') as f:
                        approved_list = json.load(f)

                    approved_list.append(py_file)
                    attachments_dict = dict()
                    attachments_dict['text'] = add_ignore[random.randint(0, len(add_ignore)-1)] % (py_file)
                    attachments_dict['mrkdwn_in'] = ["text", "pretext"]
                    attachments = [attachments_dict]

                    slack.chat.post_message(channel="#code-conflict-chatbot", text=None, attachments=attachments, as_user=True)

                    with open('../user_data/approved_list.json', 'w') as f:
                        json.dump(approved_list,f)
                    break

        else:
            content = tokenizer.tokenize(rand_text)
            for sentence in content:
                if require_something_sentence(sentence):
                    pass
                else:
                    pass

def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    def run(*args):
        time.sleep(1)

    _thread.start_new_thread(run, ())

get_severe_shell = make_shell_list(os.path.join(os.path.pardir,"situation_shell","get_severe.txt"))
approved_shell = make_shell_list(os.path.join(os.path.pardir,"situation_shell","approved.txt"))
notify_conflict_shell = make_shell_list(os.path.join(os.path.pardir,"situation_shell","go_to_same_file.txt"))

#### MAIN ####
def load_token() :
    if not os.path.isfile("bot_server_config.ini") :
        print("ERROR :: There is no bot_server_config.ini")
        exit(2)
    else :
        config = configparser.ConfigParser()
        config.read("bot_server_config.ini")
        try :
            token=config["SLACK"]["TOKEN"]
        except :
            print("ERROR :: It is bot_server_config.ini")
            exit(2)
    return token

token = load_token()
slack = Slacker(token)

model_list = model_loading()
# nltk.download('punkt')
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

res = slack.auth.test().body



msg = [{
    'fallback': res['user'] + ' is LOG-IN!',
    'pretext': '*Connected to ' + res['team'] + '(' + channel + ')*',
    'text': 'Hello! I\'m Sayme. \nIf you need me, please call me with @Sayme first.',
    'color': '#36a64f',
    'mrkdwn_in': ['pretext']
}]

slack.chat.post_message(channel, '', attachments=msg, as_user=True)

response = slack.rtm.start()
endpoint = response.body['url']

# websocket.enableTrace(True)
ws = websocket.WebSocketApp(endpoint, on_message=on_message, on_error=on_error, on_close=on_close)
ws.on_open = on_open
ws.run_forever()
