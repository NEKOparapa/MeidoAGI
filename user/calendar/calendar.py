import datetime
import json

#创建日程表类
class Calendar :
      #初始化日程表
    def __init__(self):
        self.my_calendar = {}
        #每个日程安排为键值对结构，key为日期，value为日程内容，例如下面的示例
        #key:"2023-07-17 09:30:00"(datatime类型)
        #value:{}
        #下面是value的示例
        # {
        #事件时间 "calendar_event_datetime":"2023-07-17 09:30:00"(datatime类型),
        #事件名称 "calendar_event_objectives":"元旦节",
        #事件内容 "calendar_event_content":"今天是元旦节",
        #事件状态 "calendar_event_status":"未完成",
        #任务分步数 "event_distribution":5,
        #任务已完成进度 "event_progress":0, 
        #事件执行结果 "calendar_event_result":""
        # }
        #任务分步式列表结构示例
        self.calendar_event_content =[
        {
            "task_id": 1,
            "task_description": "获取苹果的单价",
            "function_used": True,
            "function_name": "get_the_price_of_the_item",
            "function_parameters": {"item": "苹果",
                                    "unit": "人民币"},
            "function_response": "五块人民币",
            "task_result": "一个苹果的价格是五块人民币"
        },
        {
            "task_id": 2,
            "task_description": "计算五个苹果的总价",
            "function_used": False
        }
        ]


    #调用功能函数的函数
    def call_calendar_function(self, function_name, function_arguments):

      #根据函数调用名称，调用相应的函数
      if function_name == "add_calendar_event":
          function_response = self.add_calendar_event(calendar_name=function_arguments.get("calendar_name"),calendar_content=function_arguments.get("calendar_content"),calendar_datetime = function_arguments.get("calendar_datetime"))
      elif function_name == "delete_calendar_event":
          function_response = self.delete_calendar_event(calendar_datetime=function_arguments.get("calendar_datetime"))
      elif function_name == "modify_calendar_event":
          function_response = self.modify_calendar_event(calendar_datetime=function_arguments.get("calendar_datetime"),calendar_name=function_arguments.get("calendar_name"),calendar_content=function_arguments.get("calendar_content"))
      elif function_name == "query_calendar_event":
          function_response = self.query_calendar_event(calendar_datetime=function_arguments.get("calendar_datetime"))
      elif function_name == "query_calendar_event_by_date":
            function_response = self.query_calendar_event_by_date(calendar_date=function_arguments.get("calendar_date"))
      elif function_name == "query_calendar_event_by_name":
          function_response = self.query_calendar_event_by_name(calendar_name=function_arguments.get("calendar_name"))

      return function_response



    #添加日程事件
    def add_calendar_event(self,calendar_name,calendar_content,calendar_datetime):
        #将输入的日期时间转换为datetime类型
        calendar_datetime = datetime.datetime.strptime(calendar_datetime, "%Y-%m-%d %H:%M:%S")
        #判断日程表中是否已经存在该日程事件
        if calendar_datetime in self.my_calendar.keys():
            print("[DEBUG] 日程表中已经存在该日程事件")
            return "日程表中已经存在该日程事件"
        else:
            #添加日程事件
            self.my_calendar[calendar_datetime] = {"calendar_name":calendar_name,"calendar_content":calendar_content,"calendar_datetime":calendar_datetime,"calendar_status":"未完成","calendar_result":""}
            print("[DEBUG] 日程表中已成创建该日程事件")
            self.auto_write_my_calendar()
            return "日程表中已成创建该日程事件"
        
    #添加日程事件的函数说明    
    function_add_calendar_event =   {
            "name": "add_calendar_event",
            "description": "输入事件描述，事件内容，日期时间，添加日程事件到日程表中",
            "parameters": {
                "type": "object",
                "properties": {
                    "calendar_name": {
                        "type": "string",
                        "description": "关于日程事件的描述",
                    },
                    "calendar_content": {
                        "type": "string",
                        "description": "日程事件的详细内容",
                    },
                    "calendar_datetime": {
                        "type": "string",
                        "description": "日程事件的日期时间，如2023-07-19 14:30:45",
                    },
                },
                "required": ["calendar_name","calendar_content","calendar_datetime"]
            },
        }





    #删除日程事件，输入事件日期与事件时间
    def delete_calendar_event(self,calendar_datetime):
        #将输入的日期时间转换为datetime类型
        calendar_datetime = datetime.datetime.strptime(calendar_datetime, "%Y-%m-%d %H:%M:%S")
        #判断日程表中是否已经存在该日程事件
        if calendar_datetime in self.my_calendar.keys():
            #删除日程事件
            del self.my_calendar[calendar_datetime]
            print("[DEBUG] 日程表中已成删除该日程事件")
            self.auto_write_my_calendar()
            return "日程表中已成删除该日程事件"
        else:
            print("[DEBUG] 日程表中不存在该日程事件")
            return "日程表中不存在该日程事件"

    #删除日程事件的函数说明
    function_delete_calendar_event =   {
            "name": "delete_calendar_event",
            "description": "输入事件日期与事件时间，删除日程事件",
            "parameters": {
                "type": "object",
                "properties": {
                    "calendar_datetime": {
                        "type": "string",
                        "description": "日程事件的日期时间，如2023-07-19 14:30:45",
                    },
                },
                "required": ["calendar_datetime"]
            },
        }


    #修改日程事件，输入事件日期与事件时间，事件名称，事件内容
    def modify_calendar_event(self,calendar_datetime,calendar_name,calendar_content):
        #将输入的日期时间转换为datetime类型
        calendar_datetime = datetime.datetime.strptime(calendar_datetime, "%Y-%m-%d %H:%M:%S")
        #判断日程表中是否已经存在该日程事件
        if calendar_datetime in self.my_calendar.keys():
            #修改日程事件
            self.my_calendar[calendar_datetime]["calendar_name"] = calendar_name
            self.my_calendar[calendar_datetime]["calendar_content"] = calendar_content
            self.my_calendar[calendar_datetime]["calendar_status"] = "未完成"
            print("[DEBUG] 日程表中已成修改该日程事件")
            self.auto_write_my_calendar()
            return "日程表中已成修改该日程事件"
        else:
            print("[DEBUG] 日程表中不存在该日程事件")
            return "日程表中不存在该日程事件"

    #修改日程事件的函数说明
    function_modify_calendar_event =   {
            "name": "modify_calendar_event",
            "description": "输入事件日期与事件时间，事件名称，事件内容，修改日程事件",
            "parameters": {
                "type": "object",
                "properties": {
                    "calendar_datetime": {
                        "type": "string",
                        "description": "日程事件的日期时间，如2023-07-19 14:30:45",
                    },
                    "calendar_name": {
                        "type": "string",
                        "description": "关于日程事件的描述",
                    },
                    "calendar_content": {
                        "type": "string",
                        "description": "日程事件的详细内容",
                    },
                },
                "required": ["calendar_datetime","calendar_name","calendar_content"]
            },
        }

    
    #查询日程事件，输入事件日期与事件时间
    def query_calendar_event(self,calendar_datetime):
        #将输入的日期时间转换为datetime类型
        calendar_datetime = datetime.datetime.strptime(calendar_datetime, "%Y-%m-%d %H:%M:%S")
        #判断日程表中是否已经存在该日程事件
        if calendar_datetime in self.my_calendar.keys():
            #查询日程事件
            print("[DEBUG] 日程表中已成查询该日程事件")
            return self.my_calendar[calendar_datetime]
        else:
            print("[DEBUG] 日程表中不存在该日程事件")
            return "日程表中不存在该日程事件"
      
    #查询日程事件的函数说明
    function_query_calendar_event =   {
            "name": "query_calendar_event",
            "description": "输入事件日期与事件时间，查询日程事件",
            "parameters": {
                "type": "object",
                "properties": {
                    "calendar_datetime": {
                        "type": "string",
                        "description": "日程事件的日期时间，如2023-07-19 14:30:45",
                    },
                },
                "required": ["calendar_datetime"]
            },
        }
    
    #查询日程事件，输入日期，返回该日期下的所有日程事件，按照时间顺序排列，合成列表返回
    def query_calendar_event_by_date(self,calendar_date):
        #将输入的日期转换为datetime类型
        calendar_date = datetime.datetime.strptime(calendar_date, "%Y-%m-%d")
        #判断日程表中是否已经存在该日程事件
        calendar_event_list = []
        for key in self.my_calendar.keys():
            if key.date() == calendar_date.date():
                calendar_event_list.append(self.my_calendar[key])
        if len(calendar_event_list) == 0:
            print("[DEBUG] 日程表中不存在该日程事件")
            return "日程表中不存在该日程事件"
        else:
            print("[DEBUG] 日程表中已成查询该日程事件")
            return calendar_event_list
    
    #查询日程事件的函数说明
    function_query_calendar_event_by_date =   {
            "name": "query_calendar_event_by_date",
            "description": "输入日期，返回该日期下的所有日程事件",
            "parameters": {
                "type": "object",
                "properties": {
                    "calendar_date": {
                        "type": "string",
                        "description": "日程事件的日期，如2023-01-01",
                    },
                },
                "required": ["calendar_date"]
            },
        }


    
    #查询日程事件，输入事件名称(应该使用模糊查询，待改进)
    def query_calendar_event_by_name(self,calendar_name):
        #判断日程表中是否已经存在该日程事件
        for key in self.my_calendar.keys():
            if self.my_calendar[key]["calendar_name"] == calendar_name:
                print("[DEBUG] 日程表中已成查询该日程事件")
                return self.my_calendar[key]
        print("[DEBUG] 日程表中不存在该日程事件")
        return "日程表中不存在该日程事件"
    
    #查询日程事件的函数说明
    function_query_calendar_event_by_name =   {
            "name": "query_calendar_event_by_name",
            "description": "输入事件名称，查询日程事件", 
            "parameters": {
                "type": "object",
                "properties": {
                    "calendar_name": {
                        "type": "string",
                        "description": "关于日程事件的描述",
                    },
                },
                "required": ["calendar_name"]
            },
        }

    #自动写入到本地文件中,方便debug
    def auto_write_my_calendar(self):
        #把任务库写入到本地文件中，指定编码格式为utf-8
        with open("my_calendar.json", "w", encoding="utf-8") as f:
            json.dump(self.my_calendar, f, ensure_ascii=False, indent=4)

