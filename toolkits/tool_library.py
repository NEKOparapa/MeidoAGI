import json
import os
import importlib.util
import inspect


#————————————————————————————————————————工具库————————————————————————————————————————
class Tool_library():
    #初始化工具库
    def __init__(self):
        self.tool_library = {}
        # 每个工具为键值对结构，key为工具id（int），value为工具内容，例如下面的示例
        # key:0 
        # value:{
        #工具id   "tool_id":"0",
        #工具名字 "tool_name":"",
        #工具描述 "tool_description":"",
        #工具调用规范 "tool_specifications":{},
        #内存地址 "tool_address":"",
        #工具权限 "tool_permission":"0",
        #工具分类 "tool_category": "",
        #启用状态 "tool_enabled": False
        # }

        #获取当前文件夹路径
        folder_path = os.path.dirname(os.path.abspath(__file__))

        
        #构建工具库
        for module in self.import_all_modules_in_folder(folder_path):
            #获取指定文件夹下的所有模块中的所有类，函数，字典
            classes, funcs, dicts = self.get_all_classes_funcs_dicts_in_module(module)
            #过滤字典，只保留以function_开头的字典
            dicts_with_prefix = self.filter_dicts_by_prefix("function_", dicts)

            print(f"已导入工具: {module.__name__}")
            #print(f"Classes: {classes}")
            print(f"工具内存地址 : {funcs}")
            print(f"工具功能描述': {dicts_with_prefix}")
            print()

            #筛选函数并录入工具库
            for func_name, func in funcs: #遍历所获得函数中的每个函数
                #print(f"Function: {func_name}")
                #print(f"Function code: {inspect.getsource(func)}")
                new_func_name = "function_" + func_name #构建匹配的工具调用规范的名字

                for dict_name, dict_obj in dicts_with_prefix: #遍历字典库中的字典
                    #print(f"Dictionary: {dict_name}")
                    #print(f"Dictionary code: {dict_obj}")
                    if new_func_name == dict_name: #如果存在名字相同的字典，表示找到了该工具对应的工具调用规范

                        #计算function_library的长度，用于构建新的工具id
                        tool_id = len(self.tool_library) + 1
                        #获取工具调用规范中的内容
                        tool_specifications = dict_obj
                        #获取工具调用规范中的工具名字
                        tool_name = tool_specifications["function"]["name"]
                        #获取工具调用规范中的工具描述
                        tool_description = tool_specifications["function"]["description"]
                        #获取工具调用规范中的工具权限
                        tool_permission = "1"
                        
                        #构建工具结构字典
                        functions = {
                            "tool_id": str(tool_id), #转换成str类型,是为了chromadb向量数据库不出错
                            "tool_name": tool_name,
                            "tool_description": tool_description,
                            "tool_specifications": tool_specifications,
                            "tool_address":func,
                            "tool_permission": tool_permission,
                            "tool_category": module.__name__,
                            "tool_enabled": True,
                        }
                        #录入工具库
                        self.tool_library[int(tool_id)] = functions


    # 输入工具名字和参数，在工具库中调用该工具，并根据工具调用规范关于参数的说明与输入的参数字典，动态输入参数
    def call_tool(self,tool_name, input_parameter):
        #根据工具名字，在工具库中查找，并获取工具相关信息
        for tool_id, tool_info in self.tool_library.items():    #遍历工具库，注意是字典结构，所以需要用到items()方法
            if tool_name == tool_info["tool_name"]:
                code = 1
                break
            else:
                code = 0
        #如果没有找到对应的工具，返回错误信息
        if code == 0:
            return "[error]没有找到对应的工具"
        
        #打印输出此时调用的工具全部信息，方便调试
        #print(f"调用的工具全部信息：{function_info}")

        #获取工具内存地址
        try:
            function = tool_info["tool_address"]
        except:
            return "[error]没有找到对应的工具内存地址"

        #获取工具调用规范
        try:
            tool_specifications = tool_info["tool_specifications"]
        except:
            return "[error]没有找到对应的工具调用规范"
        
        #获取工具调用规范中的参数说明字典
        try:
            function_parameters = tool_specifications["function"]["parameters"]["properties"]
        except:
            return "[error]没有找到对应的参数说明字典"

        #获取必需给出的输入参数列表
        try:
            function_required = tool_specifications["function"]["parameters"]["required"]
        except:
            return "[error]没有找到对应的必需参数列表"
        
        #遍历参数说明字典，根据参数说明字典中的参数名字，从输入的参数字典中获取对应的参数值
        try:
            args = {}
            for key, value in function_parameters.items():
                if key in input_parameter:
                    #构建输入参数字典
                    args[key] = input_parameter[key]
        except:
            return "[error] 无法正常提取输入的参数内容"
        
        #检查一下输入的参数是否完整
        missing_keys = [key for key in function_required if key not in args]
        if missing_keys:
            return f"输入的参数不完整，缺少以下必需参数：{', '.join(missing_keys)}"

        #调用工具
        try:
            result = function(**args)#* 和 ** 是解包运算符（列表和字典），它们用于解包数据结构中的元素，可以将字典中的键值对作为参数传入工具
        except Exception as e:
            print("[ERROR] 调用该工具时出错,无法成功运行，错误信息为：",e,'\n')
            result = "[ERROR] 调用该工具时出错,无法成功运行，错误信息为：" + str(e)

        return result





    #根据工具权限，获取相应的全部工具调用规范
    def get_tool_by_permission(self, permission):
        function_list = []
        #遍历工具库，注意是字典结构，所以需要用到items()方法
        for tool_id, function in self.tool_library.items():
            if function["tool_permission"] == permission:
                #只获取工具调用规范的内容
                tool_specifications = function["tool_specifications"].copy()
                function_list.append(tool_specifications)
        return function_list


    #输入工具名字，获取对应的工具调用规范的内容
    def get_tool_by_name(self, tool_name):
        #遍历工具库，注意是字典结构，所以需要用到items()方法
        for tool_id, function in self.tool_library.items():
            if function["tool_name"] == tool_name:
                #只获取工具调用规范的内容
                tool_specifications = function["tool_specifications"].copy()
                return tool_specifications



    #输入单个工具id，获取id对应的工具调用规范的内容
    def get_tool_by_id(self, tool_id):
        #转换成int类型
        tool_id = int(tool_id)

        #根据id获取工具
        function = self.tool_library[tool_id]

        #只获取工具调用规范的内容
        tool_specifications = function["tool_specifications"].copy()
        return tool_specifications



    #输入包含工具id的列表，获取id对应的工具调用规范的内容，并以列表返回
    def get_tool_by_id_list(self, tool_id_list):
        tool_list = []
        #遍历工具库，注意是字典结构，所以需要用到items()方法
        for tool_id, function in self.tool_library.items():
            #需要对输入列表中的id进行遍历
            for id in tool_id_list:
                if function["tool_id"] == id:
                    #只获取工具调用规范的内容
                    tool_specifications = function["tool_specifications"].copy()
                    tool_list.append(tool_specifications)
        return tool_list

        
    #根据输入工具权限，获取全部工具描述，和对应的工具id，作为两个不同的列表返回
    def get_all_tools(self,tool_permission):
        tool_id_list = []
        tool_description_list = []
        #遍历工具库，注意是字典结构，所以需要用到items()方法
        for tool_id, function in self.tool_library.items():
            if function["tool_permission"] == tool_permission:
                tool_id_list.append(function["tool_id"])
                tool_description_list.append(function["tool_description"])
        return tool_id_list,tool_description_list
    

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

    #获取指定模块中的所有类，工具，字典
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
    

