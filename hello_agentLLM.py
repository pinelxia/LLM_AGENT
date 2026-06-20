import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict


#加载.env环境
load_dotenv()


class HelloAgentsLLM:
    """
    作为hello agents的定制llm客户端
    用于调用任何兼容OpenAI接口的服务，并默认使用流式响应
    """
    def __init__(self,model : str = None ,apiKey : str = None , baseUrl : str = None ,timeout : int = None):
        """
        初始化客户端。优先使用传入参数，如果未提供，则从环境变量加载
        """
        self.model = model or os.getenv('LLM_MODEL_ID')
        apiKey = apiKey or os.getenv('LLM_API_KEY')
        baseUrl = baseUrl or os.getenv('LLM_BASE_URL')
        timeout = timeout or int(os.getenv('LLM_TIMEOUT', 60))

        if not all([self.model, apiKey, baseUrl]):
            raise ValueError("模型ID、API Key和Base URL必须提供。")
        
        self.client = OpenAI(api_key=apiKey, base_url=baseUrl, timeout=timeout)

    def think(self, messages : List[Dict[str ,str]],temperature : float = 0.1 ) -> str:
        """
        调用模型进行思考，返回最终的文本结果
        """
        print(f"调用模型 {self.model} 进行思考，温度: {temperature}")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream= True
            )

            print("大模型响应：")
            collected_content = []
            for chunk in response:
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content or ''
                print(content,end='',flush=True)
                collected_content.append(content)
            print("\n")
            return ''.join(collected_content)
        
        except Exception as e:
            print(f"调用模型时发生错误: {e}")
            return None

if __name__ == "__main__":
    try:
        llmClient = HelloAgentsLLM()

        exampleMesages = [
            {"role": "system", "content": "你是一个专业的算法工程师，擅长使用Python进行算法设计和实现。"},
            {"role": "user", "content": "写一个快速排序算法"}
        ]

        print("调用LLM")
        responseText = llmClient.think(messages=exampleMesages, temperature=0.3)
        if responseText:
            print("最终响应文本：")
            print(responseText)
    except ValueError as e:
        print(e)