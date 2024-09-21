import re

qa_database = {
    "你好": "你好！很高兴见到你。",
    "今天天气如何": "抱歉，我是一个简单的问答系统，无法获取实时天气信息。不过，希望您今天心情愉快！",
    "你是谁": "我是一个基于规则的简单问答系统。我可以回答一些基本问题。",
    "你的名字是什么": "我是一个AI助手，没有具体的名字。你可以叫我小助手。",
    "你能做什么": "我可以回答一些简单的问题，比如介绍自己、问候等。如果你有其他问题，也可以问问看。",
    "再见": "再见！祝您有个愉快的一天。",
    "谢谢": "不用谢，我很高兴能帮到你。",
    "你好吗": "作为一个AI，我没有情感，但我随时准备为您服务。您今天感觉如何？",
    "现在几点了": "抱歉，作为一个简单的问答系统，我无法获取实时信息。您可以看看您的设备时间。"
}

def find_best_match(question):
    question = question.lower()
    best_match = None
    max_similarity = 0

    for key in qa_database.keys():
        similarity = sum(1 for a, b in zip(question, key.lower()) if a == b) / max(len(question), len(key))
        if similarity > max_similarity:
            max_similarity = similarity
            best_match = key

    return best_match if max_similarity > 0.5 else None

def generate_answer(question):
    best_match = find_best_match(question)
    if best_match:
        return qa_database[best_match]
    else:
        keywords = re.findall(r'\b\w+\b', question.lower())
        for key in qa_database.keys():
            if any(keyword in key.lower() for keyword in keywords):
                return qa_database[key]
    return "抱歉，我没有找到相关的答案。您可以尝试用不同的方式提问，或者问一些我知道的问题。"