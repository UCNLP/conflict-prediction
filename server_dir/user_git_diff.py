class user_git_diff:

    def __init__(self, content):
        self.content = content

        for proj_name_temp in self.content.keys():
            self.proj_name = proj_name_temp

        for user_name_temp in self.content[self.proj_name].keys():
            self.user_name = user_name_temp

    def get_proj_name(self):
        return self.proj_name

    def get_user_name(self):
        return self.user_name

    def get_working_data(self):

        # working_list = [ ["file_name", "logic_name"], ["file_name", "logic_name"], ... ]
        working_list = list()

        temp_work_data_dict = self.content[self.proj_name][self.user_name]

        for file_name in temp_work_data_dict.keys():
            temp_work = list()

            logic_list = temp_work_data_dict[file_name]

            for temp_logic in logic_list:
                temp_work.append(file_name)
                temp_work.append(temp_logic[0]) # temp_logic[0] = logic_name

            working_list.append(temp_work)

        return working_list