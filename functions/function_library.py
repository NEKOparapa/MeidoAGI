import json




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
        self.add_function("1", "get_current_weather", "输入位置与温度单位，获取给定位置的当前天气", self.function_get_current_weather, "1")
        self.add_function("2", "get_n_day_weather_forecast", "输入位置、温度单位和天数，获取该位置未来N天的天气预报", self.function_get_n_day_weather_forecast, "1")
        self.add_function("3", "get_the_price_of_the_item", "输入物品名词，金额单位，获取物品的单个价格", self.function_get_the_price_of_the_item, "1")

    #功能1：获取给定位置的当前天气--------------------------------------------
    def get_current_weather(self, location, unit):
        """Get the current weather in a given location"""
        weather_info = {
            "location": location,
            "temperature": "31",
            "unit": unit,
            "forecast": "晴天",
        }
        return json.dumps(weather_info)

    #定义AI调用函数的信息，包括函数名字，描述，参数，参数类型，参数范围，参数描述，必需给出的参数
    function_get_current_weather = {
                "name": "get_current_weather", #函数名字
                "description": "输入位置与温度单位，获取给定位置的当前天气", #函数描述

                "parameters": { "type": "object", # 暂时不知道干嘛，都有先带着
                                "properties": {"location": {"type": "string",
                                                            "description": "需要查询的城市，例如南宁、北京", #参数描述
                                                            },
                                                "unit": {"type": "string",  #参数类型
                                                        "enum": ["摄氏度", "华氏度"], #参数范围
                                                        "description": "使用的温度单位，从用户位置推断出来。" #参数描述
                                                        },
                                                },
                                "required": ["location","unit"], #必需给出的参数
                                },
                    }


    #功能2：获取N天的天气预报--------------------------------------------
    def get_n_day_weather_forecast(self, location, unit, num_days):
        """Get an N-day weather forecast"""
        weather_info = {
            "location": location,
            "temperature": "28",
            "unit": unit,
            "num_days": num_days,
            "forecast": "持续雨天",
        }
        return json.dumps(weather_info)



    function_get_n_day_weather_forecast  = {
            "name": "get_n_day_weather_forecast",
            "description": "输入位置、温度单位和天数，获取该位置未来N天的天气预报",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "需要查询的城市，例如南宁、北京",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["摄氏度", "华氏度"],
                        "description": "使用的温度单位，从用户位置推断出来。",
                    },
                    "num_days": {
                        "type": "integer",
                        "description": "需要预报的天数",
                    }
                },
                "required": ["location", "unit", "num_days"]
            },
        }


    #功能3：获取单个物品的价格--------------------------------------------
    def get_the_price_of_the_item(self, item,unit):
        price_info = {
            "item": item,
            "price": "12",
            "unit": unit
        }
        return json.dumps(price_info)



    function_get_the_price_of_the_item  = {
            "name": "get_the_price_of_the_item",
            "description": "输入物品名词，金额单位，获取物品的单个价格",
            "parameters": {
                "type": "object",
                "properties": {
                    "item": {
                        "type": "string",
                        "description": "需要查询的物品，例如苹果、香蕉",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["人民币", "美元"],
                        "description": "使用的金额单位，根据用户要求或者从用户语言推断出来。",
                    }
                },
                "required": ["item", "unit"]
            },
        }




    #调用功能函数的函数
    def call_function(self, function_name, function_arguments):

        #根据函数调用名称，调用相应的函数
        if function_name == "get_the_price_of_the_item":
            function_response = self.get_the_price_of_the_item(item=function_arguments.get("item"),unit=function_arguments.get("unit"),)

        elif function_name == "get_current_weather":
            function_response = self.get_current_weather(location=function_arguments.get("location"),unit=function_arguments.get("unit"),)

        elif function_name == "get_n_day_weather_forecast":
            function_response = self.get_n_day_weather_forecast(location=function_arguments.get("location"),unit=function_arguments.get("unit"),num_days=function_arguments.get("num_days"),)
        
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



    #输入单个函数id，获取id对应的功能函数说明（AI调用）的内容，并以列表返回
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