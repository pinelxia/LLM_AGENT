from Executor import ToolExecutor
from tools import search


#创建工具执行器实例
tool_executor = ToolExecutor()  


#注册搜索工具
search_tool_name = "search"
search_tool_description = "一个SerpApi的实战网页搜索引擎工具。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
tool_executor.registerTool(search_tool_name, search_tool_description, search)


#打印可用的工具
print("可用的工具:")
print(tool_executor.getAvailableTools())

#智能体的action调用，测试一个实时性较强的问题

print("\n--------执行Action： Search['今天的日期是？']--------")

tool_name ="search"

tool_input = "今天的日期是？"

tool_function = tool_executor.getTool(tool_name)

if tool_function:
    observation = tool_function(tool_input)
    print("Observation")
    print(observation)
else:
    print(f'error: tool {tool_name} not found')
