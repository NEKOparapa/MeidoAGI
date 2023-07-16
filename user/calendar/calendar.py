

#创建日程表类
class calendar :
      #初始化日程表
    def __init__(self):
        self.my_calendar = {}
        #每个日程安排为键值对结构，key为日期，value为日程内容，例如下面的示例
        #key:2020-01-01
        #value:{
        #日程内容 "calendar_content":"今天是元旦节",
        #日程状态 "calendar_status":"未完成",
        #日程执行器 "calendar_executor":""
        #}

#日程表执行器（循环自动查询日程表并提交到任务库执行，自动查询任务结果）
class calendar_executor:
    pass