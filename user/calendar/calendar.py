import datetime
import json

#创建日程表类
class calendar :
      #初始化日程表
    def __init__(self):
        self.my_calendar = {}
        #每个日程安排为键值对结构，key为日期，value为日程内容，例如下面的示例
        #key:"2023-07-17 09:30:00"(datatime类型)
        #value:{}
        #下面是value的示例
        # {
        #事件名称 "calendar_name":"元旦节",
        #事件内容 "calendar_content":"今天是元旦节",
        #事件时间 "calendar_datetime":"2023-07-17 09:30:00"(datatime类型),
        #事件状态 "calendar_status":"未完成",
        #事件执行结果 "calendar_result":""
        # }


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



    #添加日程事件
    def add_calendar(self,calendar_name,calendar_content,calendar_datetime):
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
    
    #删除日程事件，输入事件日期与事件时间
    def delete_calendar(self,calendar_datetime):
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
    
    #修改日程事件，输入事件日期与事件时间，事件名称，事件内容
    def modify_calendar(self,calendar_datetime,calendar_name,calendar_content):
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
        
    
    #查询日程事件，输入事件日期与事件时间
    def query_calendar(self,calendar_datetime):
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
    
    #查询日程事件，输入事件名称
    def query_calendar_by_name(self,calendar_name):
        #判断日程表中是否已经存在该日程事件
        for key in self.my_calendar.keys():
            if self.my_calendar[key]["calendar_name"] == calendar_name:
                print("[DEBUG] 日程表中已成查询该日程事件")
                return self.my_calendar[key]
        print("[DEBUG] 日程表中不存在该日程事件")
        return "日程表中不存在该日程事件"


    #自动写入到本地文件中,方便debug
    def auto_write_my_calendar(self):
        #把任务库写入到本地文件中，指定编码格式为utf-8
        with open("my_calendar.json", "w", encoding="utf-8") as f:
            json.dump(self.my_calendar, f, ensure_ascii=False, indent=4)

#日程表执行器（循环自动查询日程表并提交到任务库执行，自动查询任务结果）
#原理大概是检测现在时间大于计划时间，就执行任务。
#执行结果以特定格式插入对话中，角色试一下用户和助手和函数看看。如：【系统消息】2020-01-01日程xxxxx时间任务执行结果，请告诉用户：今天是元旦节。
class calendar_executor:
    pass