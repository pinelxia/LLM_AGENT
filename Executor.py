from typing import Dict , Any

class ToolExecutor:
    """
    工具执行器，用于管理和执行各类工具。
    """
    def __init__(self):
        self.tools : Dict[str, Dict[str, Any]] = {}  #tools字典的键是工具名name，值是一个字典，该字典里包含了description和func两个键，分别对应工具的描述和工具的执行函数

    def registerTool(self, name : str , description : str , func : callable):
        """
        注册一个工具。
        :param name: 工具名称
        :param description: 工具描述
        :param func: 工具描述
        """
        if name in self.tools:
            print(f"Warning: Tool '{name}' is already registered. Overwriting.")
        self.tools[name] = {
            "description": description,
            "func": func
        }
        print(f"Tool '{name}' registered successfully.")
    def getTool(self, name : str):
        """
        获取已注册的工具。
        """
        return self.tools.get(name, {}).get("func")

    def getAvailableTools(self):
        """
        获取所有已注册的工具及其描述。
        """
        return "\n".join([
            f"-{name}:{info['description']}"for name , info in self.tools.items()       #把tool字典转化为items，info是一个字典，info['description']是工具的描述
        ])
    