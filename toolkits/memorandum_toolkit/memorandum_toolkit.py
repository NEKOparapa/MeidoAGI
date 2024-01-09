import json
import os
import sys


# 如果被调用，则获取到的是demo.py的当前路径，而不是这个脚本的
script_dir = os.path.dirname(os.path.abspath(sys.argv[0])) 
data_path = os.path.join(script_dir, "memo", "memo_database.json")



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



# 写入备忘录函数
def write_memorandum (text):
    #在文件夹下寻找json文件，如果存在则读取json文件
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []
    
    data.append(text)

    #写入json文件到指定文件夹中
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return f"已成功将“{text}”写入备忘录！"



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


# 查询备忘录函数
def query_memorandum (text):
    #在文件夹下寻找json文件，如果存在则读取json文件
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        return "备忘录中尚未录入任何信息，无法查询"
    
    #查询相关文本
    result_texts = find_top_matching_texts(data, text, top_n=3)    

    #整理文本
    if result_texts:
        #print("匹配字符数量从多到少的前三个结果：")
        result = "已查询到备忘录相关的内容为："+"\n"
        for text, match_count in result_texts:
            #print(f"文本 '{text}' 匹配字符数量为 {match_count}")
            result = result + text +"\n"
        
        return result
    else:
        return "未能从备忘录中找到匹配的内容"  


# 简单的字符匹配算法
def find_top_matching_texts(dictionary, input_text, top_n=3):
    """
    在字典中寻找与输入文本匹配字符数量最多的前 top_n 个文本。
    """
    matches = []

    for text in dictionary:
        common_chars = set(input_text) & set(text)
        match_count = len(common_chars)
        matches.append((text, match_count))

    # 根据匹配字符数量从多到少重新排序
    sorted_matches = sorted(matches, key=lambda x: x[1], reverse=True)

    # 输出前 top_n 个结果
    top_n_matches = sorted_matches[:top_n]

    return top_n_matches