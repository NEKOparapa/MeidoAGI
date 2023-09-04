  # coding:utf-8
import datetime
import re
import yaml
import threading
import sys
import time
import openai #需要安装库pip install openai
import json
import os
import tiktoken #需要安装库pip install tiktoken
import chromadb #需要安装库pip install chromadb 
from chromadb.utils import embedding_functions

from flask import Flask, request, jsonify  #需要安装库pip install flask

#导入其他脚本
from toolkits import function_library
from calendario import calendar_table  #库名冲突了，就随便用一个了
from vits import TTS_vits,ATM_vits

# 获取当前工作目录，之前项目使用os.path.dirname(os.path.abspath(__file__))来获取路径，但打包后路径不正确
script_dir = os.path.dirname(os.path.abspath(sys.argv[0])) 
print("[INFO] 当前工作目录是:",script_dir,'\n') 


#————————————————————————————————————————日程表执行器————————————————————————————————————————
class Calendar_executor:
    def __init__(self):
        pass

    #循环检查日程表，并自动执行日程表中的任务
    def run (self): 
        while 1 :
            print("[DEBUG]日程表执行器正在检查日程表~",'\n')
            #获取当前时间
            now_time = datetime.datetime.now()
            #输入当天的年月日，获取日程表当天的全部事件
            schedule_list = my_calendar.query_scheduled_task_by_date(now_time)
            #如果日程表是列表类型，说明当天有事件
            if type(schedule_list) == list:
                #遍历日程表当天的全部事件,如果事件的执行时间小于当前时间和状态是未完成，就执行事件
                print("[DEBUG]日程表执行器正在检查日程表中需要执行的任务~",'\n')
                for task in schedule_list:
                    #如果事件的执行时间小于当前时间和状态是未完成，就执行事件
                    if datetime.datetime.strptime(task['task_datetime'], "%Y-%m-%d %H:%M:%S")< now_time and task['task_status'] == '未完成':
                        print("[DEBUG]已发现需要执行的日程安排",'\n')
                        #获取事件状态
                        task_status = task['task_status']

                        while task_status == "未完成" :
                            print("[DEBUG]日程表执行器正在执行日程表任务:",task['task_datetime'],'\n')

                            #执行任务，并添加执行错误重试机制
                            while 1:
                                try:
                                    self.execute_unit_task_AI_agent(task['task_datetime'])
                                    break
                                except Exception as e:
                                    print("[DEBUG]日程表执行器执行任务出现错误，正在重试, 错误信息：",e,'\n')

                                    pass

                            #审查任务，并添加执行错误重试机制
                            while 1:
                                try:
                                    self.review_unit_task_AI_agent(task['task_datetime'])
                                    break
                                except Exception as e:
                                    print("[DEBUG]日程表执行器审查任务出现错误，正在重试, 错误信息：",e,'\n')
                                    pass

                            #重新获取事件状态
                            task_status = my_calendar.get_task_status(task['task_datetime'])

            else :
                print("[DEBUG]日程表执行器没有发现需要执行的日程安排",'\n')

            #每隔10s检查一次日程表
            print("[DEBUG]日程表执行器正在休息中，等待下次检查",'\n')
            time.sleep(10)



    #执行单元任务的AI代理
    def execute_unit_task_AI_agent(self,task_datetime):

        print("[DEBUG]开始执行单元任务！！！！！！！！！！！！！！！！！！")

        #任务目标示例
        task_goal_example = '''我现在有70块，想买5个苹果，想知道买完后还剩多少钱'''
        #任务列表示例
        task_list_example = ''' 
        [
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
        '''
        #执行任务结果示例
        task_result_example = '''
        根据任务列表，任务id为2的任务描述是"计算五个苹果的总价"。已知一个苹果的价格是五块人民币（来自任务id为1的执行结果），那么我们可以计算五个苹果的总价。

        五个苹果的总价为：5（苹果单价）* 5（苹果数量）= 25。

        任务结果输出为json格式：

        ```json
        {
        "task_id": 2,
        "task_result": "五个苹果的总价是25块人民币"
        }
        ```
        '''
        #根据日期时间，获取具体任务，需要重新获取任务，因为任务进度已经更新
        task = my_calendar.query_scheduled_task_by_datetime(task_datetime)

        #获取任务目标
        task_objectives = task["task_objectives"]
        #获取任务列表
        task_list = task["task_list"]
        #获取任务进度
        task_progress = task["task_progress"]
        #获取任务执行id
        task_id = task_progress + 1


        #根据任务执行id与任务列表，获取当前任务需要到的函数id
        functions_list = []
        for unit_task in task_list:
            #如果任务id与当前任务执行id相同
            if unit_task["task_id"] == task_id:
                #如果任务需要使用函数
                if unit_task["function_used"] == True:
                    #获取函数名字
                    function_name = unit_task["function_name"]
                    #获取函数调用说明
                    function_ai_call = extended_function_library.get_function_by_name(function_name)
                    #将函数调用说明添加到函数列表中
                    functions_list.append(function_ai_call)
                else :
                    #如果任务不需要使用函数，那么函数列表为空
                    functions_list = "none functions"


        #构建系统提示语句
        prompt = (
        f"你是一个专业的任务执行AI，请根据任务目标、 分步任务列表与所指定的任务id，完成对应的该步任务。"
        f"分步任务列表是按时间顺序排列，请根据前面任务执行结果，函数调用结果，进行推理说明，输出该步任务的结果，任务结果以json格式输出,并以json代码块标记。"
        f"任务目标示例###{task_goal_example}###"
        f"分步任务列表示例###{task_list_example}###"
        f"执行任务结果示例###{task_result_example}###"
        f"当前任务目标是：###{task_objectives}###，当前分步任务列表是：###{task_list}###，如果需要使用到函数，仅使用为您提供的函数###{functions_list}###。"
        )

        #构建分步任务
        ai_task = f"你需要执行的任务id是{task_id}。"

        #构建对话
        messages = [{"role": "system", "content": prompt },
                {"role": "user", "content":  ai_task}]

        print("[DEBUG] 次级执行AI请求发送内容为：",messages,'\n')

        #如果函数列表为空
        if functions_list == "none functions":
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0613",
                messages=messages ,
                temperature=0
            )
        #如果函数列表不为空
        else :
            #向模型发送用户查询以及它可以访问的函数
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0613",
                messages=messages ,
                temperature=0,
                functions=functions_list,  #关于调用函数说明内容可以放在这里，也可以放在上面的content中，AI都会识别并使用
                function_call="auto" 
            )           

        # 将字典转换为JSON字符串，并保留非ASCII字符
        json_str = json.dumps(response, ensure_ascii=False)
        # 将JSON字符串中的Unicode编码内容转换为UTF-8编码
        utf8_str = json_str.encode('utf-8')
        # 将字节串转换为字符串
        str_content = utf8_str.decode('utf-8')
        print("[DEBUG] 次级执行AI全部回复内容为：",str_content,'\n')


        #解析回复,并自动调用函数，重新发送请求，直到回复中不再有函数调用
        function_response,task_result = self.parse_response(response,messages,functions_list)


        # 从任务结果示例中提取JSON部分
        json_str = re.search(r'```json(.*?)```', task_result, re.S).group(1)
        # 将JSON字符串转换为字典变量
        task_result_dict = json.loads(json_str)
        # 从字典变量中提取任务执行结果
        task_result_new = task_result_dict["task_result"]

        #更新任务进度 
        my_calendar.update_task_progress(task['task_datetime'],task_id,function_response,task_result_new)

        print("[DEBUG] 次级AI单元任务执行结果为：",task_result,'\n')
        print("[DEBUG] 该单元任务执行结束！！！！！！！！！！！！！！！！！！",'\n')



    #审查单元任务的AI代理（审查单元任务的输入输出是否正确，正确就录入任务数据库，错误就返回信息到任务数据库）
    def review_unit_task_AI_agent(self,task_datetime):

        print("[DEBUG]开始审查单元任务！！！！！！！！！！！！！！！！！！")

        #任务目标示例
        task_goal_example = '''我现在有100块，想买一个苹果，一个香蕉，一个橘子，想知道买完后还剩多少钱'''

        #任务列表示例
        task_list_example = ''' 
        [
        {
            "task_id": 1,
            "task_description": "获取苹果的单价",
            "function_used": True,
            "function_name": "get_the_price_of_the_item",
            "function_parameters": {
            "item": "苹果",
            "unit": "人民币"
            },
            "function_response": "5块人民币",
            "task_result": "一个苹果的价格是五块人民币"
        },
        {
            "task_id": 2,
            "task_description": "获取香蕉的单价",
            "function_used": True,
            "function_name": "get_the_price_of_the_item",
            "function_parameters": {
            "item": "香蕉",
            "unit": "人民币"
            },
            "function_response": "10块人民币",
            "task_result": "一个香蕉的价格是五块人民币"
        }
        ]
        '''

        #审查任务结果示例
        task_result_example = '''
        根据您提供的任务列表，我将审查任务ID为2的任务。任务目标是计算买一个苹果、一个香蕉、一个橘子后剩余的钱数。

        任务2的描述是 "获取香蕉的单价"，功能函数已被正确使用（“get_the_price_of_the_item”函数），参数也正确（item为"香蕉"，unit为"人民币"）。函数的响应是"10块人民币"。

        但是，在当前任务结果中，任务2的结果出现错误。任务结果为：“一个香蕉的价格是五块人民币”，实际的任务结果应该是：“一个香蕉的价格是十块人民币”。

        审查结果如下：

        ```json
        {
        "task_id": 2,
        "review_result": "incorrect",
        "correct_task_result": "一个香蕉的价格是十块人民币"
        }
        ```

        任务2的结果不正确，请更正后继续。
        '''

        #根据日期时间，获取具体任务，需要重新获取任务，因为任务进度已经更新
        task = my_calendar.query_scheduled_task_by_datetime(task_datetime)

        #获取任务目标
        task_objectives = task["task_objectives"]
        #获取任务列表
        task_list = task["task_list"]
        #获取任务进度
        task_progress = task["task_progress"]
        #获取任务审查id
        task_id = task_progress 

        #审查AI挂载的函数功能列表
        functions_list = []
        #根据任务审查id与任务列表，获取当前任务需要到的函数id
        for unit_task in task_list:
            #如果任务id与当前任务审查id相同
            if unit_task["task_id"] == task_id:
                #如果任务需要使用函数
                if unit_task["function_used"] == True:
                    #获取函数名字
                    function_name = unit_task["function_name"]
                    #获取函数调用说明
                    function_ai_call = extended_function_library.get_function_by_name(function_name)
                    #将函数调用说明添加到函数列表中
                    functions_list.append(function_ai_call)
                else :
                    #如果任务不需要使用函数，那么函数列表为空
                    functions_list = "none functions"
    

        #构建系统提示语句
        prompt = (
        f"你是一个专业的任务执行结果审查AI，请根据任务目标、分步任务列表与所指定的任务id，审查该步任务是否被正确执行。"
        f"分步任务列表是按时间顺序排列，请根据前面任务执行结果，进行推理说明，审查该步任务的执行结果，将审查结果以json格式输出,并以json代码块标记。”"
        f"任务目标示例：###{task_goal_example}###"
        f"分步任务列表示例：###{task_list_example}###"
        f"审查结果示例：###{task_result_example}###"
        f"当前任务目标是：###{task_objectives}###，当前分步任务列表是：###{task_list}###，如果需要使用到函数，仅使用为您提供的函数：###{functions_list}###。"
        )


        #指定审查任务id
        task_review = f"你需要审查的任务id是{task_progress }。"

        messages = [{"role": "system", "content": prompt },
                {"role": "user", "content":  task_review}]

        print("[DEBUG] 次级审查AI请求发送内容为：",messages,'\n')

        #如果函数列表为空
        if functions_list == "none functions":
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0613",
                messages=messages ,
                temperature=0
            )
        #如果函数列表不为空
        else :
            #向模型发送用户查询以及它可以访问的函数
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0613",
                messages=messages ,
                temperature=0,
                functions=functions_list,  #关于调用函数说明内容可以放在这里，也可以放在上面的content中，AI都会识别并使用
                function_call="auto"
            ) 


        # 将字典转换为JSON字符串，并保留非ASCII字符
        json_str = json.dumps(response, ensure_ascii=False)
        # 将JSON字符串中的Unicode编码内容转换为UTF-8编码
        utf8_str = json_str.encode('utf-8')
        # 将字节串转换为字符串
        str_content = utf8_str.decode('utf-8')
        print("[DEBUG] 次级审查AI回复内容为：",str_content,'\n')


        #解析回复,并自动调用函数，重新发送请求，直到回复中不再有函数调用
        function_response,review_result = self.parse_response(response,messages,functions_list)

        # 从任务结果示例中提取JSON部分
        json_str = re.search(r'```json(.*?)```', review_result, re.S).group(1)
        # 将JSON字符串转换为字典变量
        review_result_dict = json.loads(json_str)
        # 从字典变量中提取任务审查结果
        review_result_new = review_result_dict["review_result"]

        if review_result_new == "correct":
            print("[DEBUG] 任务执行结果正确~",'\n')

            #如果任务进度等于任务分步列表长度，说明任务已经完成
            if task_progress == task["task_distribution"]:
                print("[DEBUG] 该任务列表已经全部完成~",'\n')
                my_calendar.update_task_status(task['task_datetime'],"已完成")
        
        elif review_result_new == "incorrect":
            #提取正确结果
            correct_task_result = review_result_dict["correct_task_result"]
            #直接回退进度
            my_calendar.delete_task_progress(task['task_datetime'],task_progress)

            print("[DEBUG] 任务执行结果错误~",'\n')

        print("[DEBUG] 任务执行结果审查结束~",'\n')


    #执行与审查AI的解析回复函数
    def parse_response(self,response,messages,functions_list):

        #提取AI回复内容中message部分
        message = response["choices"][0]["message"]

        #存储调用功能函数里的函数回复
        function_response = 'null' #以免没有函数调用时，无法返回函数调用结果

        while message.get("function_call"):
            print("[DEBUG] 次级AI正在申请调用函数~",'\n')

            #获取函数调用名称
            function_name = message["function_call"]["name"]
            #获取函数调用参数
            function_arguments = message["function_call"]["arguments"]
            #获取函数调用附加回复
            function_content = message['content']

            #将函数输入参数转换为字典格式
            function_arguments = json.loads(function_arguments)

            #调用函数,获得函数调用结果
            function_response = extended_function_library.call_function(function_name,function_arguments)

            print("[DEBUG] 函数调用附加说明：",function_content,'\n')
            print("[DEBUG] 调用函数名字为：",function_name,'传入参数为：',function_arguments,'函数调用结果为：',function_response,'\n')

            #把ai申请调用函数动作与函数调用结果拼接到对话历史中
            messages.append({"role": "assistant",
                           "content": function_content ,
                           "function_call": {"name": function_name,
                                             "arguments": str(function_arguments)} #将函数输入参数转换为字符串格式

                            })
            messages.append({"role": "function","name": function_name ,"content": function_response})

            print("[DEBUG] 次级AI正在重新发送请求~",'\n')
            print("[DEBUG] 次级AI请求发送内容为：",messages,'\n')

            #如果函数列表为空
            if functions_list == "none functions":
                Ai_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-0613",
                    messages=messages ,
                    temperature=0
                )
            #如果函数列表不为空
            else :
                #向模型发送用户查询以及它可以访问的函数
                Ai_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-0613",
                    messages=messages ,
                    temperature=0,
                    functions=functions_list,  #关于调用函数说明内容可以放在这里，也可以放在上面的content中，AI都会识别并使用
                    function_call="auto"
                ) 

            # 将字典转换为JSON字符串，并保留非ASCII字符
            json_str = json.dumps(Ai_response, ensure_ascii=False)
            # 将JSON字符串中的Unicode编码内容转换为UTF-8编码
            utf8_str = json_str.encode('utf-8')
            # 将字节串转换为字符串
            str_content = utf8_str.decode('utf-8')
            print("[DEBUG] 次级AI接口回复内容为：",str_content,'\n')


            #再次提取AI回复内容中message部分
            message = Ai_response["choices"][0]["message"]


        #获取AI回复内容
        content = message['content']
        return function_response,content


#————————————————————————————————————————主AI功能函数库————————————————————————————————————————
class Main_AI_function_library(): 
    #初始化功能函数库
    def __init__(self):
        #功能函数库
        self.function_library = {}
        #功能函数库的结构为字典结构
        #key为整数变量与功能函数id相同，但为数字id： 0
        #value为字典结构，存储功能函数的信息：{
        #功能函数id "function_id":str,
        #功能函数名字 "function_name":str,
        #功能函数描述 "function_description":str,
        #功能函数说明（AI调用） "function_ai_call":{},
        #功能函数权限 "function_permission":str",
        # }
        #添加功能函数
        #self.add_function("0", self.function_test_function, "0")
        self.add_function("1", self.function_create_a_task_list, "0")
        self.add_function("2", self.function_search_related_functions,"0")
        self.add_function("3", self.function_query_function_class, "0")




    #测试函数------------------------------------------------
    def test_function(self):
        print("测试函数中")
        calendar_executor.run()

        return "测试函数执行完成"
    
    #测试函数说明（AI调用）
    function_test_function =   {
            "name": "test_function",
            "description": "测试用函数（当主人说需要调用时，才能调用）",
            "parameters": {
                "type": "object",
                "properties": {
                    "switch": {
                        "type": "string",
                        "description": "调用该测试函数，则输入on",
                    }
                },
                "required": ["switch"]
            },
        }



    #搜索拓展工具库中的工具函数------------------------------------------------
    def  search_related_functions(self, function_description):
        #查询向量库，获取相似度最高前N个文本描述
        results = collection.query(
            query_texts=function_description,
            n_results=3,
            include=[ "documents",  "distances"])
        
        print("[DEBUG]语义搜索到的功能函数：",results,'\n')
        #提取关联的函数id，注意返回的是字典结构，但key对应的value是嵌套列表结构，比如ids键对应的值为[['0','1','2']]
        function_id_list = results['ids'][0]  # 获取ids键的值
        print("[DEBUG]提取到的功能函数id：" ,function_id_list,'\n')

        #根据函数id，获取相应的功能函数说明（AI调用）的内容
        function_ai_call_list = extended_function_library.get_function_by_id_list(function_id_list)
        print("[DEBUG]搜索到的功能函数说明（AI调用）：" ,function_ai_call_list,'\n')

        return function_ai_call_list
        
    #搜索拓展工具库中的工具函数说明（AI调用）
    function_search_related_functions =   {
            "name": "search_related_functions",
            "description": "根据用户需要到的函数功能的详细描述，进行语义搜索，将最可能有关的的3个功能函数返回",
            "parameters": {
                "type": "object",
                "properties": {
                    "function_description": {
                        "type": "string",
                        "description": "关于函数功能的详细描述",
                    }
                },
                "required": ["function_description"]
            },
        }

    #查询日程表的工具函数------------------------------------------------
    def  query_function_class(self, function_class):
        #创建存储函数说明的列表
        function_ai_call_list = []

        if function_class == "添加类":
            #将添加类的功能函数说明添加到函数列表中
            function_ai_call_list.append(my_calendar.function_add_scheduled_task)
        elif function_class == "删除类":
            #将删除类的功能函数说明添加到函数列表中
            function_ai_call_list.append(my_calendar.function_delete_scheduled_task)
        elif function_class == "更改类":
            #将更改类的功能函数说明添加到函数列表中
            function_ai_call_list.append(my_calendar.function_modify_scheduled_task)
        elif function_class == "查询类":
            #将查询类的功能函数说明添加到函数列表中
            function_ai_call_list.append(my_calendar.function_query_scheduled_task_by_datetime)
            function_ai_call_list.append(my_calendar.function_query_scheduled_task_by_date)


        return function_ai_call_list
        
    #查询日程表的工具函数说明（AI调用）
    function_query_function_class =   {
            "name": "query_function_class",
            "description": "日程表拥有对日程表任务进行添加，删除，查询的三大类功能，输入需要调用的功能类，返回该类下所有功能函数的调用说明",
            "parameters": {
                "type": "object",
                "properties": {
                    "function_class": {
                        "type": "string",
                        "description": "需要调用的日程表功能类",
                        "enum": ["添加类","删除类","查询类"], 
                    }
                },
                "required": ["function_class"]
            },
        }

    #根据任务目标创建分步式任务的AI代理------------------------------------------------
    def create_a_task_list(self,task_objectives):

        #任务目标示例 
        task_objectives_example = '''我现在有100块，请帮我计算一下五个苹果的价格,买完五个苹果后，我还剩多少钱？'''
        #任务列表格式示例
        task_list_example = ''' 据用户的任务目标，我们需要创建一个包含以下步骤的任务列表：

        1. 理解任务目标：
        - 用户在当前有100块钱。
        - 用户想知道五个苹果的价格。
        - 用户想知道购买五个苹果后剩余多少钱。

        2. 创建任务列表：
        1. 使用函数`get_the_price_of_the_item`，输入物品名称为"苹果"，金额单位为"人民币"，获取苹果的单价。
        2. 将获取到的苹果单价乘以5，得到五个苹果的总价。
        3. 将用户当前的钱数减去五个苹果的总价，得到购买五个苹果后剩余的钱数。    

        以下是符合要求的任务列表JSON数组：
        ```json
        [
        {
            "task_id": 1,
            "task_description": "获取苹果的单价",
            "function_used": True,
            "function_name": "get_the_price_of_the_item",
            "function_parameters": {
            "item": "苹果",
            "unit": "人民币"
            }
        },
        {
            "task_id": 2,
            "task_description": "计算五个苹果的总价",
            "function_used": False
        },
        {
            "task_id": 3,
            "task_description": "计算购买五个苹果后剩余的钱数",
            "function_used": False
            }
        }
        ]
        ```
        '''
        #次级AI挂载的函数功能列表
        functions_list = []
        #从数据库获取权限为1的函数功能列表，根据id，再从ai函数数据库读取数据，作为次级ai挂载函数功能列表
        functions_list = extended_function_library.get_function_by_permission("1")

        #构建prompt
        prompt = (
        f"你是一个专业的任务创建AI，请根据用户提出的任务目标，创建一个实现该目标的JSON数组的任务列表。"
        f"根据最终目标创建每一步任务，每步任务应该详细说明，每步任务应该尽量使用库中的功能函数完成，当前功能函数库为###{functions_list}###。"
        f"确保所有任务ID按时间顺序排列。第一步始终是关于任务目标的理解，以及拆分任务的推理说明，尽可能详细。"
        f"任务目标示例：###{task_objectives_example}###"
        f"任务列表示例：###{task_list_example}###"
        )

        #构建messages
        messages = [{"role": "system", "content": prompt },
                {"role": "user", "content":  task_objectives}]


        #向模型发送用户查询以及它可以访问的函数
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages ,
        )

        #返回任务列表
        task_list = response["choices"][0]["message"]['content']
        return task_list

    #配套的供AI申请调用的函数说明（AI调用）
    function_create_a_task_list = {
            "name": "create_a_task_list",
            "description": "输入事件任务目标，次级AI会创建分步式任务列表，并返回",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_objectives": {
                        "type": "string",
                        "description": "关于事件任务目标的详细描述",
                    }
                },
                "required": ["task_objectives"]
            },
        }




    #添加功能函数
    def add_function(self, function_id,function_ai_call, function_permission):

        function_name = function_ai_call["name"]
        function_description = function_ai_call["description"]

        #构建功能函数结构
        functions = {
            "function_id": function_id,
            "function_name": function_name,
            "function_description": function_description,
            "function_ai_call": function_ai_call,
            "function_permission": function_permission
        }
        #写入数据库
        self.function_library[int(function_id)] = functions


    #根据函数权限，获取相应的全部功能函数说明
    def get_function_by_permission(self, permission):
        function_list = []
        #遍历功能函数库，注意是字典结构，所以需要用到items()方法
        for function_id, function in self.function_library.items():
            if function["function_permission"] == permission:
                #只获取功能函数说明（AI调用）的内容
                function_ai_call = function["function_ai_call"].copy()
                function_list.append(function_ai_call)
        return function_list

        
#————————————————————————————————————————主AI对话记忆库————————————————————————————————————————
class Ai_memory:
    #初始化，创建实例时，输入历史文件路径
    def __init__(self,file_path):
        #文件路径
        self.file_path = file_path
        #存储可发送的对话历史的列表
        self.conversation_history = []
        #存储完整的对话历史的列表
        self.conversation_history_all = []

        #在文件夹下寻找conversation_history.json文件，如果存在则读取json文件（增加错误跳过语句）
        try:
            if os.path.exists(os.path.join(self.file_path, "conversation_history.json")):
                with open(os.path.join(self.file_path, "conversation_history.json"), "r", encoding="utf-8") as f:
                    self.conversation_history = json.load(f)
        except:
            print("[DEBUG] 读取对话历史文件失败！！！！！！！！！！！！！)",'\n')

        #在文件夹下寻找conversation_history_all.json文件，如果存在则读取json文件（增加错误跳过语句）
        try:
            if os.path.exists(os.path.join(self.file_path, "conversation_history_all.json")):
                with open(os.path.join(self.file_path, "conversation_history_all.json"), "r", encoding="utf-8") as f:
                    self.conversation_history_all = json.load(f)
        except:
            print("[DEBUG] 读取完整对话历史文件失败！！！！！！！！！！！！！)",'\n')


    #对话历史文件检查函数
    def check_conversation_history(self):
        pass

    #获取对话历史
    def read_log(self):
        return self.conversation_history

    #记录对话历史
    def log_message(self,role,function_name,function_arguments,content):

        #用户内容格式参考
        self.user_content_structure = {"role": "user", "content": "What's the weather like in Boston?"}


        #AI调用函数格式参考
        self.function_call_structure = {"role": "assistant",
                                        "content": None ,
                                        "function_call": {
                                                        "name": "get_current_weather",
                                                        "arguments": "{\n  \"location\": \"Boston\",\n  \"unit\": \"celsius\"\n}"
                                                          }
                                        }

        #函数调用结果格式参考
        self.function_return_structure = {"role": "function",
                                           "name": "get_current_weather",
                                           "content":  {
                                                        "location": "Boston",
                                                        "temperature": "72",
                                                        "unit": "fahrenheit",
                                                        "forecast": ["sunny", "windy"],
                                                        }}

        #AI回复格式参考
        self.AI_content_structure = {"role": "assistant", "content": "The current weather in Boston is sunny and windy with a temperature of 72 degrees Fahrenheit."}


        #如果是用户输入消息
        if role == "user":
            The_message = {"role": "user", "content": content}

        #如果是函数调用
        elif role == "function_call":
            The_message = {"role": "assistant",
                           "content": content ,
                           "function_call": {"name": function_name,
                                             "arguments": function_arguments}

                        }
        #如果是函数调用结果
        elif role == "function_return":
            #如果content是列表，表明需要记录的是搜索功能函数的结果
            if isinstance(content,list):
                #使用新列表变量，来保存，避免原列表被修改
                content_copy = []

                #将content_copy转化成字符串变量，避免请求时格式错误
                content_copy = json.dumps(content)
            #如果是字典，表明需要记录的是功能函数的结果
            elif isinstance(content,dict):
                #使用新字典变量，来保存，避免原字典被修改
                content_copy = {}

                #将content_copy转化成字符串变量，避免请求时格式错误
                content_copy = json.dumps(content)

            else:
                content_copy = content

            The_message = {"role": "function","name": function_name ,"content": content_copy}

        #如果是AI通常回复
        elif role == "assistant":
            The_message = {"role": "assistant", "content": content}

        #将对话记录到可发送的对话历史的列表
        self.conversation_history.append(The_message)
        #将对话记录到完整的对话历史的列表
        self.conversation_history_all.append(The_message)


        #计算系统提示语句的tokens数
        self.num_tokens_prompt = self.num_tokens_from_string(ai_request.prompt)
        print("[DEBUG] 系统提示语句tokens数为：",self.num_tokens_prompt,"个",'\n')
        #计算对话历史的总tokens数
        self.num_tokens_history = self.num_tokens_from_messages(self.conversation_history)
        print("[DEBUG] 对话历史tokens数为：",self.num_tokens_history,"个",'\n')
        #计算挂载函数列表的tokens数
        str_content = str(ai_request.default_functions_list)
        self.num_tokens_functions= self.num_tokens_from_string(str_content)
        #print("[DEBUG] 当前挂载的内容为：",ai_request.default_functions_list,'\n')
        print("[DEBUG] 挂载函数tokens数为：",self.num_tokens_functions,"个",'\n')


        #如果大于最大tokens数，则进行总结记忆，压缩对话历史
        if (self.num_tokens_prompt  + self.num_tokens_history + self.num_tokens_functions )  > 4000:

            #总结记忆，压缩对话历史
            print("[DEBUG] 对话历史tokens数超过4080，正在总结记忆，压缩对话历史~",'\n')
            self.conversation_history = self.compress_memory(self.conversation_history,1)


        #将对话记录变量以utf-8格式写入json文件到指定文件夹中
        with open(os.path.join(self.file_path, "conversation_history.json"), "w", encoding="utf-8") as f:
            json.dump(self.conversation_history, f, ensure_ascii=False, indent=4)

        #将完整的对话记录变量以utf-8格式写入json文件到指定文件夹中
        with open(os.path.join(self.file_path, "conversation_history_all.json"), "w", encoding="utf-8") as f:
            json.dump(self.conversation_history_all, f, ensure_ascii=False, indent=4)

    #计算消息列表内容的tokens的函数
    def num_tokens_from_messages(self,messages, model="gpt-3.5-turbo-0613"):
        """Return the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model in {
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4",
            "gpt-4-0613",
            "gpt-4-32k",
            "gpt-4-32k-0613",
            }:
            tokens_per_message = 3
            tokens_per_name = 1
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                #如果value是字符串类型才计算tokens，否则跳过，因为AI在调用函数时，会在content中回复null，导致报错
                if isinstance(value, str):
                    num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    #计算字符串内容的tokens的函数
    def num_tokens_from_string(self,string: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = len(encoding.encode(string))
        return num_tokens


    #总结记忆，压缩对话历史函数
    def compress_memory(self,dialog_history,k = 1):
        #对话历史示例
        dialog_history_example = """[{'role': 'user', 'content': '你好啊'}, {'role': 'assistant', 'content': '你好！有什么我可以帮助你的吗？'}, 
        {'role': 'user', 'content': '你在干嘛'}, 
        {'role': 'assistant', 'content': '作为您的AI女仆 ，我在等待您的指示和问题，以便帮助您解答疑惑或完成任务。请告诉我您需要什么帮 助。'}, 
        {'role': 'user', 'content': '帮我写一篇文章，关于我和我亲爱的爸爸'}, 
        {'role': 'assistant', 'content': '当然可以帮您写一篇文章关于您和您亲爱的爸爸的文章。在开始之前，我需要一些更详细的信息来编写您想要的内容。以下是一些问题 ，您可以回答其中一些或提供更多信息：\n\n1. 您想要介绍您和您爸爸之间的关系吗？比如是一个亲密的关系，或者您和您爸爸之间有特别的经历或故事。\n2. 您认为您爸爸的哪些特点或品质让您钦佩或感激？\n3. 您和您爸爸之间的共同爱好或活动是什么？\n4. 有没有什么特别的时刻或活动，您和您爸爸一起度过的时光让您难以忘怀？\n5. 您 想要突出强调的其他方面，比如您们的相似之处或相互支持的关系。\n\n请提供以上问 题的答案，或者提供更多细节，我将尽力为您编写一篇关于您和您亲爱的爸爸的文章。'}, 
        {'role': 'user', 'content': '我的爸爸是非常体贴的人，共同爱好是下棋'}]"""

        #对话历史总结示例
        summary_resultst_example = """根据给出的对话历史，可以总结出以下信息：
        ```json
        {
        "summary": "主人想让AI女仆帮忙写一篇关于主人和主人父亲的文章。AI女仆提出了一系列问题，包括介绍主人和主人父亲之间的关系、主人父亲的品质、主人和主人父亲之间的共同爱好或活动、特别的时刻或活动、以及其他想要突出强调的方面。主人回答了其中的一些问题，表示自己和父亲之间的共同爱好是下棋。"
        }
        ```
        """

        #构建系统提示语句
        prompt = (
        f"你是一名专业的记录员，你将接收到关于主人和AI女仆的对话历史，主人被标记为user，AI女仆被标记为assistant，而被标记为function的是工具调用返回结果。"
        f"你的任务是提取对话历史的主要信息并总结它。你必须将总结的信息呈现为json格式,并以json代码块标记。"
        f"请注意，你必须尽可能准确地提取信息，并确保你的总结简洁而全面。你还必须确保你的总结符合上述格式规定，以便于后续处理和分析。"
        f"对话历史示例###{dialog_history_example}###"
        f"总结结果示例###{summary_resultst_example}###"
        )


        #保存对话历史列表倒数2k个元素，即最新的k对对话内容
        conversation_end = dialog_history[-(2*k):]

        #构建需要总结的对话内容
        dialog_history.pop(0) #除去列表变量第一个元素，即系统提示语句
        dialog_history_copy = dialog_history[:-(2*k)]#去除列表中倒数2k个元素，即最新的k对对话内容

        print("[DEBUG] 需要总结的对话内容为：",dialog_history_copy,'\n')


        #构建分步任务
        ai_task = f"你需要总结的内容是###{dialog_history_copy}###"

        #构建对话
        messages = [{"role": "system", "content": prompt },
                {"role": "user", "content":  ai_task}]

        print("[DEBUG] 发送需要总结的内容为：",messages,'\n')


        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=messages ,
            temperature=0
        )


        # 将字典转换为JSON字符串，并保留非ASCII字符
        json_str = json.dumps(response, ensure_ascii=False)
        # 将JSON字符串中的Unicode编码内容转换为UTF-8编码
        utf8_str = json_str.encode('utf-8')
        # 将字节串转换为字符串
        str_content = utf8_str.decode('utf-8')
        print("[DEBUG] AI总结全部内容为：",str_content,'\n')


        # 从回复中提取message部分
        task_result =  response["choices"][0]["message"][ "content"]
        print("[DEBUG] AI总结消息内容为：",task_result,'\n')


        # 从任务结果示例中提取JSON部分
        json_str = re.search(r'```json(.*?)```', task_result, re.S).group(1)
        # 将JSON字符串转换为字典变量
        task_result_dict = json.loads(json_str)
        # 从字典变量中提取任务执行结果
        task_result_new = task_result_dict["summary"]
        print("[DEBUG] 总结AI提取内容为：",task_result_new,'\n')


        #将提取的内容格式化
        The_summary = {"role": "user", "content": "【system message】"+task_result_new}

        #重新构建对话历史
        dialog_history_new = []
        dialog_history_new.append(The_summary)
        #提取每个元素，添加到新列表中，以免记录格式错误
        for i in conversation_end:
            dialog_history_new.append(i)

        print("[DEBUG] 重新构建的对话历史内容为：",dialog_history_new,'\n')

        return dialog_history_new


#————————————————————————————————————————主AI对话请求器————————————————————————————————————————
class Ai_Request:
    def __init__(self):

        #主AI挂载的函数功能列表
        self.default_functions_list = []
        #获取主AI默认挂载函数功能列表
        self.default_functions_list = main_function_library.get_function_by_permission("0")

        #构建系统提示语句
        self.prompt = '''当前对话的用户是你的主人，你现在必须扮演主人的AI女仆，你的任务是利用功能函数库来帮助主人解答疑惑和完成主人交代的任务。你要自主解答或调用函数来解决，且仅使用为你提供的函数。
        如果主人要创建一个日程事件，请遵循以下步骤：
        1. 如果主人提供的信息较少或模糊，请确保通过提问来获取尽可能详细的信息。
        2. 在确定主人事件的细节后，请务必再次询问主人是否愿意将事件委托给下级AI生成分步式任务列表。在得到主人的肯定回答后，调用相应的函数，将事件详细描述发给下级AI。
        3. 获得分步式任务列表后，交由主人审查，询问主人是否满意。如果主人不满意，你可以再次调用相应的函数，继续生成分步式任务列表。
        4. 如果主人满意，并确认愿意后，询问主人设定事件的日期与时间。
        4. 最后获取并调用日程表的添加类函数，根据日期时间，事件目的，分布式任务列表，将该事件添加到日程表中。
        '''

    #输入用户消息，向AI发送请求,并取得回复
    def make_request(self,conversationLogger):


        #获取对话历史
        conversation_history = conversationLogger.read_log()

        #获取系统当前日期时间
        now = datetime.datetime.now()
        #添加到系统提示语句前面
        self.new_prompt = "【现实当前时间】："+now.strftime('%Y-%m-%d %H:%M:%S')+'\n'+self.prompt

        #复制对话历史到新变量中，避免原变量被修改
        new_conversation_history = conversation_history.copy()
        #添加系统提示语句到对话历史最前面
        new_conversation_history.insert(0,{"role": "system", "content": self.new_prompt}) #在列表最前面插入元素

        print('[DEBUG] 主AI请求发送的内容是：',new_conversation_history,'\n')

        #向AI发送请求
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=new_conversation_history,
            functions=self.default_functions_list,  #关于调用函数说明内容可以放在这里，也可以放在上面的content中，AI都会识别并使用
            function_call="auto"
            )

        # 从回复中提取token部分,并输出
        try:
            prompt_tokens_used = int(response["usage"]["prompt_tokens"]) #本次请求花费的tokens
            print("[DEBUG] 主AI请求花费的tokens数为：",prompt_tokens_used,"个",'\n')
        except Exception as e:
            prompt_tokens_used = 0
        try:
            completion_tokens_used = int(response["usage"]["completion_tokens"]) #本次回复花费的tokens
            print("[DEBUG] 主AI回复花费的tokens数为：",completion_tokens_used,"个",'\n')
        except Exception as e:
            completion_tokens_used = 0

        # 将字典转换为JSON字符串，并保留非ASCII字符
        json_str = json.dumps(response, ensure_ascii=False)
        # 将JSON字符串中的Unicode编码内容转换为UTF-8编码
        utf8_str = json_str.encode('utf-8')
        # 将字节串转换为字符串
        str_content = utf8_str.decode('utf-8')

        print('[DEBUG] 主AI回复内容：',str_content,'\n')

        return response


#————————————————————————————————————————主AI回复解析器————————————————————————————————————————
class Ai_Parser:
    def __init__(self):
        pass
    
    #解析回复
    def parse_response(self,response):

        #提取AI回复内容中message部分
        message = response["choices"][0]["message"]

        while message.get("function_call"):
            #尝试调用函数
            try:
                #设置函数调用状态码,以便检查函数调用是否正常运行
                status_code = 0

                #获取函数调用名称
                function_name = message["function_call"]["name"]
                #获取函数调用参数
                function_arguments = message["function_call"]["arguments"]
                #获取函数调用附加回复
                function_content = message['content']

                #设置函数调用状态码为1，表示函数调用仍正常运行
                status_code = 1
                print("[DEBUG] 主AI正在申请调用函数~  调用函数附加说明：",function_content,'\n')
                print("[DEBUG] 调用的函数名字为：",function_name,'输入参数为：',function_arguments,'\n')

                #记录一下AI的函数申请调用回复
                ai_memory.log_message("function_call",function_name,function_arguments,function_content)


                #将函数输入参数转换为字典格式
                function_arguments = json.loads(function_arguments)
                #设置函数调用状态码为2，表示函数调用仍正常运行
                status_code = 2


                #调用测试用函数
                if function_name == "test_function":
                    function_response = main_function_library.test_function()

                #调用搜索相关函数的功能函数
                elif function_name == "search_related_functions":
                    function_response = main_function_library.search_related_functions(function_description=function_arguments.get("function_description"))

                #调用创建任务列表的功能函数
                elif function_name == "create_a_task_list":
                    function_response = main_function_library.create_a_task_list(task_objectives=function_arguments.get("task_objectives"),)
                
                #调用获取日程表的功能类说明
                elif function_name == "query_function_class":
                    function_response = main_function_library.query_function_class(function_class=function_arguments.get("function_class"),)

                #调用日程表的具体的功能函数
                elif "scheduled" in function_name:
                    function_response = my_calendar.call_calendar_function(function_name=function_name,function_arguments=function_arguments)

                #调用功能函数库里的函数
                else:
                    function_response = extended_function_library.call_function(function_name,function_arguments)

                #设置函数调用状态码为3，表示函数调用仍正常运行
                status_code = 3

            except Exception as e:
                if status_code == 0:
                    print("[ERROR] 主AI调用函数时出错，错误代码为：",status_code,"错误信息为：",e,'\n')
                    function_response = "[ERROR] 调用函数时出错,无法成功提取调用函数名字"
                elif status_code == 1:
                    print("[ERROR] 主AI调用函数时出错，错误代码为：",status_code,"错误信息为：",e,'\n')
                    function_response = "[ERROR] 调用函数时出错,无法成功将函数输入参数转换为字典格式"
                elif status_code == 2:
                    print("[ERROR] 主AI调用函数时出错，错误代码为：",status_code,"错误信息为：",e,'\n')
                    function_response = "[ERROR] 调用函数时出错,无法运行该函数"



            #当正常调用函数后
            if status_code == 3:
                print("[DEBUG] 主AI已调用的函数：",function_name,'调用结果为：',function_response,'\n')

            #记录函数调用结果
            ai_memory.log_message("function_return",function_name,None,function_response)

            #再次发送对话请求
            Ai_response = ai_request.make_request(ai_memory)

            #再次提取AI回复内容中message部分
            message = Ai_response["choices"][0]["message"]


        #获取AI回复内容
        content = message['content']
        return content
        


#————————————————————————————————————————主AI对话接口————————————————————————————————————————
class ChatApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.Chat_routes()
        self.voice_to_text()

    #AI对话接口
    def Chat_routes(self):
        @self.app.route('/chat', methods=['POST'])
        def chat():
            #打印原始数据
            print('[DEBUG] 已接收到请求，原始接收数据为：',request.data,'\n')

            # 获取用户输入
            user_input = request.json.get('user_input')

            #输出用户输入
            print("【用户】：",user_input,"\n")

            # 记录用户输入
            ai_memory.log_message("user",None,None,user_input)

            # 发送对话请求
            ai_response = ai_request.make_request(ai_memory)

            # 调用 AI 解析器来解析回复，并自动执行函数调用
            content = ai_parser.parse_response(ai_response)

            # 记录 AI 纯文本回复
            ai_memory.log_message("assistant", None, None, content)

            # 生成 AI 回复的语音
            audio_path = TTS_vits.voice_vits(text=content)

            # 生成语音的口型数据文件
            mouth_data_path = ATM_vits.convertAudioToMouthData(audio_path)

            #输出AI纯文本回复内容
            print("【助手】：",content,"\n")

            # 返回响应
            return jsonify({
                'assistant_response_text': content,
                'assistant_audio_path': audio_path,
                'assistant_mouth_data_path': mouth_data_path
            })
        
    #语音转文本在线接口
    def voice_to_text(self):
        @self.app.route('/whisper', methods=['GET', 'POST'])
        def whisper():
            if request.method == 'POST':
                #获取文件路径
                audio_path = request.json.get('audio_path')

                #打开音频
                audio_file= open(audio_path, "rb")

                #发送请求，返回的是字典格式的数据
                response = openai.Audio.transcribe("whisper-1", audio_file)

                # 提取文本内容
                text = response['text']

                #返回数据
                response = {'user_input': text}
                return jsonify(response)
            else:
                return 'GET请求不支持'
        
    def run(self):
        # 启动服务器，完整地址为 http://localhost:5000/chat'
        self.app.run(host='0.0.0.0', port=5000, debug=True)


#————————————————————————————————————————系统配置接口————————————————————————————————————————     
class ConfigApp:
    def __init__(self):
        pass


#————————————————————————————————————————主程序————————————————————————————————————————
if __name__ == '__main__':
        
    # 读取 YAML 配置文件
    config_path = os.path.join(script_dir, "data", "System_Configuration.yaml")
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
        # 访问具体配置项
        Api_key = config['openai']['api_key']


    #注册api
    openai.api_key = Api_key


    #创建主AI记忆库
    file_path = os.path.join(script_dir, "data")
    ai_memory = Ai_memory(file_path)


    #创建拓展功能函数库
    extended_function_library = function_library.Function_library()

    #创建主AI功能函数库
    main_function_library = Main_AI_function_library()

    #创建AI请求器
    ai_request = Ai_Request()

    #创建AI解析器
    ai_parser = Ai_Parser()

    print("[INFO] AI基础模块启动完成！","\n")


    #创建向量存储库,并使用openai的embedding函数
    chroma_client = chromadb.Client()
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                    api_key=Api_key,
                    model_name="text-embedding-ada-002"
                )
    #创建向量存储库
    collection = chroma_client.create_collection(
                    name="my_collection", 
                    embedding_function=openai_ef
                )

    #根据函数权限，获取拓展功能函数库的函数描述与函数id
    function_id_list,function_description_list = extended_function_library.get_all_function("1")
    #将拓展功能函数库的函数描述向量化并存储
    collection.add(
    documents=function_description_list,
    ids=function_id_list #不支持数字id
    )
    print("[INFO] 功能函数库的函数描述向量化完成！","\n")


    #创建日程表
    my_calendar = calendar_table.Calendar()
 
    #创建日程表执行器
    calendar_executor = Calendar_executor()

    #后台运行日程表执行器
    with open(config_path, 'r', encoding='utf-8') as file:
        # 加载YAML数据
        data = yaml.safe_load(file)
    calendar_switch = data['calendario']['switch']

    if calendar_switch == 'on':
        thread = threading.Thread(target=calendar_executor.run)
        thread.start()
        print("[INFO] 日程表执行器启动完成！","\n")
    elif calendar_switch == 'off':
        print("[INFO] 日程表执行器关闭中！","\n")
    else:
        print("[INFO] 无法正确读取日程表配置信息！","\n")


    #开启后端接口
    chat_app = ChatApp()
    chat_app.run()


    #欢迎用户
    print("【系统】：欢迎使用AI助手！","\n")





