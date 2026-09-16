from hello_agentLLM import HelloAgentsLLM
from Executor import ToolExecutor
from tools import search
import re
from prompts import REACT_PROMPT_TEMPLATE

class ReActAgent:
    def __init__(self, llm_client:HelloAgentsLLM, tool_executor:ToolExecutor,max_steps:int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []  # 用于存储对话历史记录

    def run(self, question:str):
        """
        运行ReAct智能体,处理用户问题并返回最终答案。
        """
        self.history = []   #每次运行前清空历史记录
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1
            print(f"\n--- Step {current_step} ---")

            #格式化提示词
            tools_desc = self.tool_executor.getAvailableTools()     #获取所有已注册的工具及其描述
            history_str = "\n".join(self.history)                   #将历史记录列表转换为字符串

            prompt = REACT_PROMPT_TEMPLATE.format(
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

            #解析大模型的输出，提取thought和action
            thought, action = self._parse_output(response_text)
            if thought:
                print(f"Thought: {thought}")
            if not action:
                print("No action found in the LLM response. Stopping.")
                break

            #执行action
            if action.startswith("Finish["):
                #如果action是Finish，提取最终答案并返回
                final_answer = action[len("Finish["):-1]  #去掉  Finish[  和  ]
                print(f"Final Answer: {final_answer}")
                return final_answer

            tool_name, tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                print("Invalid action format. Skipping.")
                continue
            else:                     #不加else，如果没有调用工具，还要输出tool_name和tool_input，有安全隐患
                print(f"Executing tool: {tool_name} .The input: {tool_input}")

                tool_function = self.tool_executor.getTool(tool_name)
                if not tool_function:
                    observation = f"Tool {tool_name} not found."
                else:
                    observation = tool_function(tool_input)

                print(f"Observation: {observation}")


            #将thought、action和observation添加到历史记录中
            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")
        #循环结束
        print("Max steps reached without finding a final answer.")
        return None

    #_parse_output： 负责从LLM的完整响应中分离出Thought和Action两个主要部分。
    #_parse_action： 负责进一步解析Action字符串，例如从 Search[华为最新手机] 中提取出工具名 Search 和工具输入 华为最新手机。
    #输出解析器
    def _parse_output(self,text:str):
        """
        解析大模型的输出，提取thought和action
        """
        #thonght:匹配到Action：或文本末尾
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)",text,re.DOTALL)  #re.DOTALL让.这一元符号可以匹配换行符 ，(.*?)是非贪婪匹配，(?=\nAction:|$)是正向前瞻，表示匹配到Action:或文本末尾
        #Action:匹配到文本末尾
        action_match = re.search(r"Action:\s*(.*?)$",text,re.DOTALL)   

        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None

        return thought, action

    def _parse_action(self,action_text:str):
        """
        解析action字符串，提取工具名称和输入
        """
        match = re.match(r"(\w+)\[(.*)\]",action_text,re.DOTALL)
        if match:
            return match.group(1), match.group(2)  # 返回工具名称和输入
        return None, None  # 如果解析失败，返回None

if __name__ == "__main__":
    #测试ReActAgent
    llm_client = HelloAgentsLLM()
    tool_executor = ToolExecutor()
    tool_executor.registerTool("search","一个SerpApi的实战网页搜索引擎工具。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。",search)

    Sagent = ReActAgent(llm_client,tool_executor,max_steps=5)
    question = "华为最新款手机是？"
    final_answer = Sagent.run(question)
    print(f"\nFinal Answer: {final_answer}")