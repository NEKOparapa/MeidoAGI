import ctypes
import os
import subprocess
import time
import yaml
import sys

#当以管理员权限运行该脚本时，则自动启动原神客户端
if ctypes.windll.shell32.IsUserAnAdmin():
    print("[DEBUG] 已经成功使用管理员权限自运行") 

    #获取当前路径，自运行时，脚本路径会改变，所以得改变读取配置路径
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    # 使用两次os.path.dirname，来获取上两级目录的路径
    parent_dir = os.path.dirname(os.path.dirname(script_dir))
    print("[DEBUG] 构建配置文件读取路径：",parent_dir) 


    # 读取 YAML 配置文件
    config_path = os.path.join(parent_dir, "config", "Extended_Configuration" ,"genshin_impact_path.yaml")
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
        # 访问具体配置项
        path = config['genshin_impact']['path']
    print("[DEBUG] 已成功读取原神客户端路径：",path) 

    #启动原神
    subprocess.Popen(path)
    print("[DEBUG] 已成功运行原神客户端") 
    time.sleep(2)
 


def launch_genshin_impact(switch):

    #获取当前路径
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0])) 

    # 读取 YAML 配置文件
    try:
        config_path = os.path.join(script_dir, "config", "Extended_Configuration" ,"genshin_impact_path.yaml")
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            # 访问具体配置项
            path = config['genshin_impact']['path']
        
        #检查一下配置是否为空
        if path == None:
            return ("配置文件内容为空，请填写配置信息")

    except :
        return ("无法正确读取配置文件，请重新检查并配置相关信息")

    #尝试启动原神
    try:
        #如果拥有管理员权限
        if ctypes.windll.shell32.IsUserAnAdmin():
            subprocess.Popen(path)
            return("成功启动原神游戏客户端！")
        #如果没有管理员权限
        else:
            # 以管理员权限重新运行该脚本
            ctypes.windll.shell32.ShellExecuteW(None,"runas", sys.executable, __file__, None, 1)
            return("成功启动原神游戏客户端！")
        
    except Exception as e:
        return("启动原神游戏客户端时出现错误：", e)







#配套函数调用说明
function_launch_genshin_impact  = {
        "type": "function",
        "function": {
                    "name": "launch_genshin_impact",
                    "description": "启动运行原神游戏客户端",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "switch": {
                                "type": "string",
                                "description": "输入on，则立即启动原神游戏客户端",
                            },
                        },
                        "required": ["switch"]
                    },
                    }
}