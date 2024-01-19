import os
import sys
import requests
import json
import yaml
import webbrowser


# 谷歌搜索函数
def google_search(search_words):
    #获取当前路径
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0])) 

    # 读取 YAML 配置文件
    try:
        config_path = os.path.join(script_dir, "config", "Extended_Configuration" ,"google_search.yaml")
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            # 访问具体配置项
            key = config['google_search']['key']
            cx = config['google_search']['cx']
        
        #检查一下配置是否为空
        if (key == None) or (cx == None):
            return ("谷歌搜索的配置文件内容为空，请填写配置信息")

    except :
        return ("无法正确读取谷歌搜索的配置文件，请重新检查并配置相关信息")


    #请求地址
    url = 'https://www.googleapis.com/customsearch/v1'
    #请求数据
    params = {
        'key': key,        #谷歌api
        'q': search_words,  #搜索关键词
        'cx': cx,        #搜索引擎 ID
        'num': 6  #搜索结果数
    }

    #发送请求
    response = requests.get(url, params=params)

    #处理为json数据
    data = response.json()

    # 保存为JSON文件
    save_path1 = os.path.join(script_dir, "cache", "search_results.json")
    with open(save_path1, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


    #提取json数据内容
    results = data['items']

    #提取搜索结果里的主要信息
    records = []
    for result in results:
        # 检查 'title'，'link'，'snippet' 是否存在，存在就添加到 record 中，有些搜索结果没有'snippet'
        record = {}
        if 'title' in result:
            record['title'] = result['title']
        if 'link' in result:
            record['link'] = result['link']
        if 'snippet' in result:
            record['snippet'] = result['snippet']

        # 只有在 record 不为空时才添加到 records 列表中
        if record:
            records.append(record)

    # 保存为JSON文件
    save_path2 = os.path.join(script_dir, "cache", "results.json")
    with open(save_path2, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=4)

    #返回搜索结果
    return records

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


#默认浏览器打开网站函数
def open_url(url):
    webbrowser.open(url)
    return "已打开指定网站" + url

#配套函数调用说明
function_open_url  = {
        "type": "function",
        "function": {
                    "name": "open_url",
                    "description": "输入网站，将自动调用系统默认浏览器打开该网站",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "网站链接",
                            }
                        },
                        "required": ["url"]
                    },
                }
}
