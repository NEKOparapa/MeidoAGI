
<h1><p align='center' >编写txt文件工具</p></h1>



#  工具介绍
***
   输入路径，将文本内容写入新的txt文件中


* ### 工具配置
***
   无
  

# 工具调用规范
***
   ```
   #配套函数调用说明
   function_write_text_to_file  = {
           "type": "function",
           "function": {
                       "name": "write_text_to_file",
                       "description": "将文本内容写为txt文件保存",
                       "parameters": {
                           "type": "object",
                           "properties": {
                               "folder_path": {
                                   "type": "string",
                                   "description": "存储的文件夹路径,例如：D:/MeidoAGI/folder",
                               },
                               "text_content": {
                                   "type": "string",
                                   "description": "文本内容",
                               }
                           },
                           "required": ["folder_path","text_content"]
                       },
                   }
   }
   ```


