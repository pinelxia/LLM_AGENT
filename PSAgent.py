#规划阶段：首先，将问题分解为三个独立的计算步骤（计算周二销量、计算周三销量、计算总销量）。
#执行阶段：然后，严格按照计划，一步步执行计算，并将每一步的结果作为下一步的输入，最终得出总和。
from hello_agentLLM import HelloAgentsLLM
from prompts import PLANNER_PROMPT_TEMPLATE
import ast
from prompts import EXECUTOR_PROMPT_TEMPLATE

class Planner:
    def __init__(self,llm_client):
        self.llm_client = llm_client

    def plan(self, question: str):
        """
        根据用户问题生成一个行动计划
        """
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)

        #为了生成计划，构建一个消息列表
        messages = [{"role": "user", "content": prompt}]

        print("正在生成计划......")
        #使用流式输出来获取完整的计划
        response_text = self.llm_client.think(messages=messages) or ""   #防止出现None的情况
        print(f"计划生成完成，输出为：\n{response_text}")

        #解析LLM输出的列表字符串
        try:
            #找到```python和```之间的内容
            plan_str = response_text.split("```python")[1].split("```")[0].strip()
            #使用ast.literal_eval安全地执行字符串，将其转换为Python列表
            plan = ast.literal_eval(plan_str)
            return plan if isinstance(plan, list) else [] # 如果转换失败，返回空列表
        except (IndexError, ValueError, SyntaxError) as e:
            print(f"解析计划时出错：{e}")
            print(f"原始相应文本：{response_text}")
            return [] # 如果解析失败，返回空列表
        except Exception as e:
            print(f"生成计划时发生错误：{e}")
            return [] # 如果生成计划失败，返回空列表

#PSAgent的执行器
class PSExecutor:
    def __init__(self,llm_client):
        self.llm_client = llm_client
        self.history =[]

    def execute(self,question: str ,plan: list[str])->str:
        """
        按照计划逐步执行并解决问题
        """
        self.history = []  # 用于存储每一步的历史记录  

        print("\n正在执行计划")

        for i , step in enumerate(plan):
            print(f"\n----正在执行步骤{i}/{len(plan)}:{step}")

            prompt = EXECUTOR_PROMPT_TEMPLATE.format(
                question = question,
                plan = plan,
                history = self.history if self.history else "无"  ,  #第一步的历史记录为空
                current_step=step
            )

            messages = [{ "role" : "user","content" : prompt }]

            response_text = self.llm_client.think(messages=messages) or ""

            #更新历史记录

            self.history += f"步骤{i+1}:{step}\n结果：{response_text}\n"

            print(f"步骤{i+1}完成，结果：{response_text}")

        #循环结束之后，最后一步的响应就是最终答案
        final_answer = response_text
        return final_answer


class PlanAndSolveAgent:
    def __init__(self,llm_client):
        """
        初始化智能体，同时创建规划器和执行器实例
        """
        self.llm_client = llm_client
        self.planner = Planner(self.llm_client)
        self.executor = PSExecutor(self.llm_client)
    def run(self,question:str):
        """
        运行智能体完整流程：先规划，后执行
        """
        print(f"\n---开始处理问题---\n问题：{question}")

        #1.调用规划器生成计划
        plan = self.planner.plan(question)

        #检查计划是否生成
        if not plan:
            print("\n---任务终止---\n无法生成计划")
            return
        final_answer = self.executor.execute(question,plan)

        print(f"\n任务完成，最终答案:{final_answer}")

            
if __name__ == "__main__":
    question = "一个水果店周一卖出了15个苹果。周二卖出的苹果数量是周一的两倍。周三卖出的数量比周二少了5个。请问这三天总共卖出了多少个苹果？"
    psAgent = PlanAndSolveAgent(HelloAgentsLLM())   #传入的需要是一个实例而不是一个类，要加()的
    psAgent.run(question)