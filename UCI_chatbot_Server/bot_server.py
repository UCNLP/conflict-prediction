# Import Library
from slacker import Slacker
import websocket
import thread
import time
import json

# Slack Definition
channel = '#code-conflict-chatbot'
token = 'xoxb-151102038320-397292596885-Nv3wRxgdo5DNbwM29yjXQgMd'
slack = Slacker(token)
CMDCHAR = '?'
CMD_LIST = ['work', 'home', 'cal']

# User List Data
user_list = list()

# find slack user's name
def list_slack(id):
    try:
        slack = Slacker(token)

        # Get users list
        response = slack.users.list()
        users = response.body['members']
        for user in users:
            if not user['deleted'] and user['id'] == id:
                # print(user['id'], user['name'], user['is_admin'], user['is_owner'])
                return user['name']
    except KeyError as ex:
        print('Invalid key : %s' % str(ex))

# Message Entered on Slack
def on_message(ws, message):

    # JSON Data To Message
    msg = json.loads(message)

    # log
    print(msg)

    # Import User Data

    # Message Type is message
    if msg['type'] == 'message':

        # Message Content Convert
        rand_text = str(msg['text'])

        # Detect Hash Number
        if(rand_text.isdigit() and (len(rand_text) == 5)):
            with open('./user_data/user_git.json', 'r') as f1, open('./user_data/user_slack.json','r') as f2:
                user_git = json.load(f1)
                user_slack = json.load(f2)
                # Search User Register

                for git_user in user_git.keys():
                    # Slack id == RandomNumber ####
                    if str(user_git[git_user]) == rand_text:
                        # random number convert user id
                        # user_list[count]['slack_id'] = msg['user']
                        user_name = list_slack(msg['user'])
                        user_slack[msg['user']] = user_name
                        user_git[git_user] = user_name
                #
                #         # Save User Data Json file
                with open('./user_data/user_git.json', 'w') as make_file1, open('./user_data/user_slack.json', 'w') as make_file2:
                    json.dump(user_git, make_file1)
                    json.dump(user_slack, make_file2)

def on_error(ws, error):
    print error


def on_close(ws):
    print "### closed ###"


def on_open(ws):
    def run(*args):
        time.sleep(1)

    thread.start_new_thread(run, ())


#### MAIN ####



res = slack.auth.test().body


msg = [{
    'fallback': res['user'] + ' is LOG-IN!',
    'pretext': '*Connected to ' + res['team'] + '(' + channel + ')*',
    'text': 'bot Usage : ' + CMDCHAR + '{' + ','.join(CMD_LIST) + '}\nbot Help : ' + CMDCHAR + 'help',
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
