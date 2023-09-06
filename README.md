
<h1><p align='center' >MeidoAGI</p></h1>

<p align='center' >一款可灵活拓展功能，可自定义语音和界面模型的桌宠AI代理</p>


#  环境支持🏕️
***
   
 * **`魔法工具`**:我们**强烈建议**您选择优质稳定的代理工具,不然api接口会频繁报错无法连接,显示错误代码443或者一直没有回复
 * **`Python环境`**:[下载地址](https://www.python.org/downloads/) 下载安装3.10及以上的版本，并在安装时如果有“add to path”选项，请勾选上。
 * **`Node.js环境`**:[下载地址](https://nodejs.org/zh-cn) 下载安装左边的稳定版即可
 * **`Chat-GPT账号`**:建议您新建一个API_Key,并且最好在使用期间不要和其他程序一起使用,不然容易达到请求次数限制

# 首次使用📝
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

# 项目运行🕹️ 
***
* ### 女仆启动！
   在根目录下依次打开`启动语音模块`，`启动交互界面`，`启动MeidoAGI`

# 工具编写规范🧰 
***
* ### 第一步：编写完整的可调用Python函数和函数调用说明！
   在编写过程中如果函数名如果是 `def example_functions() ` ,则对应的函数调用说明字典名字则应该是`funtion_` + `example_functions`,最终是`funtion_example_functions`.
   下面是一个工具脚本完整编写示例
   ```
   #python3.10 版本请使用下面命令
   pip install https://github.com/Artrajz/archived/raw/main/fasttext/fasttext-0.9.2-cp310-cp310-win_amd64.whl
   #python3.9  版本请使用下面命令
   pip install https://github.com/Artrajz/archived/raw/main/fasttext/fasttext-0.9.2-cp39-cp39-win_amd64.whl
   ```
* ### 第二步：放置脚本文件
   在根目录的toolkits文件夹中，创建专属文件夹，并放进脚本。还希望同时放入一份README.md，用来简单说明一下脚本的功能，如果有配置文件，则写明一下配置的教程。



* ### 第三步：放置相关配置文件（可选）
   如果你的项目需要用户自行配置类似平台key，账号许可等内容，请把配置文件放在data文件夹里的Extended_Configuration文件夹里

