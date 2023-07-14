

class User_information_database:
    def __init__(self):
        #用户基本信息
        self.user_name = ''
        self.user_email = ''
        self.user_phone_number = ''
        self.user_address = ''

        #用户爱好信息
        self.user_hobby = ''


        #用户讨厌信息
        self.user_hate = '' 


        #用户行为信息
        self.user_action = '' 


        #用户其他信息
        self.user_other = ''



    def get_user_name(self):
        return self.user_name

    def get_user_password(self):
        return self.user_password

    def get_user_email(self):
        return self.user_email

    def get_user_phone_number(self):
        return self.user_phone_number

    def get_user_address(self):
        return self.user_address

    def set_user_name(self, user_name):
        self.user_name = user_name

    def set_user_password(self, user_password):
        self.user_password = user_password
