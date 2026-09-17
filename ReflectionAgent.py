from typing import List ,Dict ,Any ,Optional
from hello_agentLLM import HelloAgentsLLM
import prompts

class Memory:
    """
    一个简单的短时记忆模块，用于存储智能体的行动与反思轨迹
    """

    def __init__(self):
        """
        初始化一个空列表来存储所有的记录.
        """
        self.records:List[Dict[str,Any]] = []

    def add_record(self,record_type:str ,content:str):
        """
        向记忆中添加一条新纪录。

        参数：
        record_type(str):记录的类型（'execution' or 'reflection'）
        content(str): 记录的具体内容（例如，生成的代码或反思的反馈）
        """
        record ={"type":record_type,"content":content}

        self.records.append(record)
        print(f"记忆已更新，新增一条'{record_type}'记录。")

    def get_trajectory(self)->str:
        """
        将所有记忆记录格式化为一个连贯的字符串文本，用于构建提示词。
        """
        trajectory_parts = []
        for record in self.records:
            if record['type']=='execution':
                trajectory_parts.append(f"上一轮尝试(代码):\n{record['content']}")
            elif record['type']=='reflection':
                trajectory_parts.append(f"评审员反馈:\n{record['content']}")

        return "\n\n".join(trajectory_parts)   #把列表中的元素用\n\n连接起来返回一个新字符串

    def get_last_execution(self)->Optional[str]:
        """
        获取最近的一次执行结果（例如，最新生成的代码）。
        如果不存在，则返回None。
        """
        for record in reversed(self.records):
            if record['type']=='execution':
                return record['content']
        return None


class ReflectionAgent:
    def __init__(self,llm_client = HelloAgentsLLM(),max_iterations = 3):
        self.llm_client = llm_client
        self.memory = Memory()
        self.max_iterations = max_iterations
    def run(self,task:str):
        print(f'\n开始处理任务\n任务：{task}')

        #初始执行

        print("正在尝试初始执行")
        initial_prompt = prompts.INITIAL_PROMPT_TEMPLATE.format(task = task)
        initial_code = self._get_llm_response(initial_prompt)
        self.memory.add_record("execution",initial_code)


        #循环迭代：反思和优化
        for i in range(self.max_iterations):
            print(f"\n第{i+1}/{self.max_iterations}轮迭代")

            #反思
            print("\n正在反思。。。。。。")
            last_code = self.memory.get_last_execution()
            reflect_prompt = prompts.REFLECT_PROMPT_TEMPLATE.format(task = task , code = last_code)
            feedback = self._get_llm_response(reflect_prompt)
            self.memory.add_record("reflection",feedback)

            #检查是否需要停止
            if "无需改进" in feedback:
                print("\n反思认为代码无需改进，任务完成")
                break

            #优化
            print("\n正在优化改进.........")
            refine_prompt = prompts.REFINE_PROMPT_TEMPLATE.format(
                task = task,
                last_code_attempt = last_code ,
                feedback = feedback
            )
            refined_code = self._get_llm_response(refine_prompt)
            self.memory.add_record("execution",refined_code)
        final_code = self.memory.get_last_execution()
        print(f"\n任务结束\n最终生成代码：\n```pytion\n{final_code}\n```")
        return final_code

    def _get_llm_response(self,prompt:str)->str:
        """一个辅助防范，用于调用LLM并获取完整的流式响应。"""
        messages =[{"role":"user","content":prompt}]
        response_text = self.llm_client.think(messages=messages) or ""
        return response_text

if __name__ == "__main__":
    rfAgnet = ReflectionAgent(llm_client=HelloAgentsLLM())
    task = "编写一个Python函数，找出1到n之间所有的素数 (prime numbers)。"
    rfAgnet.run(task=task)