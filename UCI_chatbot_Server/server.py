########################################################################
# Import Library
import random
import websocket
import time
import json
from flask import Flask, request
from slacker import Slacker
import thread
########################################################################

# Create app
app = Flask(__name__)

# User List
user_list = list()
working_file = dict()

@app.route("/test", methods = ["POST"])
def test():

    return "test"
# Request for Command1
@app.route("/gitDiff", methods = ["POST", "GET"])
def cmd1():

    # Get command1 content
    content = request.get_json()
    print(content)
    return "test"


# Request for Command2
@app.route("/gitLsFiles", methods = ["POST", "GET"])
def cmd2():
    # for test
    working_file['test'] = ['client.py','server.py']

    # Get command2 content
    content = request.get_json(silent=True)
    key = str(content[0]).strip()
    for keys in working_file.keys():
        if keys == key:
            continue
        for working_files in working_file[keys]:
            for new_working_files in content:
                if new_working_files in working_files:
                    token = ''
                    slack = Slacker(token)

                    attachments_dict = dict()
                    attachments_dict['text'] = "Conflict Detected!"
                    attachments_dict['mrkdwn_in'] = ["text", "pretext"]
                    attachments = [attachments_dict]

                    slack.chat.post_message(channel="#code-conflict-chatbot", text=None, attachments=attachments, as_user=True)

    print working_file

    working_file[key] = content[1:]

    return "test"


# User Search
@app.route("/userSearch", methods = ["POST"])
def userSearch():

    # Initialize sign_in_flag
    sign_in_flag = "False"

    # Get User Git ID
    content = request.get_json(silent=True)
    git_id = str(content['email'])

    print(git_id)

    # User Search
    for temp in user_list:

        # log
        print (str(temp['git_id']))

        compare_temp = str(temp['git_id'])

        # Already Sign In
        if(compare_temp == git_id):
            sign_in_flag = "True"
            break

    # User have to sign in
    if(sign_in_flag != "True"):

        # Generate Random Number
        rand_num = createRandomTemp()

        # Create User Data
        temp_dict = dict()
        temp_dict['slack_id'] = str(rand_num)
        temp_dict['git_id'] = git_id

        # Add User Data
        user_list.append(temp_dict)
        print(user_list)

        # Create JSON User Data
        json_dict = dict()
        json_dict['user'] = user_list

        print(json_dict)

        # Save User Data Json file
        with open('./user_data/user.json', 'w') as make_file:
            json.dump(json_dict, make_file)

        # Return Random Number
        sign_in_flag = str(rand_num)

    # Return Ture or Random Number
    return sign_in_flag


# Verifying User
@app.route("/verifyUser", methods = ["POST"])
def verifyUser():

    return "test"


def createRandomTemp():

    # Create Random Number
    rand_num = random.randint(10000, 99999)

    # log
    print("random Number: " + str(rand_num))

    return rand_num

# Create Random Number
@app.route("/createRandom", methods = ["GET"])
def createRandom():

    # Get Git ID
    content = request.get_json()
    git_id = content['email']

    # Create Random Number
    rand_num = random.randint(10000, 99999)

    # log
    print("random Number: " + str(rand_num))

    # Add Random Number
    rand_set.add({ 'rand_num':rand_num, 'git_id':git_id})

    return str(rand_num)


# Observe Random Number
@app.route("/observeRandom", methods = ["GET"])
def observeRandomNumber():

    return

# Observing Direct
def observeDirect():

    return

# MAIN
if __name__ == "__main__":

    # Import User Data
    with open('./user_data/user.json', 'r') as f:
        user_list = json.load(f)['user']
        print(user_list)

    # Run App
    app.run(debug=True, host="0.0.0.0", port=5009)