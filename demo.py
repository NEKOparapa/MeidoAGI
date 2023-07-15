# coding:utf-8
import re
import threading
import sys
import openai #需要安装库pip install openai
import json
import os
import tiktoken #需要安装库pip install tiktoken
import chromadb #需要安装库pip install chromadb 
from chromadb.utils import embedding_functions

#导入格式：from 文件夹.文件名 import 类名
from toolkits.function_library import Function_library
from calendar.task_library import Task_library
#from agents.cot_agent import  cot_mode


#————————————————————————————————————————次级AI代理————————————————————————————————————————
#思维链模式（根据任务目标，思考一步做一步看一步，再根据这步和目标，再进行下一步。直到结果）
class cot_mode:
    def __init__(self):
        pass



    #根据任务目标创建分步式任务的AI代理（使用大容量模型，把所有的工具描述带上，以思维链方式来创建,交给用户判断，是否合适，不合适则重新生成）
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
        functions_list = function_library.get_function_by_permission("1")

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

    #配套的供AI申请调用的函数说明
    function_create_a_task_list = {
            "name": "create_a_task_list",
            "description": "输入任务目标，次级AI会创建分步式任务列表，并返回",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_objectives": {
                        "type": "string",
                        "description": "关于任务目标的详细描述",
                    }
                },
                "required": ["task_objectives"]
            },
        }


    #开始循环执行分步式任务的AI代理
    def start_distributed_task_AI_agent(self,task_cache_id):
        # try:
        #     #获取任务状态
        #     task_status = task_library.get_task_status(task_cache_id)

        #     while task_status == "进行中" :
        #         self.execute_unit_task_AI_agent(task_cache_id)

        #         self.review_unit_task_AI_agent(task_cache_id)

        #         #重新获取任务状态
        #         task_status = task_library.get_task_status(task_cache_id)
        # #抛出异常
        # except Exception as e:
        #     print("线程执行出错，错误信息如下：")
        #     print(e)
        #     return "执行失败"

        #获取任务状态
        task_status = task_library.get_task_status(task_cache_id)

        while task_status == "进行中" :
            self.execute_unit_task_AI_agent(task_cache_id)

            self.review_unit_task_AI_agent(task_cache_id)

            #重新获取任务状态
            task_status = task_library.get_task_status(task_cache_id)

    #配套的供AI申请调用的函数说明
    function_start_distributed_task_AI_agent = {
            "name": "start_distributed_task_AI_agent",
            "description": "传入任务目标，JSON数组格式的任务列表，次级AI代理会开始自动执行任务",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_objectives": {
                        "type": "string",
                        "description": "关于任务目标的详细描述",
                    },
                    "task_list": {
                        "type": "string",
                        "description": "json数组格式的任务列表",
                    }
                },
                "required": ["task_objectives","task_list"]
            },
        }



    #读取任务库中全部任务执行情况的函数
    def read_tasks_running_status(self):
        return task_library.read_all_task_list()

    #配套的供AI申请调用的函数说明
    function_read_tasks_running_status = {
            "name": "read_tasks_running_status",
            "description": "读取任务库中全部任务执行情况",
            "parameters": {
                "type": "object",
                "properties": {
                    "read_request": {
                        "type": "string",
                        "description": "是否读取全部任务执行情况？如果是，传入yes，如果否，传入no",
                    }
                },
                "required": ["read_request"]
            },
        }




    #执行单元任务的AI代理
    def execute_unit_task_AI_agent(self,task_cache_id):

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


        #获取任务
        task = task_library.read_task_list(task_cache_id)
        #获取任务目标
        task_objectives = task["task_objectives"]
        #获取任务列表
        task_list = task["task_list"]
        #获取任务进度
        task_progress = task["task_progress"]
        #获取任务执行id
        task_id = task_progress + 1


        #执行AI挂载的函数功能列表
        functions_list = []
        #根据任务执行id与任务列表，获取当前任务需要到的函数id
        for unit_task in task_list:
            #如果任务id与当前任务执行id相同
            if unit_task["task_id"] == task_id:
                #如果任务需要使用函数
                if unit_task["function_used"] == True:
                    #获取函数名字
                    function_name = unit_task["function_name"]
                    #获取函数调用说明
                    function_ai_call = function_library.get_function_by_name(function_name)
                    #将函数调用说明添加到函数列表中
                    functions_list.append(function_ai_call)
                else :
                    #如果任务不需要使用函数，那么函数列表为空
                    functions_list = "none functions"


        #构建系统提示语句
        prompt = (
        f"你是一个专业的任务执行AI，请根据任务目标、分步任务列表与所指定的任务id，完成对应的该步任务。"
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
        task_library.update_task_progress(task_cache_id,task_id,function_response,task_result_new)

        print("[DEBUG] 次级AI单元任务执行结果为：",task_result,'\n')
        print("[DEBUG]该单元任务执行结束！！！！！！！！！！！！！！！！！！",'\n')






    #审查单元任务的AI代理（审查单元任务的输入输出是否正确，正确就录入任务数据库，错误就返回信息到任务数据库）
    def review_unit_task_AI_agent(self,task_cache_id):

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


        #获取任务
        task = task_library.read_task_list(task_cache_id)
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
                    function_ai_call = function_library.get_function_by_name(function_name)
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
                task_library.update_task_status(task_cache_id,"完成")
        
        elif review_result_new == "incorrect":
            #提取正确结果
            correct_task_result = review_result_dict["correct_task_result"]
            #直接回退进度
            task_library.delete_task_progress(task_cache_id,task_progress)

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

            #调用函数
            function_response = function_library.call_function(function_name,function_arguments)

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
        #功能函数id "function_id":"0",
        #功能函数名字 "function_name":"",
        #功能函数描述 "function_description":"",
        #功能函数说明（AI调用） "function_ai_call":{},
        #功能函数权限 "function_permission":"0",
        # }
        #添加功能函数
        self.add_function("1", "create_a_task_list", "输入任务目标，次级AI会创建分步式任务列表，并返回", Ai_agent.function_create_a_task_list, "0")
        self.add_function("2", "start_distributed_task_AI_agent", "输入任务目标，任务列表，次级AI代理会开始自动执行任务", Ai_agent.function_start_distributed_task_AI_agent,"0")
        self.add_function("3", "search_related_functions", "根据用户需要到的函数功能的详细描述，进行语义搜索，将最可能有关的的3个功能函数返回", self.function_search_related_functions,"0")
        self.add_function("4", "read_tasks_running_status", "读取任务库中全部任务执行情况", Ai_agent.function_read_tasks_running_status, "0")

    #搜索功能函数------------------------------------------------
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
        function_ai_call_list = function_library.get_function_by_id_list(function_id_list)
        print("[DEBUG]搜索到的功能函数说明（AI调用）：" ,function_ai_call_list,'\n')

        return function_ai_call_list
        
    #功能搜索函数说明（AI调用）
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



    #添加功能函数
    def add_function(self, function_id, function_name, function_description, function_ai_call, function_permission):
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


    #根据函数权限，获取相应的全部功能函数
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
        #存储对话历史的列表
        self.conversation_history = []

        #在文件夹下寻找conversation_history.json文件，如果存在则读取json文件，如果不存在则跳过
        if os.path.exists(os.path.join(self.file_path, "conversation_history.json")):
            with open(os.path.join(self.file_path, "conversation_history.json"), "r", encoding="utf-8") as f:
                self.conversation_history = json.load(f)

        #如果没有找到对话历史文件，则重新构建系统提示语句
        else:
            #构建系统提示语句
            self.prompt = '''你是用户的AI助理，你的任务是利用功能函数库来帮助用户解答疑惑和完成他们交代的任务。当用户向你交代任务时，请判断任务的复杂程度。
            如果任务较为简单，但用户提供的信息不足，请通过提问补充相关信息，然后自主解答或调用函数来解决，必须仅使用为您提供的函数。如果任务较为复杂，请遵循以下步骤：

            1. 如果用户提供的信息较少或模糊，请确保通过提问来获取尽可能详细的信息。
            2. 在确定用户任务的细节后，请务必再次询问用户是否愿意将任务委托给下级AI生成分步式任务列表。在得到用户的肯定回答后，调用相应的函数，将任务详细描述发给下级AI。
            3. 获得分步式任务列表后，交由用户审查，询问用户是否满意。如果用户不满意，你可以再次调用相应的函数，继续生成分步式任务列表。
            4. 如果用户满意，并确认愿意将任务列表交给给下级AI执行，你可以直接调用相应的函数，将分步式任务列表交给给下级AI执行。

            示例1 - 简单任务：
            用户描述：今天天气怎么样？
            处理方法：
            1. 向用户询问他们想要查询哪个地区的天气。
            2. 获取用户的回答后，调用查询天气的函数，传入相应参数，然后将查询结果返回给用户。

            示例2 - 复杂任务：
            用户描述：我想设计一款手机应用，但不知道从哪里开始。
            处理方法：
            1. 向用户询问应用的具体类型、功能和目标用户等相关信息。
            2. 在获取详细信息后，询问用户是否愿意将任务委托给下级AI生成分步式任务列表。
            3. 获得用户的肯定回答后，调用相应的函数，将任务详细描述发给下级AI。
            4. 获取分步式任务列表后，交由用户审查，询问用户是否满意。如有需要，可根据用户反馈再次调用函数生成新的任务列表。
            5. 用户满意并确认愿意将任务列表交给下级AI执行时，调用相应的函数，将分步式任务列表交给给下级AI执行。'''

            #添加系统提示语句到对话历史最前面
            self.conversation_history.insert(0,{"role": "system", "content": self.prompt}) #在列表最前面插入元素

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


        #根据输入用户，生成格式化消息
        if role == "user":
            The_message = {"role": "user", "content": content}

        elif role == "function_call":
            The_message = {"role": "assistant",
                           "content": content ,
                           "function_call": {"name": function_name,
                                             "arguments": function_arguments}

                        }
            
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

        elif role == "assistant":
            The_message = {"role": "assistant", "content": content}

        #将对话记录到列表中
        self.conversation_history.append(The_message)



        #计算对话历史的总tokens数
        self.num_tokens_history = self.num_tokens_from_messages(self.conversation_history)
        #print("[DEBUG] 对话历史tokens数为：",self.num_tokens_history,"个")
        #计算挂载函数的tokens数
        self.num_tokens_functions= 4 * self.num_tokens_from_messages(request.default_functions_list)
        #print("[DEBUG] 挂载函数tokens数为：",self.num_tokens_functions,"个",'\n')

        #如果大于最大tokens数，删除最早的对话记录的第二，第三个元素
        if (self.num_tokens_history + self.num_tokens_functions )  > 4000:
            print("[DEBUG] 对话历史tokens数超过4080，删除最早的对话记录的第二，第三个元素，保留系统提示语句")
            #删除列表索引为1，2的元素
            del self.conversation_history[1:3]


        #将对话记录变量以utf-8格式写入json文件到指定文件夹中
        with open(os.path.join(self.file_path, "conversation_history.json"), "w", encoding="utf-8") as f:
            json.dump(self.conversation_history, f, ensure_ascii=False, indent=4)

    #计算对话历史的tokens的函数
    def num_tokens_from_messages(self,messages, model="gpt-3.5-turbo-0613"):
        """Return the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
            }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif "gpt-3.5-turbo" in model:
            print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            return 0
        elif "gpt-4" in model:
            print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
            return 0
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

    #计算挂载函数的tokens的函数
    def num_tokens_from_functions(self,functions_list, model="gpt-3.5-turbo-0613"):
        pass

        
#————————————————————————————————————————主AI对话请求器————————————————————————————————————————
class Ai_Request:
    def __init__(self):

        #主AI挂载的函数功能列表
        self.default_functions_list = []
        #从数据库获取权限为1的函数功能列表，根据id，再从ai函数数据库读取数据，作为主AI默认挂载函数功能列表
        self.default_functions_list = main_function_library.get_function_by_permission("0")

        #主AI挂载的临时函数功能列表
        self.temp_functions_list = []


    #输入用户消息，向AI发送请求,并取得回复
    def make_request(self,conversationLogger):


        #获取对话历史
        conversation_history = conversationLogger.read_log()
        print('[DEBUG] 主AI请求发送的内容是：',conversation_history,'\n')


        #主AI挂载的所有函数功能列表
        self.all_functions_list = []

        #如果临时函数功能列表不为空，将临时函数功能列表与默认函数功能列表合并为新的列表，并且中间要复制一份，否则会改变默认函数功能列表
        if self.temp_functions_list != []:
            self.all_functions_list = self.default_functions_list.copy()
            self.all_functions_list.extend(self.temp_functions_list) #extend()方法只接受一个列表作为参数，并将该参数的每个元素都添加到原有的列表中

        else:
            self.all_functions_list = self.default_functions_list.copy()
        print('[DEBUG] 主AI挂载的函数是：',self.all_functions_list, '\n')


        #向AI发送请求
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=conversation_history,
            functions=self.all_functions_list,  #关于调用函数说明内容可以放在这里，也可以放在上面的content中，AI都会识别并使用
            function_call="auto"
            )

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
            print("[DEBUG] 主AI正在申请调用函数~",'\n')

            #获取函数调用名称
            function_name = message["function_call"]["name"]
            #获取函数调用参数
            function_arguments = message["function_call"]["arguments"]
            #获取函数调用附加回复
            function_content = message['content']
            print("[DEBUG] 主AI已调用函数附加说明：",function_content,'\n')

            #记录一下AI的函数申请调用回复
            history.log_message("function_call",function_name,function_arguments,function_content)


            #将函数输入参数转换为字典格式
            function_arguments = json.loads(function_arguments)

            #根据函数调用名称，调用相应的管理函数
            if function_name == "search_related_functions":
                function_response = main_function_library.search_related_functions(function_description=function_arguments.get("function_description"))

            elif function_name == "create_a_task_list":
                function_response = Ai_agent.create_a_task_list(task_objectives=function_arguments.get("task_objectives"),)

            elif function_name == "read_tasks_running_status":
                function_response = Ai_agent.read_tasks_running_status()

            elif function_name == "start_distributed_task_AI_agent":
                
                #提取输入参数的任务目标与任务列表
                task_objectives = function_arguments.get("task_objectives")
                task_list = function_arguments.get("task_list")

                #查询任务数据库的任务数
                task_num = task_library.get_task_num()

                #将还是字符串格式的任务列表里的true和false转换为布尔值
                task_list = task_list.replace("true","True")
                task_list = task_list.replace("false","False")

                #处理任务列表，把任务列表转换为列表变量
                task_list = eval(task_list)
                #计算任务列表的长度
                task_list_length = len(task_list)
                
                #创建任务并添加任务到任务数据库中
                task = {
                    "task_cache_id":task_num,
                    "task_status":"进行中",
                    "task_objectives":task_objectives,
                    "task_list":task_list,
                    "task_distribution" : task_list_length,
                    "task_progress":0, 
                }
                task_library.write_task_list(task)

                # # 创建一个新的子线程对象,并传入任务缓存id(必须是可迭代对象)
                # my_thread = threading.Thread(target=Ai_agent.start_distributed_task_AI_agent, args=(task_num,))

                # # 启动子线程任务
                # my_thread.start()

                Ai_agent.start_distributed_task_AI_agent(task_num)

                function_response = '任务已在后台由代理AI开始执行~请耐心等待结果~'

            #调用功能函数库里的函数
            else:
                function_response = function_library.call_function(function_name,function_arguments)

            print("[DEBUG] 主AI已调用的函数为：",function_name,'输入参数为：',function_arguments,'调用结果为：',function_response,'\n')

            #记录函数调用结果
            history.log_message("function_return",function_name,None,function_response)

            #再次发送对话请求
            Ai_response = request.make_request(history)

            #再次提取AI回复内容中message部分
            message = Ai_response["choices"][0]["message"]


        #获取AI回复内容
        content = message['content']
        return content
        

#————————————————————————————————————————主AI对话窗口————————————————————————————————————————
class Chat_window:
    #初始化
    def __init__(self):
        pass

    #开启对话器
    def start_conversation(self):
        while 1 :
            #获取用户输入
            user_input = input("【用户】：")
            print("\n")

            #记录用户输入
            history.log_message("user",None,None,user_input)

            #发送对话请求
            Ai_response = request.make_request(history)

            #调用AI解析器来解析回复，并自动执行函数调用
            content = parser.parse_response(Ai_response)

            #输出AI纯文本回复内容
            print("【助手】：",content,"\n")

            #记录AI纯文本回复
            history.log_message("assistant", None, None, content)
        
        


#————————————————————————————————————————主程序————————————————————————————————————————
if __name__ == '__main__':
    # 获取当前工作目录
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0])) 
    print("[INFO] 当前工作目录是:",script_dir,'\n') 

    #注册api
    Api_key = "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"
    openai.api_key = Api_key

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

    #创建主AI记忆库
    history = Ai_memory(script_dir)

    #创建AI代理
    Ai_agent = cot_mode()

    #创建功能函数库
    function_library = Function_library()

    #创建主AI功能函数库
    main_function_library = Main_AI_function_library()

    #创建任务库
    task_library = Task_library()

    #创建AI请求器
    request = Ai_Request()

    #创建AI解析器
    parser = Ai_Parser()

    #创建聊天窗口
    chat = Chat_window()

    #根据函数权限，获取功能函数库的函数描述与函数id
    function_id_list,function_description_list = function_library.get_all_function("1")
    #将功能函数库的函数描述向量化并存储
    collection.add(
    documents=function_description_list,
    ids=function_id_list #不支持数字id
)
    print("[INFO] 功能函数描述向量化完成！","\n")


    #欢迎用户
    print("【助手】：欢迎使用AI助手！","\n")

    #开启对话器
    chat.start_conversation()



