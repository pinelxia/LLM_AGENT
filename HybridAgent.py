from hello_agentLLM import HelloAgentsLLM
import prompts
from RAgent import ReActAgent
from PSAgent import PlanAndSolveAgent
from ReflectionAgent import ReflectionAgent

#定义分析器类，用于分析问题适用于分析当前问题应用哪个架构来解决
class Analysis:
    def __init__(self,llm_client = HelloAgentsLLM()):
        self.llm_client = llm_client

    def analysis(self,question :str)->str:
        prompt = prompts.ANALYSIS_PROMPT_TEMPLATE.format(question = question)
        messages = [{"role":"user","content":prompt}]
        response_text = self.llm_client.think(messages=messages)
        return response_text


class HybridAgent:
    def __init__(self,Agent_list:list,llm_client = HelloAgentsLLM()):
        self.llm_client = llm_client
        self.Agent_list = Agent_list


if __name__ == "__main__":
    PS_question = "一个水果店周一卖出了15个苹果。周二卖出的苹果数量是周一的两倍。周三卖出的数量比周二少了5个。请问这三天总共卖出了多少个苹果？"
    RA_question = "华为最新款手机是？"
    RF_question = "编写一个Python函数，找出1到n之间所有的素数 (prime numbers)。"
    analy = Analysis()
    print(analy.analysis(PS_question),analy.analysis(RA_question),analy.analysis(RF_question))