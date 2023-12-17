
<h1><p align='center' >获取动漫更新信息工具</p></h1>



#  工具介绍
***
   抓取 https://yuc.wiki/ 网站上的动漫更新信息，来获取今日的动漫更新列表



* ### 工具配置
***
   无
  

# 工具调用规范
***
   ```
   #配套函数调用说明
   function_anime_schedule_scraper  = {
           "type": "function",
           "function": {
                       "name": "anime_schedule_scraper",
                       "description": "获取当前季度的当天的动漫更新信息",
                       "parameters": {
                           "type": "object",
                           "properties": {
                               "switch": {
                                   "type": "string",
                                   "description": "调用该功能，则输入on",
                               }
                           },
                           "required": ["switch"]
                       },
                   }
   }
   ```


