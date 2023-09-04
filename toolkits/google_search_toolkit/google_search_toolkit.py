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
        config_path = os.path.join(script_dir, "data", "Extended_Configuration" ,"google_search.yaml")
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
    with open('search_results.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


    #提取json数据内容
    results = data['items']

    #提取搜索结果里的主要信息
    records = []
    for result in results:
        record = {
            'title': result['title'],
            'link': result['link'],  
            'snippet': result['snippet']
        }
        
        records.append(record)

    # 保存为JSON文件
    with open('results.json', 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=4)

    #返回搜索结果
    return records

#配套函数调用说明
function_google_search  = {
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


#系统打开网站函数
def open_website(website_url):
    webbrowser.open(website_url)
    return "已打开指定网站" + website_url

#配套函数调用说明
function_open_website  = {
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
