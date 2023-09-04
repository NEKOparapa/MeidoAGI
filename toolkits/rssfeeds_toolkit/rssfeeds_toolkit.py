import datetime
import feedparser#需要安装feedparser库



#获取动漫Rss订阅消息函数
def get_anime_rssfeed():
    url = 'https://mikanime.tv/RSS/Classic'


    #获取RSS源内容
    feed = feedparser.parse(url)
    #print("[DEBUG] 该RSS源标题。",feed['feed']['title'],'\n')

    #获取解析后的全部项目内容
    entrys = feed["entries"]

    #只获取其中每个项目的部分内容，并组成新的列表
    feed_list = [] # 初始化feed列表
    today = datetime.date.today() #获取今天的日期
    for entry in entrys:
        #获取标题
        title = entry["title"]
        #获取发布时间
        published = entry["published"]
        #获取下载链接
        download = entry["links"][2]["href"]

        #只获取今天发布的内容
        if published.find(str(today)) != -1:
            #如果标题字符串没有带“720p”，“繁中”，“繁体”，“繁日”字样
            if title.find("720P") == -1 and title.find("繁中") == -1 and title.find("繁体") == -1 and title.find("繁日") == -1:
                    #组成新的字典
                    feed_dict = {"title":title,"download":download}

                    #截取动漫名称前N个字符，检查列表中每个元素的动漫名称前N个字符是否与当前动漫名称前N个字符相同，如果相同则不添加到列表中，如果不相同则添加到列表中
                    if len(feed_list) == 0:
                        feed_list.append(feed_dict)
                    else:
                        mark = 0
                        for feed in feed_list:
                            if feed["title"][:7] == feed_dict["title"][:7]:
                                #print("[DEBUG] 新信息的动漫名",feed["title"][:7])
                                #print("[DEBUG] 旧信息的动漫名",feed_dict["title"][:7])
                                #print("[DEBUG] 该动漫名称已存在，不添加到列表中。","\n")
                                mark = 1
                                break
                        #如果动漫名称不在列表中，则添加到列表中
                        if mark == 0:
                            feed_list.append(feed_dict)
    #返回动漫Rss订阅消息列表
    return feed_list

#配套函数调用说明
function_get_anime_rssfeed  = {
        "name": "get_anime_rssfeed",
        "description": "获取今日动漫更新的RSS订阅消息列表",
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