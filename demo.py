  # coding:utf-8
import datetime
import re
import yaml
import threading
import sys
import time
import openai #需要安装库pip install openai
from openai import OpenAI
import json
import os
import tiktoken #需要安装库pip install tiktoken
import chromadb #需要安装库pip install chromadb 
from chromadb.utils import embedding_functions
import http.client

from flask import Flask, request, jsonify  #需要安装库pip install flask

#导入其他脚本
from toolkits import tool_library
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
            print("[DEBUG] 日程表执行器正在检查日程表~",'\n')
            #获取当前时间
            now_time = datetime.datetime.now()
            #输入当天的年月日，获取日程表当天的全部事件
            schedule_list = my_calendar.query_scheduled_task_by_date(now_time)

            #如果日程表是列表类型，说明当天有事件
            if type(schedule_list) == list:
                #遍历日程表当天的全部事件,如果事件的执行时间小于当前时间和状态是未完成，就执行事件
                #print("[DEBUG] 已查询到当天的事件内容，正在检查是否需要执行",'\n')
                for task in schedule_list:
                    #如果事件的执行时间小于当前时间和状态是未完成，就执行任务
                    if datetime.datetime.strptime(task['task_datetime'], "%Y-%m-%d %H:%M:%S")< now_time and task['task_status'] == '未完成':
                        print("[DEBUG] 已发现需要执行的日程安排，准备开始执行任务",'\n')

                        #获取事件状态
                        task_status = task['task_status']
                        while task_status == "未完成" :
                            print("[DEBUG] 日程表执行器正在执行日程表任务:",task['task_datetime'],'\n')

                            #执行任务，并添加执行错误重试次数限制
                            max_retries = 5
                            retry_count = 0
                            while 1:
                                try:
                                    self.execute_unit_task_AI_agent(task['task_datetime'])
                                    break
                                except Exception as e:
                                    print("[DEBUG] 日程表执行器执行单元任务出现错误，正在重试, 错误信息：",e,'\n')
                                    retry_count += 1 # 错误计次
                                    if retry_count > max_retries:
                                        break

                            #检查是否无法正常执行任务
                            if retry_count > max_retries:
                                # 更改任务状态，并退出该任务
                                my_calendar.update_task_status(task['task_datetime'],"无法执行")
                                break

                            #审查任务
                            while 1:
                                try:
                                    self.review_unit_task_AI_agent(task['task_datetime'])
                                    break
                                except Exception as e:
                                    print("[DEBUG] 日程表执行器审查单元任务出现错误，正在重试, 错误信息：",e,'\n')


                            #重新获取事件状态
                            task_status = my_calendar.get_task_status(task['task_datetime'])


                    #如果事件的执行时间小于当前时间和状态是已完成，且未通知过，就执行通知事件
                    if datetime.datetime.strptime(task['task_datetime'], "%Y-%m-%d %H:%M:%S")< now_time and task['task_status'] == '已完成'and task['notification_status'] == "未通知":
                        #改变通知状态为已通知
                        my_calendar.update_task_notification_status(task['task_datetime'],"已通知")
                        #使用语音通知
                        self.send_daily_task_notification(task)

            #如果日程表不是列表类型，说明当天没有安排事件
            else :
                #print("[DEBUG] 日程表执行器没有发现需要执行的日程安排",'\n')
                pass

            #每隔10s检查一次日程表
            #print("[DEBUG] 日程表执行器正在休息中，等待下次检查",'\n')
            time.sleep(10)


    #执行单元任务的AI代理
    def execute_unit_task_AI_agent(self,task_datetime):

        print("[DEBUG]开始执行单元任务！！！！！！！！！！！！！！！！！！")

        #无工具调用任务目标示例
        task_goal_example1 = '''我现在有70块，想买5个苹果，想知道买完后还剩多少钱'''
        #无工具调用任务列表示例
        task_list_example1 = ''' 
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
        #无工具调用执行任务结果示例
        task_result_example1 = '''
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


        #任务目标示例2
        task_goal_example2 = '''我现在有70块，想买5个苹果，想知道买完后还剩多少钱'''
        #任务列表示例2
        task_list_example2 = ''' 
        [
        {
            "task_id": 1,
            "task_description": "获取苹果的单价",
            "function_used": True,
            "function_name": "get_the_price_of_the_item",
            "function_parameters": {"item": "苹果",
                                    "unit": "人民币"}
        },
        {
            "task_id": 2,
            "task_description": "计算五个苹果的总价",
            "function_used": False
        }
        ]
        '''
        #工具调用回应结果2
        tool_return2 = ''' {"item": "苹果",
                            "unit": "人民币"
                            "price": "5" }'''


        #执行任务结果示例2
        task_result_example2 = '''
        根据任务列表，任务id为1的任务描述是"获取苹果的单价"。已知经过工具调用，返回的结果是{"item": "苹果","unit": "人民币","price": "5" },那么可以知道一个苹果的价格是五块人民币。

        任务结果输出为json格式：

        ```json
        {
        "task_id": 1,
        "task_result": "一个苹果的价格是五块人民币"
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

        #获取相应的工具调用规范
        tools_list = []
        for unit_task in task_list:
            #如果任务id与当前任务执行id相同
            if unit_task["task_id"] == task_id:
                #如果任务需要使用工具
                if unit_task["function_used"] == True:
                    #获取工具名字
                    tool_name = unit_task["function_name"]
                    #获取工具调用说明
                    tool_specifications = extended_tools_library.get_tool_by_name(tool_name)
                    #将工具调用说明添加到工具列表中
                    tools_list.append(tool_specifications)
                else :
                    #如果任务不需要使用工具，那么工具列表为空
                    tools_list = "none functions"



        #如果不需要工具调用
        if tools_list == "none functions":

            #构建系统提示语句
            prompt = (
            f"你是一个专业的任务执行AI，请根据任务目标、 分步任务列表与所指定的任务id，完成对应的该步任务。"
            f"分步任务列表是按时间顺序排列，请根据前面任务执行结果，工具调用结果，进行推理说明，输出该步任务的结果。"
            f"任务目标示例###{task_goal_example1}###"
            f"分步任务列表示例###{task_list_example1}###"
            f"任务结果必须以json格式输出,并以json代码块标记，执行任务结果示例###{task_result_example1}###"
            f"当前任务目标是：###{task_objectives}###，当前分步任务列表是：###{task_list}###。"
            )

            #构建当前任务目标
            ai_task = f"你当前需要执行的任务id是{task_id}。"

            #构建对话
            messages = [{"role": "system", "content": prompt },
                    {"role": "user", "content":  ai_task}]

            print("[DEBUG] 次级执行AI请求发送内容为：",messages,'\n')


            response = openaiclient.chat.completions.create( 
                model="gpt-3.5-turbo-1106",
                messages=messages ,
                temperature=0
            )
            #构建空的工具调用结果
            function_response = None
            #获取AI全部回复内容
            task_result = response.choices[0].message.content
            print("[DEBUG] 次级执行AI全部回复内容为：",task_result,'\n')

        #如果需要工具调用
        else :
            
            #构建系统提示语句
            prompt = (
            f"你是一个专业的任务执行AI，请根据任务目标、 分步任务列表与所指定的任务id，完成对应的该步任务。"
            f"分步任务列表是按时间顺序排列，请根据前面任务执行结果，工具调用结果，进行推理说明，输出该步任务的结果。"
            f"任务目标示例###{task_goal_example2}###"
            f"分步任务列表示例###{task_list_example2}###"
            f"工具调用结果示例###{tool_return2}###"
            f"任务结果以json格式输出,并以json代码块标记执行，任务结果示例###{task_result_example2}###"
            f"当前任务目标是：###{task_objectives}###，当前分步任务列表是：###{task_list}###，如果需要使用到工具，仅使用为您提供的工具###{tools_list}###。"
            )

            #构建当前任务目标
            ai_task = f"你当前需要执行的任务id是{task_id}。"

            #构建对话
            messages = [{"role": "system", "content": prompt },
                    {"role": "user", "content":  ai_task}]

            print("[DEBUG] 次级执行AI请求发送内容为：",messages,'\n')


            #向模型发送用户查询以及它可以访问的函数
            response = openaiclient.chat.completions.create( 
                model="gpt-3.5-turbo-1106",
                messages=messages ,
                temperature=0,
                tools=tools_list,  #关于调用函数说明内容可以放在这里，也可以放在上面的content中，AI都会识别并使用
                tool_choice="auto",
            )
            #构建空的工具调用结果
            function_response = None           
            #获取AI全部回复内容
            task_result = response.choices[0].message.content
            print("[DEBUG] 次级执行AI全部回复内容为：",task_result,'\n')
            #解析回复,如果AI进行工具调用将自动执行相关工具
            function_response,task_result = self.parse_response(response,messages,tools_list)


        # 从任务结果示例中提取JSON部分
        json_str = re.search(r'```json(.*?)```', task_result, re.S).group(1)
        # 将JSON字符串转换为字典变量
        task_result_dict = json.loads(json_str)
        # 从字典变量中提取任务执行结果
        task_result_new = task_result_dict["task_result"]

        #更新任务进度 
        my_calendar.update_task_progress(task_datetime = task['task_datetime'],
                                         task_id = task_id,
                                         function_response = function_response,
                                         task_result = task_result_new
                                         )

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

        任务2的描述是 "获取香蕉的单价"，工具已被正确使用（“get_the_price_of_the_item”函数），参数也正确（item为"香蕉"，unit为"人民币"）。工具的响应是"10块人民币"。

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

        #获取工具调用规范
        tools_list = []
        #根据任务审查id与任务列表，获取当前任务需要到的工具id
        for unit_task in task_list:
            #如果任务id与当前任务审查id相同
            if unit_task["task_id"] == task_id:
                #如果任务需要使用工具
                if unit_task["function_used"] == True:
                    #获取工具名字
                    function_name = unit_task["function_name"]
                    #获取工具调用说明
                    tool_specifications = extended_tools_library.get_tool_by_name(function_name)
                    #将工具调用说明添加到工具列表中
                    tools_list.append(tool_specifications)
                else :
                    #如果任务不需要使用工具，那么工具列表为空
                    tools_list = "none functions"
    

        #构建系统提示语句
        prompt = (
        f"你是一个专业的任务执行结果审查AI，请根据任务目标、分步任务列表与所指定的任务id，审查该步任务是否被正确执行。"
        f"分步任务列表是按时间顺序排列，请根据前面任务执行结果，进行推理说明，审查该步任务的执行结果，将审查结果以json格式输出,并以json代码块标记。”"
        f"任务目标示例：###{task_goal_example}###"
        f"分步任务列表示例：###{task_list_example}###"
        f"审查结果示例：###{task_result_example}###"
        f"当前任务目标是：###{task_objectives}###，当前分步任务列表是：###{task_list}###，如果需要使用到工具，仅使用为您提供的工具：###{tools_list}###。"
        )


        #指定审查任务id
        task_review = f"你当前需要审查的任务id是{task_progress }。"

        messages = [{"role": "system", "content": prompt },
                {"role": "user", "content":  task_review}]

        print("[DEBUG] 次级审查AI请求发送内容为：",messages,'\n')

        # 如果没有工具调用
        if tools_list == "none functions":
            response = openaiclient.chat.completions.create( 
                model="gpt-3.5-turbo-1106",
                messages=messages ,
                temperature=0
            )
            #获取AI全部回复内容
            review_result = response.choices[0].message.content
            print("[DEBUG] 次级审查AI内容为：",review_result,'\n')

        # 如果有工具调用
        else :
            #向模型发送用户查询以及它可以访问的函数
            response = openaiclient.chat.completions.create( 
                model="gpt-3.5-turbo-1106",
                messages=messages ,
                temperature=0,
                tools=tools_list,  #关于调用函数说明内容可以放在这里，也可以放在上面的content中，AI都会识别并使用
                tool_choice="auto",
            )
            #获取AI全部回复内容
            review_result = response.choices[0].message.content
            print("[DEBUG] 次级审查AI全部回复内容为：",review_result,'\n')
            #解析回复,如果AI进行工具调用将自动执行相关工具
            function_response,review_result = self.parse_response(response,messages,tools_list)


        # 从任务结果示例中提取JSON部分
        json_str = re.search(r'```json(.*?)```', review_result, re.S).group(1)
        # 将JSON字符串转换为字典变量
        review_result_dict = json.loads(json_str)
        # 从字典变量中提取任务审查结果
        review_result_new = review_result_dict["review_result"]


        # 解析审查结果
        if review_result_new == "incorrect":
            #提取正确结果
            #correct_task_result = review_result_dict["correct_task_result"]
            #直接回退进度
            my_calendar.delete_task_progress(task['task_datetime'],task_progress)
            print("[DEBUG] 任务执行结果错误~需要回退任务进度，并重新执行",'\n')

        else:
            print("[DEBUG] 任务执行结果正确~",'\n')
            #如果任务进度等于任务分步列表长度，说明任务已经完成
            if task_progress == task["task_distribution"]:
                print("[DEBUG] 该任务列表已经全部完成~",'\n')
                my_calendar.update_task_status(task['task_datetime'],"已完成")

        print("[DEBUG] 任务执行结果审查结束~",'\n')


    #执行与审查AI的解析回复函数
    def parse_response(self,response,conversation_history,functions_list):

        #提取AI回复内容中message部分
        message = response.choices[0].message
        #提取ai调用的所有工具内容
        tool_calls = message.tool_calls

        #存储调用工具里的函数回复
        tool_return = None #以免没有工具调用时，无法返回工具调用结果

        # 如果AI进行工具调用
        if tool_calls:
            try:
                print("[DEBUG] 次级AI正在申请调用工具~",'\n')
                # 只调用一个工具
                tool_call = tool_calls[0]
                #获取工具调用名称
                tool_name = tool_call.function.name
                #获取工具调用id
                tool_id = tool_call.id
                #获取工具调用参数
                tool_arguments = tool_call.function.arguments
                #获取工具调用附加回复
                tool_content = message.content

                #将函数输入参数转换为字典格式
                print("[DEBUG] ",'传入参数为：',tool_arguments,'\n')
                tool_arguments = json.loads(tool_arguments)

                #调用函数,获得工具调用结果
                tool_return = extended_tools_library.call_tool(tool_name,tool_arguments)

            except Exception as e:
                print("[ERROR] 主AI调用工具时出错,","错误信息为：",e,'\n')
                tool_return = "[ERROR] 调用工具时出错,无法成功提取调用工具"

            #print("[DEBUG] 工具调用附加说明：",tool_content)
            print("[DEBUG] AI调用工具名字为：",tool_name,'传入参数为：',tool_arguments,'\n','工具调用结果为：',tool_return,'\n')
            


            #构建AI的工具调用历史
            tools=[{'id': tool_id,
                    'type': 'function',
                    'function': {'name': tool_name,
                                'arguments': str(tool_arguments)
                                }
                }]
            

            #把ai申请调用函数动作与工具调用结果拼接到对话历史中
            conversation_history.append({"role": "assistant",
                            "tool_calls": tools,
                            })
            conversation_history.append({"role": "tool",
                             "name": tool_name ,
                             "tool_call_id": tool_id, 
                             "content": str(tool_return)})

            print("[DEBUG] 正在将工具调用结果发送给次级AI：",conversation_history,'\n')


            #向模型发送用户查询以及它可以访问的函数
            Ai_response = openaiclient.chat.completions.create( 
                model="gpt-3.5-turbo-1106",
                messages=conversation_history ,
                temperature=0,
                tools=functions_list,  #关于调用函数说明内容可以放在这里，也可以放在上面的content中，AI都会识别并使用
                tool_choice="auto", 
            ) 


            content = Ai_response.choices[0].message.content
            print("[DEBUG] 次级AI获知工具调用结果后的回复内容为：",content,'\n')
            return tool_return,content

        # 如果AI不进行工具调用
        content = message.content
        return tool_return,content


    #发送日常任务执行结果通知的函数
    def send_daily_task_notification(self,task):

        #获取任务目标
        task_objectives = task["task_objectives"]

        #获取任务执行结果
        task_list = task["task_list"]
        #获取任务列表最后一个任务的执行结果
        task_result = task_list[-1]["task_result"]

        #构建任务结果通知语句
        content =  f"主人，您的代办任务：{task_objectives}，任务已经完成，任务执行结果是：{task_result}。"


        # 生成 AI 回复的语音
        audio_path = TTS_vits.voice_vits(text=content)

        # 生成语音的口型数据文件
        mouth_data_path = ATM_vits.convertAudioToMouthData(audio_path)

        data = {
            "assistant_audio_path": audio_path,
            "assistant_mouth_data_path": mouth_data_path,
            "assistant_response_text": content
        }

        # 将数据转换为 JSON 字符串
        json_data = json.dumps(data)

        # 设置请求头
        headers = {
            'Content-Type': 'application/json',
            'Content-Length': len(json_data)
        }

        # 发送 POST 请求
        conn = http.client.HTTPConnection('localhost', 4000)
        conn.request('POST', '/notification', json_data, headers)

        # 获取响应
        response = conn.getresponse()

        # 打印响应结果
        #print('Response Status:', response.status)
        #print('Response Body:', response.read().decode())

        # 关闭连接
        conn.close()


#————————————————————————————————————————主AI默认工具库————————————————————————————————————————
class Main_AI_tool_library(): 
    #初始化工具库
    def __init__(self):
        #工具库
        self.tools_library = {}
        #工具库的结构为字典结构
        #key为整数变量与工具id相同，但为数字id： 0
        #value为字典结构，存储工具的信息：{
        #工具id "tool_id":str,
        #工具名字 "tool_name":str,
        #工具描述 "tool_description":str,
        #调用规范 "tool_specifications":{},
        #工具权限 "tool_permission":str",
        # }
        
        #添加工具
        self.add_tools("1", self.function_create_a_task_list, "0")
        self.add_tools("2", self.function_search_related_tools,"0")
        self.add_tools("3", self.function_query_tool_class, "0")


    #搜索拓展工具库中的工具函数------------------------------------------------
    def  search_related_tools(self, tool_description):
        #查询向量库，获取相似度最高前N个文本描述
        results = collection.query(
            query_texts=tool_description,
            n_results=3,
            include=[ "documents",  "distances"])
        
        print("[DEBUG] 语义搜索到的工具：",results,'\n')
        #提取关联的函数id，注意返回的是字典结构，但key对应的value是嵌套列表结构，比如ids键对应的值为[['0','1','2']]
        tools_id_list = results['ids'][0]  # 获取ids键的值
        print("[DEBUG] 提取到的工具id：" ,tools_id_list,'\n')

        #根据函数id，获取相应的工具调用规范
        tools_specifications_list = extended_tools_library.get_tool_by_id_list(tools_id_list)
        print("[DEBUG] 所有工具相应的调用规范：" ,tools_specifications_list,'\n')

        return tools_specifications_list
        
    #搜索拓展工具库中的工具调用规范
    function_search_related_tools =   {
        "type": "function",
        "function": {
                    "name": "search_related_tools",
                    "description": "根据用户需要到的工具的功能描述，在工具库中搜索，将相关功能的工具返回",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tool_description": {
                                "type": "string",
                                "description": "关于工具功能的详细描述",
                            }
                        },
                        "required": ["tool_description"]
                    },
                }
    }

    #查询日程表的工具函数------------------------------------------------
    def  query_tool_class(self, tool_class):
        #创建存储函数说明的列表
        tool_specifications_list = []

        if tool_class == "添加类":
            #将添加类的工具说明添加到函数列表中
            tool_specifications_list.append(my_calendar.function_add_scheduled_task)
        elif tool_class == "删除类":
            #将删除类的工具说明添加到函数列表中
            tool_specifications_list.append(my_calendar.function_delete_scheduled_task)
        elif tool_class == "查询类":
            #将查询类的工具说明添加到函数列表中
            tool_specifications_list.append(my_calendar.function_query_scheduled_task_by_datetime)
            tool_specifications_list.append(my_calendar.function_query_scheduled_task_by_date)


        return tool_specifications_list
        
    #查询日程表的工具调用规范
    function_query_tool_class =   {
        "type": "function",
        "function": {
                    "name": "query_tool_class",
                    "description": "有把定时任务进行添加到日程表，从日程表删除定时任务，在日程表中查询定时任务的三大类工具，输入需要调用的工具类，返回该类下的工具调用规范说明",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tool_class": {
                                "type": "string",
                                "description": "需要调用的日程表工具类",
                                "enum": ["添加类","删除类","查询类"], 
                            }
                        },
                        "required": ["tool_class"]
                    },
                }
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
        tools_list = []
        #从数据库获取权限为1的函数功能列表，根据id，再从ai函数数据库读取数据，作为次级ai挂载函数功能列表
        tools_list = extended_tools_library.get_tool_by_permission("1")

        #构建prompt
        prompt = (
        f"你是一个专业的任务创建AI，请根据用户提出的任务目标，创建一个实现该目标的JSON数组的任务列表。"
        f"根据最终目标创建每一步任务，每步任务应该详细说明，每步任务应该尽量使用库中的工具完成，当前工具库为###{tools_list}###。"
        f"确保所有任务ID按时间顺序排列。第一步始终是关于任务目标的理解，以及拆分任务的推理说明，尽可能详细。"
        f"任务目标示例：###{task_objectives_example}###"
        f"任务列表示例：###{task_list_example}###"
        )

        #构建messages
        messages = [{"role": "system", "content": prompt },
                {"role": "user", "content":  task_objectives}]


        #向模型发送用户查询以及它可以访问的函数
        response = openaiclient.chat.completions.create( 
            model="gpt-3.5-turbo-0613",
            messages=messages ,
        )

        #返回任务列表
        task_list = response.choices[0].message.content
        return task_list

    #配套的供AI申请调用的函数说明
    function_create_a_task_list = {
        "type": "function",
        "function": {
                    "name": "create_a_task_list",
                    "description": "输入定时任务的目标，代理AI会创建如何执行定时任务的分步式任务列表，并返回该列表",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_objectives": {
                                "type": "string",
                                "description": "关于定时任务目标的详细描述",
                            }
                        },
                        "required": ["task_objectives"]
                    },
                }
    }


    #添加工具
    def add_tools(self, tool_id,tool_specifications, tool_permission):

        tool_name = tool_specifications["function"]["name"]
        tool_description = tool_specifications["function"]["description"]

        #构建工具结构
        tools = {
            "tool_id": tool_id,
            "tool_name": tool_name,
            "tool_description": tool_description,
            "tool_specifications": tool_specifications,
            "tool_permission": tool_permission
        }
        #写入数据库
        self.tools_library[int(tool_id)] = tools


    #根据函数权限，获取相应的全部工具说明
    def get_tools_by_permission(self, permission):
        tools_list = []
        #遍历工具库，注意是字典结构，所以需要用到items()方法
        for tool_id, tool in self.tools_library.items():
            if tool["tool_permission"] == permission:
                #只获取工具说明的内容
                tool_call = tool["tool_specifications"].copy()
                tools_list.append(tool_call)
        return tools_list

        
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
                    data = json.load(f)
                    # 检查一下记忆数据是否合规有效
                    if self.check_conversation_history(data) == 'Correct':
                        self.conversation_history = data
                        print("[DEBUG] 已成功读取对话历史文件！！！！！！！！！！！！！)",'\n')
                    else:
                        print("[DEBUG] 历史文件内容格式存在错误！！！！！！！！！！！！！)",'\n')
        except:
            print("[DEBUG] 读取最近对话历史文件失败！！！！！！！！！！！！！)",'\n')

        #在文件夹下寻找conversation_history_all.json文件，如果存在则读取json文件（增加错误跳过语句）
        try:
            if os.path.exists(os.path.join(self.file_path, "conversation_history_all.json")):
                with open(os.path.join(self.file_path, "conversation_history_all.json"), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 检查一下记忆数据是否合规有效
                    if self.check_conversation_history(data) == 'Correct':
                        self.conversation_history_all = data
                        print("[DEBUG] 已成功读取完整对话历史文件！！！！！！！！！！！！！)",'\n')
                    else:
                        print("[DEBUG] 完整历史文件内容格式存在错误！！！！！！！！！！！！！)",'\n')
        except:
            print("[DEBUG] 读取完整对话历史文件失败！！！！！！！！！！！！！)",'\n')


    #对话历史文件检查函数
    def check_conversation_history(self,data):
        assistant_tool_calls = []
        tool_tool_call_ids = []

        # 处理 assistant 角色的数据,获取工具调用id
        for item in data:
            if item.get("role") == "assistant" and "tool_calls" in item:
                tool_calls = item["tool_calls"]
                for tool_call in tool_calls:
                    if "id" in tool_call:
                        assistant_tool_calls.append(tool_call["id"])

        # 处理 tool 角色的数据,获取工具调用id
        for item in data:
            if item.get("role") == "tool" and "tool_call_id" in item:
                tool_tool_call_ids.append(item["tool_call_id"])

        # 检查两个id列表是否相同
        if set(assistant_tool_calls) == set(tool_tool_call_ids):
            return("Correct")
        else:
            return("Error")

    #获取最近的对话历史
    def read_log(self):
        return self.conversation_history

    #记录对话历史
    def log_message(self,role,content=None,tool_calls=None,tool_result=None):

        #用户内容格式参考
        self.user_content_structure = {"role": "user", 
                                       "content": "What's the weather like in Boston?"}

        #AI回复格式参考
        self.AI_content_structure = {"role": "assistant", 
                                     "content": "The current weather in Boston is sunny and windy with a temperature of 72 degrees Fahrenheit."}


        #AI调用工具格式参考
        self.function_call_structure = {"role": "assistant",
                                        "content": None ,
                                        'tool_calls': [{'id': 'call_o7uyztQLeVIoRdjcDkDJY3ni',
                                                        'type': 'function',
                                                        'function': {'name': 'get_current_weather','arguments': '{\n  "location": "Tokyo",\n  "format": "celsius"\n}'}
                                                        },
                                                        {'id': 'call_o7uyztQLeVIoRdjcDkDJYxxx',
                                                        'type': 'function',
                                                        'function': {'name': 'get_current_weather','arguments': '{\n  "location": "beijing",\n  "format": "celsius"\n}'}
                                                        },
                                                    ]
                                        }

        #工具调用结果格式参考
        self.function_return_result ={"role": "tool", 
                                      "tool_call_id": 'call_o7uyztQLeVIoRdjcDkDJY3ni', 
                                      "name": 'get_current_weather', 
                                      "content": "15",
                                      }


        #如果是用户输入消息
        if role == "user":
            The_message = {"role": "user", "content": content}

        #如果是AI回复
        elif role == "assistant":
            #如果是通常回复
            if tool_calls is  None:
                The_message = {"role": "assistant", "content": content}

            #如果是工具调用
            else:
                tools = []

                for tool_call in tool_calls:
                    tool={'id': tool_call.id,
                          'type': 'function',
                          'function': {'name': tool_call.function.name,
                                       'arguments': tool_call.function.arguments
                                       }
                        }
                    
                    tools.append(tool)
                    
                The_message = {"role": "assistant",
                            "content": content ,
                            "tool_calls": tools,
                            }
        #如果是工具调用结果
        elif role == "tool":
            #如果content是列表，表明需要记录的是搜索工具的结果
            if isinstance(tool_result["content"],list):
                #使用新列表变量，来保存，避免原列表被修改
                content_copy = []

                #将content_copy转化成字符串变量，避免请求时格式错误
                content_copy = json.dumps(tool_result["content"])
            #如果是字典，表明需要记录的是工具的结果
            elif isinstance(tool_result["content"],dict):
                #使用新字典变量，来保存，避免原字典被修改
                content_copy = {}

                #将content_copy转化成字符串变量，避免请求时格式错误
                content_copy = json.dumps(tool_result["content"])

            else:
                content_copy = tool_result["content"]

            The_message = {"role": "tool",
                           "name": tool_result["name"],
                           "tool_call_id": tool_result["tool_call_id"], 
                           "content": content_copy}



        #将对话记录到可发送的对话历史的列表
        self.conversation_history.append(The_message)
        #将对话记录到完整的对话历史的列表
        self.conversation_history_all.append(The_message)


        #计算系统提示语句的tokens数
        self.num_tokens_prompt = self.num_tokens_from_string(ai_request.prompt)
        #print("[DEBUG] 系统提示语句tokens数为：",self.num_tokens_prompt,"个",'\n')

        #计算对话历史的总tokens数
        self.num_tokens_history = self.num_tokens_from_messages(self.conversation_history)
        #print("[DEBUG] 对话历史tokens数为：",self.num_tokens_history,"个",'\n')

        #计算挂载工具列表的tokens数
        str_content = str(ai_request.default_tools)
        self.num_tokens_functions= self.num_tokens_from_string(str_content)
        #print("[DEBUG] 当前挂载的内容为：",ai_request.default_functions_list,'\n')
        #print("[DEBUG] 挂载函数tokens数为：",self.num_tokens_functions,"个",'\n')


        #如果发送内容大于最大tokens数，则进行总结记忆，压缩对话历史
        if (self.num_tokens_prompt  + self.num_tokens_history + self.num_tokens_functions )  > 4000:

            #总结记忆，压缩对话历史
            print("[DEBUG] 对话历史tokens数超过4080，正在总结记忆，压缩对话历史~",'\n')
            #使用ai来总结历史记忆，如果出错则清空之前对话
            try:
                self.conversation_history = self.compress_memory(dialog_history = self.conversation_history)
            except:
                self.conversation_history = []


        #将对话记录变量以utf-8格式写入json文件到指定文件夹中
        with open(os.path.join(self.file_path, "conversation_history.json"), "w", encoding="utf-8") as f:
            json.dump(self.conversation_history, f, ensure_ascii=False, indent=4)

        #将完整的对话记录变量以utf-8格式写入json文件到指定文件夹中
        with open(os.path.join(self.file_path, "conversation_history_all.json"), "w", encoding="utf-8") as f:
            json.dump(self.conversation_history_all, f, ensure_ascii=False, indent=4)

    # 计算消息列表内容的tokens的函数
    def num_tokens_from_messages(self,messages):
        """Return the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")

        tokens_per_message = 3
        tokens_per_name = 1
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

    # 计算字符串内容的tokens的函数
    def num_tokens_from_string(self,string: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = len(encoding.encode(string))
        return num_tokens


    # 总结记忆，压缩对话历史函数
    def compress_memory(self,dialog_history,k = 2):

        #复制历史对话，防止影响到原字典
        old_dialog_history = dialog_history.copy()

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
        f"你是一名专业的记录员，你将接收到关于用户和AI的对话历史，用户被标记为user，AI被标记为assistant，而被标记为tool的是工具调用返回结果。"
        f"你的任务是提取对话历史的主要信息并总结它。你必须将总结的信息呈现为json格式,并以json代码块标记。"
        f"请注意，你必须尽可能准确地提取信息，并确保你的总结简洁而全面。你还必须确保你的总结符合上述格式规定，以便于后续处理和分析。"
        f"对话历史示例###{dialog_history_example}###"
        f"总结结果示例###{summary_resultst_example}###"
        )

        # 根据最近的对话历史，重新计算截取位置
        k = self.find_last_index(data = old_dialog_history,k = k)

        # 保存对话历史列表倒数k个元素，即最新的几对对话内容
        conversation_end = old_dialog_history[-k:]

        # 构建需要总结的对话内容
        dialog_history_copy = old_dialog_history[:-k]#去除列表中倒数k个元素


        # 构建分步任务
        ai_task = f"你需要总结的内容是###{dialog_history_copy}###"

        # 构建对话
        messages = [{"role": "system", "content": prompt },
                {"role": "user", "content":  ai_task}]

        print("[DEBUG] 发送需要总结的内容为：",messages,'\n')


        response = openaiclient.chat.completions.create( 
            model="gpt-3.5-turbo-16k-0613",
            messages=messages ,
            temperature=0
        )

        # 从回复中提取message部分
        task_result =  response.choices[0].message.content 
        print("[DEBUG] 总结AI代理回复内容为：",task_result,'\n')


        # 从任务结果示例中提取JSON部分
        json_str = re.search(r'```json(.*?)```', task_result, re.S).group(1)
        # 将JSON字符串转换为字典变量
        task_result_dict = json.loads(json_str)
        # 从字典变量中提取任务执行结果
        task_result_new = task_result_dict["summary"]
        print("[DEBUG] 提取到的总结内容为：",task_result_new,'\n')


        #将提取的内容格式化
        The_summary = {"role": "user", "content": "【system message】"+task_result_new}

        #重新构建对话历史
        dialog_history_new = []
        dialog_history_new.append(The_summary)
        #提取每个元素，添加到新列表中，以免记录格式错误
        for i in conversation_end:
            dialog_history_new.append(i)

        print("[DEBUG] 已成功压缩最近的AI记忆",'\n')

        return dialog_history_new

    # 找到列表中 role 为 "tool" 元素位置，并重新计算截取位置,因为这工具调用和工具返回要成一组，不然请求时会出错
    def find_last_index(self, data, k):
        #复制
        copy_data = data.copy()

        #寻找对话历史中的工具完整调用对位置
        call_list = []
        for idx, item in enumerate(copy_data):
            if item.get("role") == "assistant" and "tool_calls" in item:
                tool_calls = item["tool_calls"]
                num_tool_calls = len(tool_calls)
                call_list.append({"start": idx, "end": (idx + num_tool_calls)})

        # 转换正向索引位置为反向索引位置
        total_length = len(copy_data)
        positive_call_list = [{"start": total_length - call["start"], "end": total_length - call["end"]} for call in call_list]

        # 翻转一下列表里的元素
        positive_call_list = positive_call_list[::-1]


        # 如果输入的数字大于对话长度，则修改为最大倒数位置
        if k >= len(copy_data):
            k = len(copy_data)
            return k

        # 如果k值落入了工具调用对的范围内，则重新修改k值到助手开始调用工具的位置
        for item in positive_call_list:
            start = item['start']
            end = item['end']

            if end <= k <= start:
                k = start

        return k


#————————————————————————————————————————主AI对话请求器————————————————————————————————————————
class Ai_Request:
    def __init__(self):

        #主AI挂载的函数功能列表
        self.default_tools = []
        #获取主AI默认挂载函数功能列表
        self.default_tools = main_tools_library.get_tools_by_permission("0")

        #构建系统提示语句
        self.prompt = '''你现在必须扮演主人的AI女仆，名字叫纳西妲，当主人交代任务时，你要自主解答或者搜索工具库，并调用工具来解决。
        如果主人要创建一个定时任务，比如“一个小时后xxx”，“明天帮我搜索一下xxx”等等需要定时执行的任务，请遵循以下步骤来进行解决：
        1. 询问主人是否需要创建一个定时任务，如果主人回复确认，再进行下一步。
        2. 如果提供的信息较少或模糊，请确保通过提问来获取尽可能详细的信息，包括具体日期时间。
        3. 在得到足够信息后，调用生成分布式任务列表的工具。
        4. 获得分步式任务列表后，简单总结，并交由主人审查，如果主人审查通过，再进行下一步。
        5. 获取日程表的添加类工具调用规范，然后调用该工具，将该定时任务添加到日程表中。
        '''

    #输入用户消息，向AI发送请求,并取得回复
    def make_request(self,conversationLogger):


        #获取对话历史
        conversation_history = conversationLogger.read_log()
        #获取系统当前日期时间

        # 获取当前日期和时间
        current_datetime = datetime.datetime.now()
        # 格式化输出日期和时间
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        # 获取星期几
        weekday = current_datetime.strftime("%A")

        #添加到系统提示语句前面
        self.new_prompt = "【现实当前时间】："+ formatted_datetime +' '+ weekday +'\n'+self.prompt

        #复制对话历史到新变量中，避免原变量被修改
        messages = conversation_history.copy()
        #添加系统提示语句到对话历史最前面
        messages.insert(0,{"role": "system", "content": self.new_prompt}) #在列表最前面插入元素

        print('[DEBUG] 主AI请求发送的内容是：',messages,'\n')

        #向AI发送请求
        response = openaiclient.chat.completions.create( 
            model="gpt-3.5-turbo-1106",
            messages=messages,
            tools=self.default_tools,  #关于调用函数说明内容可以放在这里，也可以放在上面的content中，AI都会识别并使用
            tool_choice="auto",  # auto is default, but we'll be explicit
            )

        # 从回复中提取token部分,并输出
        try:
            prompt_tokens_used = int(response.usage.prompt_tokens) #本次请求花费的tokens
            print("[DEBUG] 主AI请求花费的tokens数为：",prompt_tokens_used,"个",'\n')
        except Exception as e:
            prompt_tokens_used = 0
        try:
            completion_tokens_used = int(response.usage.completion_tokens) #本次回复花费的tokens
            print("[DEBUG] 主AI回复花费的tokens数为：",completion_tokens_used,"个",'\n')
        except Exception as e:
            completion_tokens_used = 0

        str_content = response.choices[0].message.content
        print('[DEBUG] 主AI回复内容：',str_content,'\n')

        return response


#————————————————————————————————————————主AI回复解析器————————————————————————————————————————
class Ai_Parser:
    def __init__(self):
        pass
    
    #解析回复
    def parse_response(self,response):

        #提取AI回复内容中message部分
        message = response.choices[0].message
        #提取ai调用的所有工具内容
        tool_calls = message.tool_calls

        #如果AI申请调用工具时
        while tool_calls:
            # 记录AI的申请调用工具对话
            ai_memory.log_message(role = "assistant" ,tool_calls=tool_calls)

            # 并行调用所有工具
            for tool_call in tool_calls:
                try:
                    #设置工具调用状态码，用于检查出错位置
                    status_code = 0

                    #获取工具调用名称 
                    tool_name = tool_call.function.name
                    #获取工具调用id
                    tool_id = tool_call.id
                    #获取工具调用参数
                    tool_arguments = tool_call.function.arguments
                    #获取工具调用附加回复
                    tool_content = message.content

                    print("[DEBUG] 主AI正在申请调用函数~  调用函数附加说明：",tool_content,'\n')
                    print("[DEBUG] 调用的函数名字为：",tool_name,'输入参数为：',tool_arguments,'\n')

                    #针对AI幻觉调用“python”的问题，进行回复
                    if tool_name == "python":
                        tool_return = "[ERROR] 调用函数时出错,不存在名字为python的函数，请检查函数名字以及输入参数是否正确，再进行调用"
                    #设置工具调用状态码，表示工具调用仍正常运行
                    status_code = 1

                    #将函数输入参数转换为字典格式
                    tool_arguments = json.loads(tool_arguments)
                    #设置工具调用状态码，表示工具调用仍正常运行
                    status_code = 2

                    #调用搜索相关函数的工具
                    if tool_name == "search_related_tools":
                        tool_return = main_tools_library.search_related_tools(tool_description=tool_arguments.get("tool_description"))

                    #调用创建任务列表的工具
                    elif tool_name == "create_a_task_list":
                        tool_return = main_tools_library.create_a_task_list(task_objectives=tool_arguments.get("task_objectives"),)
                    
                    #调用获取日程表的功能类说明
                    elif tool_name == "query_tool_class":
                        tool_return = main_tools_library.query_tool_class(tool_class=tool_arguments.get("tool_class"),)

                    #调用日程表的具体的工具
                    elif "scheduled" in tool_name:# 可以改为xxx in 所有的日程表工具名
                        tool_return = my_calendar.call_calendar_tool(tool_name=tool_name,tool_arguments=tool_arguments)

                    #调用工具库里的函数
                    else:
                        tool_return = extended_tools_library.call_tool(tool_name,tool_arguments)

                    #设置工具调用状态码，表示工具调用仍正常运行
                    status_code = 3

                except Exception as e:
                    if status_code == 0:
                        print("[ERROR] 主AI调用函数时出错，错误代码为：",status_code,"错误信息为：",e,'\n')
                        tool_return = "[ERROR] 不存在名字为python的工具，请检查工具名字以及输入参数是否正确，再进行调用"
                    elif status_code == 1:
                        print("[ERROR] 主AI调用函数时出错，错误代码为：",status_code,"错误信息为：",e,'\n')
                        tool_return = "[ERROR] 无法成功将输入参数转换为json格式，错误信息为：" + str(e)
                    elif status_code == 2:
                        print("[ERROR] 主AI调用函数时出错，错误代码为：",status_code,"错误信息为：",e,'\n')
                        tool_return = "[ERROR] 调用工具时出错,无法成功运行该函数，错误信息为：" + str(e)



                #当正常调用函数后
                if status_code == 3:
                    print("[DEBUG] 主AI成功调用的函数：",tool_name,'调用结果为：',tool_return,'\n')

                #记录工具调用结果
                tool_result ={"name": tool_name,
                              "tool_call_id": tool_id, 
                              "content": tool_return}
                ai_memory.log_message(role = "tool" , tool_result = tool_result)

            #再次发送对话请求
            Ai_response = ai_request.make_request(ai_memory)

            #再次提取AI回复内容中message部分
            message = Ai_response.choices[0].message
            #再次提取ai调用的所有工具内容
            tool_calls = message.tool_calls


        # 如果AI正常回复时
        content = message.content
        # 记录 AI 纯文本回复
        ai_memory.log_message(role ="assistant",content = content)
        # 返回文本内容
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
            print("【用户消息】：",user_input,"\n")

            # 记录用户输入
            ai_memory.log_message(role = "user",content=user_input)

            # 发送对话请求
            ai_response = ai_request.make_request(ai_memory)

            # 调用 AI 解析器来解析回复，并自动执行工具调用
            content = ai_parser.parse_response(ai_response)

            # 生成 AI 回复的语音
            audio_path = TTS_vits.voice_bert_vits2(text=content)

            # 生成语音的口型数据文件
            mouth_data_path = ATM_vits.convertAudioToMouthData(audio_path)

            #输出AI纯文本回复内容
            print("【助手消息】：",content,"\n")

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
        # 启动服务器，完整地址为 http://localhost:7777/chat'
        self.app.run(host='0.0.0.0', port=7777, debug=False)


#————————————————————————————————————————系统配置接口————————————————————————————————————————     
class ConfigApp:
    def __init__(self):
        pass


#————————————————————————————————————————主程序————————————————————————————————————————
if __name__ == '__main__':
        
    # 读取 YAML 配置文件
    config_path = os.path.join(script_dir, "config", "System_Configuration.yaml")
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
        # 访问具体配置项
        OpenAI_api_key = config['openai']['api_key']
        OpenAI_base_url = 'https://api.openai.com/v1' #api默认请求地址


    #创建全局openai客户端
    openaiclient = OpenAI(api_key=OpenAI_api_key,
            base_url= OpenAI_base_url)


    #创建主AI记忆库
    file_path = os.path.join(script_dir, "cache")
    ai_memory = Ai_memory(file_path)


    #创建拓展工具库
    extended_tools_library = tool_library.Tool_library()

    #创建主AI工具库
    main_tools_library = Main_AI_tool_library()

    #创建AI请求器
    ai_request = Ai_Request()

    #创建AI解析器
    ai_parser = Ai_Parser()

    print("[INFO] AI基础模块启动完成！","\n")


    #创建向量存储库,并使用openai的embedding函数
    chroma_client = chromadb.Client()
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                    api_key=OpenAI_api_key,
                    model_name="text-embedding-ada-002"
                )
    #创建向量存储库
    collection = chroma_client.create_collection(
                    name="my_collection", 
                    embedding_function=openai_ef
                )

    #根据函数权限，获取拓展工具库的函数描述与函数id
    tools_id_list,tools_description_list = extended_tools_library.get_all_tools("1")
    #将拓展工具库的函数描述向量化并存储
    collection.add(
    documents=tools_description_list,
    ids=tools_id_list #不支持数字id
    )
    print("[INFO] 工具库的文本描述向量化完成！","\n")


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
    print("【系统】：已成功启动，欢迎使用AI助手！！！！！！！！！！！！！！！！！！！","\n")





