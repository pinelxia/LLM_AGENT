from typing import TypedDict,List
from hello_agentLLM import HelloAgentsLLM
import os
from dotenv import load_dotenv
load_dotenv()
import langchain_openai
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


llm = langchain_openai.ChatOpenAI(
    model = os.getenv("LLM_MODEL_ID"),
    api_key= os.getenv("LLM_API_KEY"),
    base_url= os.getenv("LLM_BASE_URL"),
    temperature= 0.1
)

#定义全局状态的数据结构
class AgentState(TypedDict):
    messages: List[str]             #对话记录
    current_task: str               #当前任务
    final_answer: str               #最终答案
    #任何其他想要追踪的全局状态



#定义一个规划者节点函数，节点起作用的方式就是更新全局状态

def planner_node(state:AgentState)->AgentState:
    """
    根据当前任务制定计划，并更新状态
    """
    current_task = state['current_task']

    #调用llm生成计划
    plan = f"为任务'{current_task}'生成计划，输出严格按照: plan```计划的内容```"
    response = llm.invoke([SystemMessage(content=plan)])
    response_text = response.content

    #将新消息追加到状态
    state["messages"].append(response_text)
    return state

def executor_node(state:AgentState)->AgentState:
    """
    执行最新计划，并更新状态
    """
    latest_plan = state["messages"][-1]

    #执行计划并获得结果
    result = f"执行计划'{latest_plan}'的结果是："
    response = llm.invoke([SystemMessage(content=result)])
    response_text = response.content

    state["messages"].append(response_text)
    return state

def should_continue(state:AgentState)->str:
    """条件函数：根据状态决定下一步路由。"""
    if len(state["messages"]) < 3:
        return "continue_to_planner"
    else:
        state["final_answer"] = state["messages"][-1]
        return "end_workflow"


from langgraph.graph import StateGraph , END

#初始化一个状态图，并绑定定义的状态结构
workflow = StateGraph(AgentState)

#将级欸但函数添加到图中
workflow.add_node("planner",planner_node)
workflow.add_node("executor",executor_node)

#设置图的入口点
workflow.set_entry_point("planner")


# 添加常规边，连接planner 和 executor
workflow.add_edge("planner","executor")

#添加边条件
workflow.add_conditional_edges(
    #起始节点
    "executor",
    #判断函数
    should_continue,
    #路由映射：将判断函数的返回值映射到目标节点
    {
        "continue_to_planner":"planner" ,     #如果返回"continue_to_planner"，则跳挥planner节点
        "end_workflow":END
    }
)
#编译图，生成可执行的应用
app = workflow.compile()

#运行图
inputs = {"current_task":"今天的日期是？","messages":[]}
for event in app.stream(inputs):
    print(event)