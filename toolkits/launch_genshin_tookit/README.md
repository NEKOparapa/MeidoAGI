
<h1><p align='center' >启动原神客户端工具</p></h1>



#  工具介绍
***
   启动原神.exe



* ### 工具配置
***
   配置文件路径，如D:\Software\Genshin Impact\launcher.exe
  

# 工具调用规范
***
   ```
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
   ```


