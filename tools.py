from serpapi import SerpApiClient           #导入SerpApi客户端
import os                                       #导入操作系统模块，用于获取环境变量
from dotenv import load_dotenv

load_dotenv()      #H加载.env文件中的环境变量


def search(query:str)->str:                 #定义函数，返回搜索结果，输入query是字符串类型，输出也是字符串
    """
    一个SerpApi的实战网页搜索引擎工具。
    该工具会智能地解析搜索结果，优先返回直接答案或者知识图谱信息。
    """
    print(f"using SerpApi to search for:{query}")
    try:
        api_key = os.getenv('SERPAPI_API_KEY')      #从环境变量中获取SerpApi的API Key
        if not api_key:
            return "SerpApi API Key is not set in environment"

        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "gl":"cn",    #国家代码
            "hl":"zh-cn"     #语言代码
        }

        client = SerpApiClient(params)          #创建SerpApi客户端
        results = client.get_dict()             #获取搜索结果并转换为字典格式

        #智能解析：优先寻找最直接的答案
        if "answer_box_list" in results:
            return "\n".join(results["answer_box_list"])    #如果存在直接答案，返回这些答案
        if "answer_box" in results and "answer" in results["answer_box"]:
            return results["answer_box"]["answer"]          #如果存在知识图谱信息，返回这些信息
        if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            return results["knowledge_graph"]["description"]  #如果存在知识图谱描述，返回这些描述
        if "organic_results" in results and results["organic_results"]: 

            snippets =[
                f"[{i+1}]{res.get('title','')}\n{res.get('snippet','')}"for i,res in enumerate(results["organic_results"][:3])  #只取前三条有机搜索结果
            ]
            return "\n".join(snippets)  #返回前三条有机搜索结果的标题和摘要
        return "No relevant information found."  #如果没有找到相关信息，返回提示信息
    except Exception as e:
        return f"Error during search: {e}"  #如果在搜索过程中发生错误，返回错误信息