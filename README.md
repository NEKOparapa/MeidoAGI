
<h1><p align='center' >MeidoAGI</p></h1>

<p align='center' >一款可灵活拓展功能，可自定义语音和界面模型的桌宠AI</p>


#  环境支持🏕️
***
   
 * **`魔法工具`**:选择优质稳定的代理工具,不然api接口会频繁报错无法连接,显示错误代码443或者一直没有回复
 * **`Python环境`**:[下载地址](https://www.python.org/downloads/) 下载安装3.10及以上的版本，并在安装时如果有“add to path”选项，请勾选上。
 * **`Node.js环境`**:[下载地址](https://nodejs.org/) 下载安装左边的稳定版即可
 * **`Chat-GPT账号`**:建议您新建一个API_Key,并且最好在使用期间不要和其他程序一起使用,不然容易达到请求次数限制

# 首次使用📝
***
* ### 安装pip依赖
   在根目录下打开CMD窗口，并输入下面安装全部依赖库命令:
   ```
   pip install -r requirements.txt
   ```
* ### 安装npm依赖
   在live2d目录下打开CMD窗口，先运行
   ```
   npm install -g cnpm --registry=https://registry.npmmirror.com
   ```
   
   再运行
   ```
   cnpm install --save-dev electron
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
 * **`谷歌搜索`**:需要配置谷歌key以及CX码 [配置说明](https://github.com/NEKOparapa/MeidoAGI/blob/main/toolkits/google_search_toolkit/README.md)
 * **`启动原神`**:配置原神客户端的文件路径[配置说明](https://github.com/NEKOparapa/MeidoAGI/blob/main/toolkits/launch_genshin_tookit/README.md)

# 项目运行🕹️ 
***
* ### 女仆启动！
   打开系统代理，并在根目录下依次打开`启动语音模块`，`启动交互界面`，`启动MeidoAGI`

# 现有的AI工具🕹️ 
***
* **`谷歌搜索`**:使用谷歌进行搜索
* **`打开网站`**:自动调用默认浏览器打开网站
* **`获取今日动漫更新信息`**:自动抓取动漫资讯网站的更新信息
* **`启动原神客户端`**:原神，启动
* **`编写txt文件`**:指定路径，将文本内容写为txt文件

# 工具编写规范🧰 
***
* ### 第一步：编写完整的可调用Python函数和函数调用说明！
   在编写过程中如果函数名如果是 `def example_functions() ` ,则对应的函数调用说明字典名字则应该是`funtion_` + `example_functions`,最终是`funtion_example_functions`.
   下面是一个工具脚本完整编写示例
   ```
   import json
   
   
   #获取给定位置的当前天气--------------------------------------------
   def get_current_weather(location, unit):
       """Get the current weather in a given location"""
       weather_info = {
           "location": location,
           "temperature": "31",
           "unit": unit,
           "forecast": "晴天",
       }
       return json.dumps(weather_info)
   
   #对应的函数调用说明，包括函数名字，描述，参数，参数类型，参数范围，参数描述，必需给出的参数
   function_get_current_weather = {
           "type": "function",
           "function": {
               "name": "get_current_weather", #函数名字
   
               "description": "输入位置与温度单位，获取给定位置的当前天气", #函数描述
   
               "parameters": { "type": "object", 
                               "properties": {"location": {"type": "string",     # 参数类型
                                                           "description": "需要查询的城市，例如南宁、北京", # 参数描述
                                                           },
                                               "unit": {"type": "string",  # 参数类型
                                                       "enum": ["摄氏度", "华氏度"],    # 参数范围
                                                       "description": "使用的温度单位，从用户语言进行推断。" # 参数描述
                                                       },
                                               },
                               "required": ["location","unit"], #必需给出的参数
                               },
                   }
   }
   ```
* ### 第二步：放置脚本文件
   在根目录的toolkits文件夹中，创建专属文件夹，并放进脚本。还希望同时放入一份README.md，用来简单说明一下脚本的功能，如果有配置文件，则写明一下配置的教程。




* ### 放置相关配置文件和添加依赖库（可选）
   如果你的项目需要用户自行配置类似平台key，账号许可等内容，请把配置文件放在data文件夹里的Extended_Configuration文件夹里
  
   如果需要到新的依赖库，请添加到根目录的requirements.txt里最下面的tool类下

