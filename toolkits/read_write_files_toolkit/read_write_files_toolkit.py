import os

#写为txt文件函数
def write_text_to_file(folder_path, text_content):
    # 创建文件夹路径（如果不存在）
    os.makedirs(folder_path, exist_ok=True)

    # 构造完整的文件路径
    file_path = os.path.join(folder_path, 'output.txt')

    # 将文本内容写入文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text_content)

    print(f'文件已成功写入：{file_path}')


#配套函数调用说明
function_write_text_to_file  = {
        "type": "function",
        "function": {
                    "name": "write_text_to_file",
                    "description": "将文本内容写为txt文件保存",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "folder_path": {
                                "type": "string",
                                "description": "存储的文件夹路径,例如：D:/MeidoAGI/folder",
                            },
                            "text_content": {
                                "type": "string",
                                "description": "文本内容",
                            }
                        },
                        "required": ["folder_path","text_content"]
                    },
                }
}

