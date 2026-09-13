from hello_agentLLM import HelloAgentsLLM
from Executor import ToolExecutor
from tools import search

class ReActAgent:
    def __init__(self, llm_client:HelloAgentsLLM, tool_executor:ToolExecutor,max_steps:int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []  # 用于存储对话历史记录

    def run(self, question:str):
        """
        运行ReAct智能体，处理用户问题并返回最终答案。
        """
        self.history = []   #每次运行前清空历史记录
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1
            print(f"\n--- Step {current_step} ---")

            #格式化提示词
            tools_desc = self.tool_executor.getAvailableTools()     #获取所有已注册的工具及其描述
            history_str = "\n".join(self.history)                   #将历史记录列表转换为字符串

            prompt = REACT_PROMPT.format(
                tools=tools_desc,                #工具列表
                history=history_str,            #历史记录
                question=question               #用户问题
            )


            #调用大模型进行思考
            messages = [{"role":"user","content":prompt}]
            response_text = self.llm_client.think(messages = messages)

            if not response_text:
                print("error: LLM did not return a response.")
                break

    #输出解析器
    def _parse_output(self,text:str):
        """
        解析大模型的输出，提取thought和action
        """
        #thonght:匹配到Action：或文本末尾
        thought = ""