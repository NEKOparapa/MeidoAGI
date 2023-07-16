import json


#功能1：获取给定位置的当前天气--------------------------------------------
def get_current_weather(location, unit):
    """Get the current weather in a given location"""
    weather_info = {
        "location": location,
        "temperature": "31",
        "unit": unit,
        "forecast": "晴天",
    }
    return json.dumps(weather_info)

#定义AI调用函数的信息，包括函数名字，描述，参数，参数类型，参数范围，参数描述，必需给出的参数
function_get_current_weather = {
            "name": "get_current_weather", #函数名字
            "description": "输入位置与温度单位，获取给定位置的当前天气", #函数描述

            "parameters": { "type": "object", # 暂时不知道干嘛，都有先带着
                            "properties": {"location": {"type": "string",
                                                        "description": "需要查询的城市，例如南宁、北京", #参数描述
                                                        },
                                            "unit": {"type": "string",  #参数类型
                                                    "enum": ["摄氏度", "华氏度"], #参数范围
                                                    "description": "使用的温度单位，从用户位置推断出来。" #参数描述
                                                    },
                                            },
                            "required": ["location","unit"], #必需给出的参数
                            },
                }


#功能2：获取N天的天气预报--------------------------------------------
def get_n_day_weather_forecast(location, unit, num_days):
    """Get an N-day weather forecast"""
    weather_info = {
        "location": location,
        "temperature": "28",
        "unit": unit,
        "num_days": num_days,
        "forecast": "持续雨天",
    }
    return json.dumps(weather_info)



function_get_n_day_weather_forecast  = {
        "name": "get_n_day_weather_forecast",
        "description": "输入位置、温度单位和天数，获取该位置未来N天的天气预报",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "需要查询的城市，例如南宁、北京",
                },
                "unit": {
                    "type": "string",
                    "enum": ["摄氏度", "华氏度"],
                    "description": "使用的温度单位，从用户位置推断出来。",
                },
                "num_days": {
                    "type": "integer",
                    "description": "需要预报的天数",
                }
            },
            "required": ["location", "unit", "num_days"]
        },
    }


