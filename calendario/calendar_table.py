import datetime
import json
import os
import sys

#创建日程表类
class Calendar :
      #初始化日程表
    def __init__(self):
        self.my_calendar = {}
        #每个日程安排为键值对结构，key为日期(datatime类型)，value为日程内容，例如下面的示例
        #任务分步式列表结构示例
        self.example_task_list =[
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
        #key示例
        example_key =datetime.datetime.strptime("2023-07-23 01:30:00", "%Y-%m-%d %H:%M:%S")
        #value示例
        example_value =   {
            "task_datetime":"2023-07-23 01:30:00",  #事件时间
            "task_objectives":"计算五个苹果的价格",  #事件目标 
            "task_list":self.example_task_list,    #事件内容
            "task_distribution":2,                 #事件分步数
            "task_progress":1,                     #事件已完成进度
            "task_status":"已完成",                #事件状态 
            "notification_status":1,               #通知状态 
            }



        #在文件夹下寻找my_calendar.json文件，如果存在则读取json文件
        try:
            script_dir = os.path.dirname(os.path.abspath(sys.argv[0])) 
            if os.path.exists(os.path.join(script_dir, "cache", "my_calendar.json")):
                with open(os.path.join(script_dir, "cache", "my_calendar.json"), "r", encoding="utf-8") as f:
                    my_calendar_json = json.load(f)
                    # 遍历字典，将日期字符串转换为 datetime 对象
                    for key, value in my_calendar_json.items():
                        # 将日期字符串转换为 datetime 对象
                        key_obj = datetime.datetime.strptime(key, "%Y-%m-%d %H:%M:%S")
                        
                        # 更新字典中的值为 datetime 对象
                        self.my_calendar[key_obj] = value
                    print("[DEBUG] 已成功读取用户日程表内容！！)",'\n')
        except:
            print("[DEBUG] 读取用户日程表内容失败！！",'\n')



    #调用日程表下工具的函数
    def call_calendar_tool(self, tool_name, tool_arguments):
        #根据函数调用名称，调用相应的函数
        try:
            if tool_name == "add_scheduled_task":
                tool_response = self.add_scheduled_task(task_datetime = tool_arguments.get("task_datetime"),task_objectives=tool_arguments.get("task_objectives"),task_list=tool_arguments.get("task_list"))
            elif tool_name == "delete_scheduled_task":
                tool_response = self.delete_scheduled_task(task_datetime=tool_arguments.get("task_datetime"))
            elif tool_name == "query_scheduled_task_by_datetime":
                tool_response = self.query_scheduled_task_by_datetime(task_datetime=tool_arguments.get("task_datetime"))
            elif tool_name == "query_scheduled_task_by_date":
                    tool_response = self.query_scheduled_task_by_date(task_date=tool_arguments.get("task_date"))
            elif tool_name == "query_scheduled_task_by_name":
                tool_response = self.query_scheduled_task_by_name(task_objectives=tool_arguments.get("task_objectives"))

        except Exception as e:
            print("[ERROR] 调用日程表工具时出错,无法成功运行，错误信息为：",e,'\n')
            tool_response = "[ERROR] 调用日程表工具时出错,无法成功运行，错误信息为：" + str(e)
        
        
        return tool_response



    #添加定时任务
    def add_scheduled_task(self,task_objectives,task_list,task_datetime):
        #将输入的日期时间转换为datetime类型
        if type(task_datetime) != datetime.datetime:
            task_datetime = datetime.datetime.strptime(task_datetime, "%Y-%m-%d %H:%M:%S")
        #判断日程表中是否已经存在该定时任务
        if task_datetime in self.my_calendar.keys():
            print("[DEBUG] 日程表中已经存在该定时任务")
            return "日程表中已经存在该定时任务"
        else:

            #将还是字符串格式的任务列表里的true和false转换为布尔值
            task_list = task_list.replace("true","True")
            task_list = task_list.replace("false","False")

            #处理任务列表，把任务列表转换为列表变量
            task_list = eval(task_list)
            #计算任务列表的长度
            scheduled_task_list_length = len(task_list)
            
            #构建key-value结构的定时任务
            task_key = task_datetime

            task_value =   {
            "task_datetime":str(task_datetime),
            "task_objectives":task_objectives,
            "task_list":task_list,
            "task_distribution":scheduled_task_list_length,
            "task_progress":0,
            "task_status":"未完成",
            "notification_status":"未通知",
            }

            #将定时任务添加到日程表中
            self.my_calendar[task_key] = task_value

            print("[DEBUG] 日程表中已成创建该定时任务")
            self.auto_write_my_scheduled()
            return "日程表中已添加该定时任务"
        
    #添加定时任务的工具调用规范    
    function_add_scheduled_task =   {
        "type": "function",
        "function": {
                    "name": "add_scheduled_task",
                    "description": "添加定时任务到日程表中，系统按照该日期时间自动执行，并自动通知结果",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_objectives": {
                                "type": "string",
                                "description": "定时任务目标",
                            },
                            "task_list": {
                                "type": "list",
                                "description": """分步式任务列表,输入列表数据，数据结构如：
                                                [{"task_id": 1,"task_description": "获取苹果的单价","function_used": True,"function_name": "get_the_price_of_the_item",
                                                "function_parameters": {"item": "苹果","unit": "人民币"}}]"""},
                            "task_datetime": {
                                "type": "string",
                                "description": "执行的日期时间，如2023-07-19 14:30:45",
                            },
                        },
                        "required": ["task_objectives","task_list","task_datetime"]
                    },
                }
    }


    #删除定时任务，输入事件日期与事件时间
    def delete_scheduled_task(self,task_datetime):
        #将输入的日期时间转换为datetime类型
        if type(task_datetime) != datetime.datetime:
            task_datetime = datetime.datetime.strptime(task_datetime, "%Y-%m-%d %H:%M:%S")
        #判断日程表中是否已经存在该定时任务
        if task_datetime in self.my_calendar.keys():
            #删除定时任务
            del self.my_calendar[task_datetime]
            print("[DEBUG] 日程表中已删除该定时任务")
            self.auto_write_my_scheduled()
            return "日程表中已删除该定时任务"
        else:
            print("[DEBUG] 日程表中不存在该定时任务")
            return "日程表中不存在该定时任务"

    #删除定时任务的工具调用规范
    function_delete_scheduled_task =   {
        "type": "function",
        "function": {
                    "name": "delete_scheduled_task",
                    "description": "输入任务的日期与时间，删除相应的定时任务",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_datetime": {
                                "type": "string",
                                "description": "定时任务的日期时间，如2023-07-19 14:30:45",
                            },
                        },
                        "required": ["task_datetime"]
                    },
                }
    }

    
    #查询定时任务，输入日期与时间，精确查找
    def query_scheduled_task_by_datetime(self,task_datetime):
        #将输入的日期时间转换为datetime类型
        if type(task_datetime) != datetime.datetime:
            task_datetime = datetime.datetime.strptime(task_datetime, "%Y-%m-%d %H:%M:%S")
        #判断日程表中是否已经存在该定时任务
        if task_datetime in self.my_calendar.keys():
            #查询定时任务
            print("[DEBUG] 日程表中已查询该定时任务")

            self.query_result = {}
            self.query_result = self.my_calendar[task_datetime].copy()

            return self.query_result
        else:
            print("[DEBUG] 日程表中不存在该定时任务")
            return "日程表中不存在该定时任务"
      
    #查询定时任务的工具调用规范
    function_query_scheduled_task_by_datetime =   {
        "type": "function",
        "function": {
                    "name": "query_scheduled_task_by_datetime",
                    "description": "输入日期与时间，查询相应的定时任务",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_datetime": {
                                "type": "string",
                                "description": "定时任务的日期时间，如2023-07-19 14:30:45",
                            },
                        },
                        "required": ["task_datetime"]
                    },
                }
    }
    
    #查询定时任务，输入日期，返回该日期下的所有定时任务，范围查找
    def query_scheduled_task_by_date(self,task_date):
        #如果不是datetime类型，将输入的日期转换为datetime类型
        if type(task_date) != datetime.datetime:
            task_date = datetime.datetime.strptime(task_date, "%Y-%m-%d")
        #判断日程表中是否已经存在该定时任务
        scheduled_task_list = []
        for key in self.my_calendar.keys():
            if key.date() == task_date.date():
                #新建一个字典，存储查询结果
                self.query_result = {}
                self.query_result= self.my_calendar[key].copy()
                #把查询结果添加到列表中
                scheduled_task_list.append(self.query_result)
                
        if len(scheduled_task_list) == 0:
            #print("[DEBUG] 日程表中不存在该天的定时任务")
            return "日程表中不存在该天的定时任务"
        else:
            print("[DEBUG] 日程表中已查询到该天的定时任务")
            return scheduled_task_list
    
    #查询定时任务的工具调用规范
    function_query_scheduled_task_by_date =   {
        "type": "function",
        "function": {
                    "name": "query_scheduled_task_by_date",
                    "description": "输入日期，返回该天的所有定时任务",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_date": {
                                "type": "string",
                                "description": "定时任务的日期，如2023-01-01",
                            },
                        },
                        "required": ["task_date"]
                    },
                }
    }

    #查询定时任务，输入事件名称，返回相关事件，模糊查找
    def query_scheduled_task_by_name(self,scheduled_name):
        #判断日程表中是否已经存在该定时任务
        for key in self.my_calendar.keys():
            if self.my_calendar[key]["scheduled_name"] == scheduled_name:
                print("[DEBUG] 日程表中已查询该定时任务")
                return self.my_calendar[key]
        print("[DEBUG] 日程表中不存在该定时任务")
        return "日程表中不存在该定时任务"
    
    #查询定时任务的工具调用规范
    function_query_scheduled_task_by_name =   {
        "type": "function",
        "function": {
                    "name": "query_scheduled_task_by_name",
                    "description": "输入事件名称，查询相关的定时任务", 
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "scheduled_name": {
                                "type": "string",
                                "description": "关于定时任务的描述",
                            },
                        },
                        "required": ["scheduled_name"]
                    },
                }
    }


    #根据时间key与任务id，录入函数调用结果，任务执行结果与更新任务进度
    def update_task_progress(self,task_datetime,task_id,function_response,task_result):
        #将输入的日期时间转换为datetime类型
        if type(task_datetime) != datetime.datetime:
            task_datetime = datetime.datetime.strptime(task_datetime, "%Y-%m-%d %H:%M:%S")
        #根据任务缓存id，找到相应任务
        scheduled_task = self.my_calendar[task_datetime]
        #根据任务id，找到相应任务
        for task_unit in scheduled_task["task_list"]:
            if task_unit["task_id"] == task_id:
                #把函数调用结果与任务执行结果添加到任务列表中,如果列表中已经有了，就更新，没有就添加新键值对
                if function_response :
                    task_unit["function_response"] = str(function_response)
                if task_result:
                    task_unit["task_result"] = task_result


        #更新任务进度
        self.my_calendar[task_datetime]["task_progress"] = task_id

        #更新定时任务
        self.my_calendar[task_datetime] = scheduled_task

        #自动写入到本地文件中
        self.auto_write_my_scheduled()

    
    #根据时间key，回退一步任务进度
    def delete_task_progress(self,task_datetime,task_progress):
        #将输入的日期时间转换为datetime类型
        if type(task_datetime) != datetime.datetime:
            task_datetime = datetime.datetime.strptime(task_datetime, "%Y-%m-%d %H:%M:%S")
        #根据任务缓存id，找到相应任务
        scheduled_task = self.my_calendar[task_datetime]
        #根据任务进度，把函数调用结果与任务执行结果写入任务列表
        for task_unit in scheduled_task["task_list"]:
            if task_unit["task_id"] == task_progress:
                #删除函数调用结果与任务执行结果
                del task_unit["function_response"]
                del task_unit["task_result"]
                #回退任务进度
                scheduled_task["task_progress"] = task_progress - 1

        #自动写入到本地文件中
        self.auto_write_my_scheduled()


    #根据时间key，获取定时任务完成状态
    def get_task_status(self,task_datetime):
        #将输入的日期时间转换为datetime类型
        if type(task_datetime) != datetime.datetime:
            task_datetime = datetime.datetime.strptime(task_datetime, "%Y-%m-%d %H:%M:%S")
        #根据任务缓存id，找到相应任务
        scheduled_task = self.my_calendar[task_datetime]
        #获取任务状态
        scheduled_task_status = scheduled_task["task_status"]

        return scheduled_task_status


    #根据时间key，改变定时任务完成状态
    def update_task_status(self,task_datetime,scheduled_task_status):

        ##如果key不是datetime类型，将输入的日期时间转换为datetime类型
        if type(task_datetime) != datetime.datetime:
            task_datetime = datetime.datetime.strptime(task_datetime, "%Y-%m-%d %H:%M:%S")
        #根据任务缓存id，找到相应任务
        scheduled_task = self.my_calendar[task_datetime]
        #更新任务状态
        scheduled_task["task_status"] = scheduled_task_status

        #自动写入到本地文件中
        self.auto_write_my_scheduled()

    #根据时间key，改变定时任务通知状态
    def update_task_notification_status(self,task_datetime,task_notification_status):

        ##如果key不是datetime类型，将输入的日期时间转换为datetime类型
        if type(task_datetime) != datetime.datetime:
            task_datetime = datetime.datetime.strptime(task_datetime, "%Y-%m-%d %H:%M:%S")
        #根据任务缓存id，找到相应任务
        scheduled_task = self.my_calendar[task_datetime]
        #更新任务状态
        scheduled_task["notification_status"] = task_notification_status

        #自动写入到本地文件中
        self.auto_write_my_scheduled()

    #自动写入到本地文件中,方便debug
    def auto_write_my_scheduled(self):
        #新建一个字典，用于写入到本地文件中
        self.my_calendar_copy = {}

        #遍历原字典的每项，把datetime类型的key转换为字符串类型，写入到新字典中
        for key in self.my_calendar.keys():
            #把datetime类型的key转换为字符串类型
            self.my_calendar_copy[key.strftime("%Y-%m-%d %H:%M:%S")] = self.my_calendar[key].copy()

        #获取当前脚本的路径
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0])) 
        #拼接文件路径
        file_path = os.path.join(script_dir, "cache", "my_calendar.json")

        #把任务库写入到本地文件中，指定编码格式为utf-8
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.my_calendar_copy, f, ensure_ascii=False, indent=4)