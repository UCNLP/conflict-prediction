import os
import re
import requests
import json
import subprocess


# File definition
# os.path.join(os.getcwd(), 'UCI_chatbot_Server')
root_dir = "C:\\Users\\jc\\Desktop\\py_test"
file_dir = []
file_name = []

# Dependency definition
file_dependency = {}
file_content_list = dict()

# Request definition
ip_addr = "127.0.0.1"
port = "8080"


# Search All Directory And Append simple file name
def search_directory(url):
    for (file_path, dir, files) in os.walk(url):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext == '.py':
                # print("%s/%s" % (file_path, filename))
                file_dir.append(os.path.join(file_path,filename))
                file_name.append(filename[:len(filename)-3])


# File Content Data Reader
def file_reader(url):

    # file open
    f = open(url)

    # Read Raw Data from file
    raw_data = f.read()

    return raw_data


# Generate File Dependency Data / File Content Data
# 1. File dependency        # { 'file path' : [ dependency file list ], 'file path2' : [ dependency file list ] }
def generate_file_dependency():

    # Read Each File
    for temp_dir in file_dir:

        # make simple_file_name
        simple_file_name = str(temp_dir).split('\\')
        simple_file_name = simple_file_name[len(simple_file_name) - 1]
        simple_file_name = simple_file_name[:-3]

        # Read Raw data
        file_content = file_reader(temp_dir).splitlines()
        temp_file_list = []

        # log
        # print temp_dir

        # Initialize class, function set
        # Initialize file dict for dependency
        in_content = list()

        # Read Each line
        for file_line in file_content:

            # Split raw line
            index = 0
            temp_line = file_line.split(' ')

            # Detect class under function
            if (file_line[0:4] != '    '):
                if file_line != '':
                    class_dep = False
                    def_dep = False

            # Read Each token
            for temp_token in temp_line:

                # Generate file dependency [keyword : import]
                if temp_token == "import":
                    import_file = temp_line[index + 1]

                    # Search import file list
                    for temp_file_dir in file_dir:
                        temp1_file_dir = str(temp_file_dir).split('\\')
                        temp1_file_dir = temp1_file_dir[len(temp1_file_dir) - 1]
                        temp1_file_dir = temp1_file_dir[:-3]

                        # if file imported => add file dependency
                        if import_file == temp1_file_dir:
                            temp_file_list.append(temp_file_dir)
                            file_dependency[temp_dir] = temp_file_list
                            break

                # Generate class dependency [ keyword : class ]
                elif temp_token == "class":

                    # Read class name
                    class_name = file_line.strip()
                    in_content.append(class_name)

                # Generate function dependency [ keyword : def ]
                elif temp_token == "def":

                    # Read function name
                    def_name = file_line.strip()
                    in_content.append(def_name)

                # index plus
                index += 1

        file_content_list[temp_dir] = in_content
        # print file_content_list


# Generate Function Class Dependency
# 1. Function dependency    # [ [ 'file name + function name', 'dependency function list' ], ['file name + function name' : 'dependency function list' ]
# 2. Class dependency       # [ [ 'file name + class name', dependency class list ], ['file name + class name', 'dependency class list' ]
def generate_func_class_dependency():

    all_dependency_list = list()

    # Read Each File
    for temp_dir in file_dir:

        # log
        # print temp_dir

        # Read Raw data
        file_content = file_reader(temp_dir).splitlines()

        content_dependency_list = []
        class_name = ""
        def_name = ""
        class_dep = False
        def_dep = False

        # Read Each line
        for file_line in file_content:

            # Split raw line
            index = 0
            temp_line = file_line.split(' ')

            # Detect class under function
            if (file_line[0:4] != '    '):
                if file_line != '':
                    class_dep = False
                    def_dep = False

            # Read Each token
            for temp_token in temp_line:

                # Generate class dependency [ keyword : class ]
                if temp_token == "class":

                    # Read class name
                    class_name = file_line.strip()

                    # String processing
                    if class_name[-1] == ':':
                        class_name = class_name[:-1].strip()

                    class_dep = True

                # Generate function dependency [ keyword : def ]
                elif temp_token == "def":

                    # Read function name
                    def_name = file_line.strip()

                    # String processing
                    def_name = def_name.split('(')[0]

                    def_dep = True

                    # class function dependency
                    if (file_line[0:4] == "    ") and (len(file_line) >= 4) and class_dep:
                        temp_list = []
                        temp_list.append(temp_dir + '|' + class_name + '|' + def_name)
                        temp_list.append(temp_dir + '|' + class_name)
                        content_dependency_list.append(temp_list)
                        all_dependency_list.append(temp_list)
                        break

                # Import function dependency
                elif re.findall(str("  "), file_line) != None:

                    # function - function call dependency
                    if def_dep:

                        # Search all directory
                        for t_dir in file_dir:

                            # Search other directory
                            if t_dir != temp_dir:

                                # Read clear function, class name
                                func_name_list = convert_func_name(file_content_list[t_dir])

                                # Search about usage of function
                                for temp_func_name in func_name_list:
                                    find_flag = temp_token.find(temp_func_name)

                                    # Find function dependency
                                    if find_flag > 0:
                                        temp_func_list = []
                                        temp_func_list.append(t_dir + '|def ' + temp_func_name)

                                        # class dependency discriptor
                                        if class_dep:
                                            temp_func_list.append(temp_dir + '|' + class_name)
                                        else:
                                            temp_func_list.append(temp_dir + '|' + def_name)

                                        content_dependency_list.append(temp_func_list)
                                        all_dependency_list.append(temp_func_list)
                                        break

                    # function - class call dependency
                    elif class_dep:

                        # Search all directory
                        for t_dir in file_dir:

                            # Search other directory
                            if t_dir != temp_dir:

                                # Read clear function, class name
                                class_name_list = convert_class_name(file_content_list[t_dir])

                                # Search about usage of function
                                for temp_class_name in class_name_list:
                                    find_flag = temp_token.find(temp_class_name)

                                    # Find Class dependency
                                    if find_flag > 0:
                                        temp_func_list = []
                                        temp_func_list.append(t_dir + '|def ' + temp_class_name)
                                        temp_func_list.append(temp_dir + '|' + class_name)
                                        content_dependency_list.append(temp_func_list)
                                        all_dependency_list.append(temp_func_list)
                                        break

            # index plus
                index += 1

        #print content_dependency_list

    return all_dependency_list


def convert_func_name(raw_name_list):

    convert_name_list = []

    for raw_name in raw_name_list:

        split_name = str(raw_name).split(' ')

        if(split_name[0] == "def"):
            temp_name_list = split_name[1].split('(')
            temp_name = temp_name_list[0]
            convert_name_list.append(temp_name)

    return convert_name_list


def convert_class_name(raw_name_list):

    convert_name_list = []

    for raw_name in raw_name_list:

        split_name = str(raw_name).split(' ')

        if(split_name[0] == "class"):
            temp_name = split_name[1]

            if(temp_name[-1] == ':'):
                temp_name = temp_name[:-1]

            convert_name_list.append(temp_name)

    print convert_name_list
    return convert_name_list


def create_edge(raw_list):

    # print "raw_list"
    # print raw_list

    for dep_obj in raw_list:
        for compare_dep in raw_list:

            if dep_obj[1] == compare_dep[0]:
                new_temp = []
                new_temp.append(dep_obj[0])
                new_temp.append(compare_dep[1])

                raw_list.append(new_temp)

    #print raw_list


# Post To Server
def postToServer(uri, json_data):

    # Create URL
    url = "http://" + ip_addr + ":" + port + uri # 80

    # Headers
    headers = {'Content-Type': 'application/json; charset=utf-8'}

    # Post To Server
    req = requests.post(url, headers=headers, data = json.dumps(json_data))

    # Log
    print(req)

    return req


# Send To Server with graph data [ [u, v], [u, v], [u, v] ]
def sendGraphInfo(root_dir_temp):

    search_directory(root_dir_temp)

    generate_file_dependency()

    raw_list = generate_func_class_dependency()
    graph_data = [ [os.path.normpath(u), os.path.normpath(v)] for (u, v) in raw_list ]

    print(graph_data)

    # Post To Server
    postToServer("/graphInfo", graph_data)


# Git clone using user URL
def gitCloneFromURL(git_url):

    cmd_line = 'git clone ' + git_url
    git_dir_name = git_url.split('/')[4]
    root_dir_temp = os.path.join(os.getcwd(), git_dir_name)

    # git clone from user git url
    git_clone_return = str(subprocess.check_output(cmd_line, shell=True)).strip()

    return root_dir_temp


if __name__ == '__main__':

    # git clone from user git url
    root_dir_temp = gitCloneFromURL("https://github.com/j21chan/py_test")

    # Send to the server with Git dependency of function and class
    sendGraphInfo(root_dir_temp)