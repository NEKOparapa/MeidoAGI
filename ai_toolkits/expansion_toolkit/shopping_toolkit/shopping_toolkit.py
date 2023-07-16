import json



#功能1：获取单个物品的价格--------------------------------------------
def get_the_price_of_the_item(item,unit):
    price_info = {
        "item": item,
        "price": "12",
        "unit": unit
    }
    return json.dumps(price_info)



function_get_the_price_of_the_item  = {
        "name": "get_the_price_of_the_item",
        "description": "输入物品名词，金额单位，获取物品的单个价格",
        "parameters": {
            "type": "object",
            "properties": {
                "item": {
                    "type": "string",
                    "description": "需要查询的物品，例如苹果、香蕉",
                },
                "unit": {
                    "type": "string",
                    "enum": ["人民币", "美元"],
                    "description": "使用的金额单位，根据用户要求或者从用户语言推断出来。",
                }
            },
            "required": ["item", "unit"]
        },
    }

