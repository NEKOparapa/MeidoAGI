
<h1><p align='center' >谷歌搜索工具</p></h1>



#  工具介绍
***
   使用谷歌来进行搜索



* ### 工具配置
***
 * KEY 从 谷歌云 API 控制台 https://console.developers.google.com/apis/credentials 来的。
 * CX 从 谷歌可编程搜索 https://programmablesearchengine.google.com/controlpanel/create  中来
 * 一天只有 100 次的免费搜索限额，只能查询前 100 条。如需增加则 5 刀 1000 次，但一天上限 10000。 次，对于我来说已经足够用了
 * 具体获取教程请参考 https://www.jianshu.com/p/be6a2783758f

  

# 工具调用规范
***
   ```
   #配套工具调用说明
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


<h1><p align='center' >直接打开网站工具</p></h1>



#  工具介绍
***
   使用默认浏览器直接打开指定的网站



* ### 工具配置
***
无


# 工具调用规范
***
   ```
   #配套工具调用说明
   function_open_website  = {
           "type": "function",
           "function": {
                       "name": "open_website",
                       "description": "输入网站，将自动调用系统默认浏览器打开该网站",
                       "parameters": {
                           "type": "object",
                           "properties": {
                               "website_url": {
                                   "type": "string",
                                   "description": "网站",
                               }
                           },
                           "required": ["website_url"]
                       },
                   }
   }
   ```


