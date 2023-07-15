

#————————————————————————————————————————任务库————————————————————————————————————————
import json


class Task_library():
    #初始化任务库
    def __init__(self):
        #任务库
        self.task_list_library = {}
        # 每个任务为键值对结构，key为任务缓存id，value为任务内容，例如下面的示例
        # key:0 
        # value:{
        #任务缓存id "task_cache_id":0,
        #任务状态 "task_status":"未开始",
        #任务目标 "task_objectives":"",
        #任务分步式列表 "task_list":[],
        #任务分步数 "task_distribution":5,
        #任务已完成进度 "task_progress":0, 
        # }

        #任务分步式列表结构示例
        self.task_list_example =[
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

    #查询任务库的任务数量
    def get_task_num(self):
        return len(self.task_list_library)

    #返回全部任务
    def read_all_task_list(self):
        return self.task_list_library

    #写入任务
    def write_task_list(self,task):
        #获取任务缓存id
        task_cache_id = int(task["task_cache_id"])
        #写入任务
        self.task_list_library[task_cache_id] = task

        #自动写入到本地文件中
        self.auto_write_task_list()

    #根据任务缓存id，读取相应任务
    def read_task_list(self,task_cache_id):
        #根据任务缓存id，找到相应任务
        task = self.task_list_library[task_cache_id]
        return task


    #根据任务缓存id，录入函数调用结果，任务执行结果与更新任务进度
    def update_task_progress(self,task_cache_id,task_id,function_response,task_result):
        #根据任务缓存id作为key，找到相应任务
        task = self.task_list_library[task_cache_id]
        #根据任务进度，把函数调用结果与任务执行结果写入任务列表
        for task_unit in task["task_list"]:
            if task_unit["task_id"] == task_id:

                #把函数调用结果与任务执行结果添加到任务列表中,如果列表中已经有了，就更新，没有就添加新键值对
                if function_response:
                    task_unit["function_response"] = function_response
                if task_result:
                    task_unit["task_result"] = task_result

                #更新任务进度
                task["task_progress"] = task_id 

        #自动写入到本地文件中
        self.auto_write_task_list()

    ##根据任务缓存id，删除函数调用结果，任务执行结果与回退一步任务进度
    def delete_task_progress(self,task_cache_id,task_progress):
        #根据任务缓存id作为key，找到相应任务
        task = self.task_list_library[task_cache_id]
        #根据任务进度，把函数调用结果与任务执行结果写入任务列表
        for task_unit in task["task_list"]:
            if task_unit["task_id"] == task_progress:
                #删除函数调用结果与任务执行结果
                del task_unit["function_response"]
                del task_unit["task_result"]
                #回退任务进度
                task["task_progress"] = task_progress - 1

        #自动写入到本地文件中
        self.auto_write_task_list()
    
    #根据任务缓存id，更新任务状态
    def update_task_status(self,task_cache_id,task_status):
        #根据任务缓存id作为key，找到相应任务
        task = self.task_list_library[task_cache_id]
        #更新任务状态
        task["task_status"] = task_status

        #自动写入到本地文件中
        self.auto_write_task_list()

    #根据任务缓存id，获取任务状态
    def get_task_status(self,task_cache_id):
        #根据任务缓存id作为key，找到相应任务
        task = self.task_list_library[task_cache_id]
        #获取任务状态
        return task["task_status"]
    

    #自动写入到本地文件中,方便debug
    def auto_write_task_list(self):
        #把任务库写入到本地文件中，指定编码格式为utf-8
        with open("task_list_library.json", "w", encoding="utf-8") as f:
            json.dump(self.task_list_library, f, ensure_ascii=False, indent=4)
