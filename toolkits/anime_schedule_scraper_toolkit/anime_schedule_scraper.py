import json
import os
import sys
import requests
from bs4 import BeautifulSoup   #需要安装依赖库
from datetime import datetime

#获取当前季度的动漫更新信息函数
def anime_schedule_scraper(switch):

    # 解析首页
    url = 'https://yuc.wiki/'
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    # 获取所有链接项
    link_items = soup.find_all('li', class_='links-of-blogroll-item')

    # 获取第四个元素，因为网站把它排在第5项
    fourth_link_item = link_items[3]

    # 提取当季列表的后半链接
    if fourth_link_item:
        link = fourth_link_item.find('a')['href']
        #print("当前动漫更新季度：", link)

    # 与首页组合链接，为当季动画更新列表链接
    url = url + link
    #print("当季动画列表链接：", url)



    # 解析季动画更新列表链接
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    # 获取所有更新日期的table
    date_tables = soup.find_all('table', class_='date_')

    # 创建一个空字典，用于存储日期和对应的动漫列表
    anime_schedule = {}

    # 遍历每一个日期，统计记录当天的更新内容
    for date_table in date_tables: 
        date = date_table.find('td', class_='date2').text.strip() # 提取当前的更新日期标题
        #print("更新日期：", date)
        
        next_table = date_table.find_next('table')  # 当前元素的同一级别中查找下一个table标签 

        # 找到table标签且标签内不含'date2'类时继续循环
        while next_table and not next_table.find('td', class_='date2'):
            anime_name_tag = next_table.find('td', class_='date_title_') or next_table.find('td', class_='date_title') or next_table.find('td', class_='date_title__')
            anime_name = anime_name_tag.text.strip()
            #print(anime_name)

            # 将动漫名称添加到对应日期的列表中，如果日期还没有对应的列表，则创建一个新的列表
            if date in anime_schedule:
                anime_schedule[date].append(anime_name)
            else:
                anime_schedule[date] = [anime_name]

            next_table = next_table.find_next('table')   

        #print("当前日期获取结束",'\n')

    #获取系统日期，计算当天星期几
    current_weekday = datetime.now().strftime("%A")
    #提取当天更新的动漫信息
    anime_list = {} 
    if current_weekday == "Monday":
        anime_list = {"星期一": anime_schedule["周一 (月)"]}
    elif current_weekday == "Tuesday":
        anime_list = {"星期二": anime_schedule["周二 (火)"]}
    elif current_weekday == "Wednesday":
        anime_list = {"星期三": anime_schedule["周三 (水)"]}
    elif current_weekday == "Thursday":
        anime_list = {"星期四": anime_schedule["周四 (木)"]}
    elif current_weekday == "Friday":
        anime_list = {"星期五": anime_schedule["周五 (金)"]}
    elif current_weekday == "Saturday":
        anime_list = {"星期六": anime_schedule["周六 (土)"]}
    elif current_weekday == "Sunday":
        anime_list = {"星期日": anime_schedule["周日 (日)"]}
    print(anime_list)
    # 打印整个动漫更新日程
    #print(anime_schedule)


    #获取当前路径
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0])) 
    # 保存为JSON文件
    save_path2 = os.path.join(script_dir, "cache", "anime_schedule.json")
    with open(save_path2, 'w', encoding='utf-8') as f:
        json.dump(anime_list, f, ensure_ascii=False, indent=4)
    
    return anime_list



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


#调试用
#anime_schedule_scraper("on")