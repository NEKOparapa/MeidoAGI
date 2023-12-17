
<h1><p align='center' >谷歌搜索工具</p></h1>



#  工具功能🏕️
***
   使用谷歌来进行搜索

# 工具配置📝
***
* ### 下载python依赖
   在根目录下打开CMD窗口，并输入下面安装全部依赖库命令:
   ```
   pip install -r requirements.txt
   ```
   windows下可能安装不了其中的fasttext,可以用以下命令单独安装
   ```
   #python3.10 版本请使用下面命令
   pip install https://github.com/Artrajz/archived/raw/main/fasttext/fasttext-0.9.2-cp310-cp310-win_amd64.whl
   #python3.9  版本请使用下面命令
   pip install https://github.com/Artrajz/archived/raw/main/fasttext/fasttext-0.9.2-cp39-cp39-win_amd64.whl
   ```
* ### 系统配置
   在根目录下打开data文件夹，记事本打开System_Configuration.yaml文件:
   ```
   # openai配置
   openai:
     api_key:
   
   # 日程表配置
   calendario:
     switch: off
   ```
   里面配置内容暂时为上面内容，请在api-key后面放入由Chat-GPT账号生成的API_Key，如果需要打开日程表执行功能，把off改为on

* ### 工具配置
   在根目录下打开data/Extended_Configuration文件夹:
   。。。。。。。。
  

# 工具调用规范🧰 
***

   ```
   
   #对应的函数调用说明，包括函数名字，描述，参数，参数类型，参数范围，参数描述，必需给出的参数
   function_get_current_weather = {
               "name": "get_current_weather", #函数名字
   
               "description": "输入位置与温度单位，获取给定位置的当前天气", #函数描述
   
               "parameters": { "type": "object", 
                               "properties": {"location": {"type": "string",     #参数类型
                                                           "description": "需要查询的城市，例如南宁、北京", #参数描述
                                                           },
                                               "unit": {"type": "string",  
                                                       "enum": ["摄氏度", "华氏度"],    #参数范围
                                                       "description": "使用的温度单位，从用户语言进行推断。" #参数描述
                                                       },
                                               },
                               "required": ["location","unit"], #必需给出的参数
                               },
                   }
   ```


