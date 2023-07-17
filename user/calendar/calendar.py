

#创建日程表类
class calendar :
      #初始化日程表
    def __init__(self):
        self.my_calendar = {}
        #每个日程安排为键值对结构，key为日期，value为日程内容，例如下面的示例
        #key:2020-01-01
        #value:[]
        #下面是value列表的中某个安排示例
        # {
        #事件id "calendar_id":0,
        #事件名称 "calendar_name":"元旦节",
        #事件内容 "calendar_content":"今天是元旦节",
        #事件日期 "calendar_date":"2020-01-01",
        #事件时间 "calendar_time":"00:00:00",
        #事件状态 "calendar_status":"未完成",
        #事件执行结果 "calendar_result":""
        # }

#日程表执行器（循环自动查询日程表并提交到任务库执行，自动查询任务结果）
#原理大概是检测现在时间大于计划时间，就执行任务。
#执行结果以特定格式插入对话中，角色试一下用户和助手和函数看看。如：【系统消息】2020-01-01日程xxxxx时间任务执行结果，请告诉用户：今天是元旦节。
class calendar_executor:
    pass