import json
import os
import importlib.util
import inspect


#————————————————————————————————————————功能函数库————————————————————————————————————————
class Function_library():
    #初始化功能函数库
    def __init__(self):
        #功能函数库
        self.function_library = {}
        # 每个函数为键值对结构，key为函数id（int），value为函数内容，例如下面的示例
        # key:0 
        # value:{
        #函数id   "function_id":"0",
        #函数名字 "function_name":"",
        #函数描述 "function_description":"",
        #函数说明 "function_ai_call":{},
        #内存地址 "function_address":"",
        #函数权限 "function_permission":"0",
        #函数分类 "function_category": "",
        #启用状态 "function_enabled": False
        # }

        #获取当前文件夹路径
        folder_path = os.path.dirname(os.path.abspath(__file__))
        #拼接新的文件夹路径
        #folder_path = os.path.join(folder_path,"expansion_toolkit")

        
        #构建功能函数库
        for module in self.import_all_modules_in_folder(folder_path):
            #获取指定文件夹下的所有模块中的所有类，函数，字典
            classes, funcs, dicts = self.get_all_classes_funcs_dicts_in_module(module)
            #过滤字典，只保留以function_开头的字典
            dicts_with_prefix = self.filter_dicts_by_prefix("function_", dicts)

            print(f"Import Module: {module.__name__}")
            #print(f"Classes: {classes}")
            print(f"Functions : {funcs}")
            print(f"Dictionaries with prefix 'function_': {dicts_with_prefix}")
            print()

            #筛选函数并录入功能函数库
            for func_name, func in funcs: #遍历函数库中的函数
                #print(f"Function: {func_name}")
                #print(f"Function code: {inspect.getsource(func)}")
                new_func_name = "function_" + func_name #构建对应的函数调用说明字典的名字
                for dict_name, dict_obj in dicts_with_prefix: #遍历字典库中的字典
                    #print(f"Dictionary: {dict_name}")
                    #print(f"Dictionary code: {dict_obj}")
                    if new_func_name == dict_name: #如果存在名字相同的字典，表示找到了该函数对应的函数调用说明字典

                        #计算function_library的长度，用于构建新的function_id
                        function_id = len(self.function_library) + 1
                        #获取函数调用说明字典中的内容
                        function_ai_call = dict_obj
                        #获取函数调用说明字典中的函数名字
                        function_name = function_ai_call["name"]
                        #获取函数调用说明字典中的函数描述
                        function_description = function_ai_call["description"]
                        #获取函数调用说明字典中的函数权限
                        function_permission = "1"
                        
                        #构建功能函数结构
                        functions = {
                            "function_id": str(function_id), #转换成str类型,是为了chromadb向量数据库不出错
                            "function_name": function_name,
                            "function_description": function_description,
                            "function_ai_call": function_ai_call,
                            "function_address":func,
                            "function_permission": function_permission,
                            "function_category": module.__name__,
                            "function_enabled": True,
                        }
                        #录入功能函数库
                        self.function_library[int(function_id)] = functions

        #写入缓存文件中
        self.auto_write_function_library()


    # 输入函数名字和参数字典，在功能函数库中调用该函数，并根据函数调用说明字典中关于参数的说明与输入的参数字典，动态输入参数
    def call_function(self,function_name, input_parameter):
        #根据函数名字，在函数功能库中查找，并获取函数信息
        for function_id, function_info in self.function_library.items():    #遍历功能函数库，注意是字典结构，所以需要用到items()方法
            if function_name == function_info["function_name"]:
                code = 1
                break
            else:
                code = 0
        #如果没有找到对应的函数，返回错误信息
        if code == 0:
            return "没有找到对应的函数"
        
        #获取函数内存地址
        function = function_info["function_address"]

        #获取函数调用说明字典
        function_ai_call = function_info["function_ai_call"]
        
        #获取函数调用说明字典中的参数说明字典
        function_parameters = function_ai_call["parameters"]["properties"]

        #获取必需给出的输入参数列表
        function_required = function_ai_call["parameters"]["required"]
        
        #遍历参数说明字典，根据参数说明字典中的参数名字，从输入的参数字典中获取对应的参数值
        args = {}
        for key, value in function_parameters.items():
            if key in input_parameter:
                #构建输入参数字典
                args[key] = input_parameter[key]

        #检查一下输入的参数是否完整
        missing_keys = [key for key in function_required if key not in args]
        if missing_keys:
            return f"输入的参数不完整，缺少以下必需参数：{', '.join(missing_keys)}"

        #调用函数
        result = function(**args)#* 和 ** 是解包运算符（列表和字典），它们用于解包数据结构中的元素，可以将字典中的键值对作为参数传入函数
        return result





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
    

    #动态导入指定文件夹包括子文件夹的所有模块
    def import_all_modules_in_folder(self, folder_path):
        for root, dirs, files in os.walk(folder_path):
            python_files = [f for f in files if f.endswith('.py')]
            for python_file in python_files:
                module_name = os.path.splitext(python_file)[0]  # remove '.py' from file name
                script_path = os.path.join(root, python_file)  # get the full path of the script
                spec = importlib.util.spec_from_file_location(module_name, script_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                yield module#迭代器，每次迭代时都产生一个模块，而不是一次性产生所有模块，便于节省内存与下面使用for循环遍历


    # #动态导入指定文件夹的所有模块
    # def import_all_modules_in_folder(self,folder_path):
    #     python_files = [f for f in os.listdir(folder_path) if f.endswith('.py')]
    #     module_names = [f[:-3] for f in python_files]  # remove '.py' from file names
    #     for module_name in module_names:
    #         spec = importlib.util.spec_from_file_location(module_name, os.path.join(folder_path, f"{module_name}.py"))
    #         module = importlib.util.module_from_spec(spec)
    #         spec.loader.exec_module(module)
    #         yield module #迭代器，每次迭代时都产生一个模块，而不是一次性产生所有模块，便于节省内存与下面使用for循环遍历

    #获取指定模块中的所有类，函数，字典
    def get_all_classes_funcs_dicts_in_module(self,module):
        classes = []
        funcs = []
        dicts = []
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                classes.append(obj)
            elif inspect.isfunction(obj):
                funcs.append((name, obj))  # store both the name and the function
            elif isinstance(obj, dict):  # check if object is a dictionary
                dicts.append((name, obj))  # store both the name and the dict
        return classes, funcs, dicts

    #根据前缀过滤字典
    def filter_dicts_by_prefix(self,prefix, dicts):
        return [(name, d) for name, d in dicts if name.startswith(prefix)]
    

    #自动把功能函数库写为json文件
    def auto_write_function_library(self):

        #复制一份，避免修改到原字典
        function_library = self.function_library.copy()

        #遍历删除函数库里的内存地址，否则无法写为json文件
        for value in function_library.values():
            if "function_address" in value:
                del value["function_address"]

        # 获取当前文件夹路径
        folder_path = os.path.dirname(os.path.abspath(__file__))
        # 拆分路径，获取父目录和最后一个文件夹的名称
        parent_dir, last_folder = os.path.split(folder_path)
        # 删除最后一个文件夹
        new_folder_path = parent_dir
        # 拼接新的文件路径
        folder_path = os.path.join(new_folder_path, "data", "function_library.json")

        #把任务库写入到本地文件中，指定编码格式为utf-8
        with open(folder_path, "w", encoding="utf-8") as f:
            json.dump(function_library, f, ensure_ascii=False, indent=4)