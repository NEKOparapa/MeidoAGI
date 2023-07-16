import json


from toolkits.expansion_toolkit.shopping_toolkit import shopping_toolkit
from toolkits.expansion_toolkit.weather_toolkit import weather_toolkit


#————————————————————————————————————————功能函数库————————————————————————————————————————
class Function_library():
    #初始化功能函数库
    def __init__(self):
        #功能函数库
        self.function_library = {}
        # 每个函数为键值对结构，key为函数id（int），value为函数内容，例如下面的示例
        # key:0 
        # value:{
        #功能函数id "function_id":"0",
        #功能函数名字 "function_name":"",
        #功能函数描述 "function_description":"",
        #功能函数说明（AI调用） "function_ai_call":{},
        #功能函数权限 "function_permission":"0",
        # }
        
        #添加功能函数
        self.add_function("1", "get_current_weather", "输入位置与温度单位，获取给定位置的当前天气", weather_toolkit.function_get_current_weather, "1")
        self.add_function("2", "get_n_day_weather_forecast", "输入位置、温度单位和天数，获取该位置未来N天的天气预报", weather_toolkit.function_get_n_day_weather_forecast, "1")
        self.add_function("3", "get_the_price_of_the_item", "输入物品名词，金额单位，获取物品的单个价格", shopping_toolkit.function_get_the_price_of_the_item, "1")




    #调用功能函数的函数
    def call_function(self, function_name, function_arguments):

        #根据函数调用名称，调用相应的函数
        if function_name == "get_the_price_of_the_item":
            function_response = shopping_toolkit.get_the_price_of_the_item(item=function_arguments.get("item"),unit=function_arguments.get("unit"),)

        elif function_name == "get_current_weather":
            function_response = weather_toolkit.get_current_weather(location=function_arguments.get("location"),unit=function_arguments.get("unit"),)

        elif function_name == "get_n_day_weather_forecast":
            function_response = weather_toolkit.get_n_day_weather_forecast(location=function_arguments.get("location"),unit=function_arguments.get("unit"),num_days=function_arguments.get("num_days"),)
        
        return function_response



    #添加功能函数到库中的函数
    def add_function(self, function_id, function_name, function_description, function_ai_call, function_permission):
        #构建功能函数结构
        functions = {
            "function_id": function_id,
            "function_name": function_name,
            "function_description": function_description,
            "function_ai_call": function_ai_call,
            "function_permission": function_permission
        }
        #写入任务
        self.function_library[int(function_id)] = functions



    #根据函数权限，获取相应的全部功能函数说明（AI调用）
    def get_function_by_permission(self, permission):
        function_list = []
        #遍历功能函数库，注意是字典结构，所以需要用到items()方法
        for function_id, function in self.function_library.items():
            if function["function_permission"] == permission:
                #只获取功能函数说明（AI调用）的内容
                function_ai_call = function["function_ai_call"].copy()
                function_list.append(function_ai_call)
        return function_list


    #输入函数名字，获取对应的功能函数说明（AI调用）的内容
    def get_function_by_name(self, function_name):
        #遍历功能函数库，注意是字典结构，所以需要用到items()方法
        for function_id, function in self.function_library.items():
            if function["function_name"] == function_name:
                #只获取功能函数说明（AI调用）的内容
                function_ai_call = function["function_ai_call"].copy()
                return function_ai_call



    #输入单个函数id，获取id对应的功能函数说明（AI调用）的内容
    def get_function_by_id(self, function_id):
        #转换成int类型
        function_id = int(function_id)

        #根据id获取功能函数
        function = self.function_library[function_id]

        #只获取功能函数说明（AI调用）的内容
        function_ai_call = function["function_ai_call"].copy()
        return function_ai_call



    #输入包含函数id的列表，获取id对应的功能函数说明（AI调用）的内容，并以列表返回
    def get_function_by_id_list(self, function_id_list):
        function_list = []
        #遍历功能函数库，注意是字典结构，所以需要用到items()方法
        for function_id, function in self.function_library.items():
            #需要对输入列表中的id进行遍历
            for id in function_id_list:
                if function["function_id"] == id:
                    #只获取功能函数说明（AI调用）的内容
                    function_ai_call = function["function_ai_call"].copy()
                    function_list.append(function_ai_call)
        return function_list

        
    #根据输入函数权限，获取全部功能函数描述，和对应的函数id，作为两个不同的列表返回
    def get_all_function(self,function_permission):
        function_id_list = []
        function_description_list = []
        #遍历功能函数库，注意是字典结构，所以需要用到items()方法
        for function_id, function in self.function_library.items():
            if function["function_permission"] == function_permission:
                function_id_list.append(function["function_id"])
                function_description_list.append(function["function_description"])
        return function_id_list,function_description_list