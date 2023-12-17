
<h1><p align='center' >谷歌搜索工具</p></h1>



#  工具介绍
***
   使用谷歌来进行搜索



* ### 工具配置
***
 * KEY 从 谷歌云 API 控制台 https://console.developers.google.com/apis/credentials 来的，需要有外币卡先注册谷歌云账号。但似乎付费的话就不用这个 KEY 了，仅用 CX 即可，这个待查。
 * CX 从 谷歌可编程搜索 https://programmablesearchengine.google.com/controlpanel/create  中来
 * 一天只有 100 次的免费搜索限额，只能查询前 100 条。如需增加则 5 刀 1000 次，但一天上限 10000。 次，对于我来说已经足够用了
 * 具体获取教程请参考 https://www.jianshu.com/p/be6a2783758f

  

# 工具调用规范
***
   ```
   #配套函数调用说明
   function_google_search  = {
           "type": "function",
           "function": {
                       "name": "google_search",
                       "description": "输入关键字、短语或问题等，谷歌将根据这些关键词提供相关的搜索结果",
                       "parameters": {
                           "type": "object",
                           "properties": {
                               "search_words": {
                                   "type": "string",
                                   "description": "需要搜索的关键字、短语或问题等",
                               }
                           },
                           "required": ["search_words"]
                       },
                   }
   }
   ```


