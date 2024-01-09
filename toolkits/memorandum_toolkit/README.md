
<h1><p align='center' >读写备忘录工具</p></h1>



#  工具介绍
***
   将用户的重要信息记录到备忘录中，也可以之后进行查询


* ### 工具配置
***
   无
  

# 工具调用规范
***
   ```
    # 写入备忘录函数的调用规范
    function_write_memorandum  = {
            "type": "function",
            "function": {
                        "name": "write_memorandum",
                        "description": "将输入的内容记录在用户的备忘录中",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "text": {
                                    "type": "string",
                                    "description": "需要记录的文本内容",
                                }
                            },
                            "required": ["text"]
                        },
                    }
    }


    # 查询备忘录函数的调用规范
    function_query_memorandum  = {
            "type": "function",
            "function": {
                        "name": "query_memorandum",
                        "description": "输入关键字，在用户的备忘录中搜索相关的内容",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "text": {
                                    "type": "string",
                                    "description": "需要搜索的关键字",
                                }
                            },
                            "required": ["text"]
                        },
                    }
    }






   ```


