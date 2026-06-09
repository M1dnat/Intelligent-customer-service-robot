# # customer_service_bot.py
# """
# 实战项目：智能客服机器人（LangChain 1.0）

# 功能说明：
# - 用户信息管理：存储和查询客户基本信息
# - 订单查询：查询用户的订单列表和单个订单状态
# - 问题记录：创建客服工单，记录用户问题和解决方案
# - 跨会话记忆：保存对话历史，用户再次访问时可以继续之前的对话
# - 对话历史导出：支持导出完整的对话记录为文本格式
# """

# import os
# import json
# from dotenv import load_dotenv
# from langchain.chat_models import init_chat_model
# from langchain.agents import create_agent
# from langchain_core.tools import tool
# from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
# from datetime import datetime
# from typing import Optional

# load_dotenv()

# # 获取 API_KEY
# API_KEY = os.getenv("API_KEY")

# # ==================== 数据管理类 ====================

# class CustomerDatabase:
#     """客户数据库（模拟真实数据库）"""
    
#     def __init__(self):
#         # 客户信息表
#         self.customers = {
#             "user001": {
#                 "name": "张三",
#                 "level": "VIP",
#                 "phone": "138****1234",
#                 "email": "zhangsan@example.com"
#             },
#             "user002": {
#                 "name": "李四",
#                 "level": "普通会员",
#                 "phone": "139****5678",
#                 "email": "lisi@example.com"
#             }
#         }
        
#         # 订单表
#         self.orders = {
#             "user001": [
#                 {"order_id": "ORD001", "product": "iPhone 15", "status": "已发货", "date": "2024-01-01"},
#                 {"order_id": "ORD002", "product": "AirPods Pro", "status": "已送达", "date": "2024-01-02"},
#                 {"order_id": "ORD003", "product": "MacBook Pro", "status": "已发货", "date": "2024-01-03"},
#             ],
#             "user002": [
#                 {"order_id": "ORD004", "product": "iPad Air", "status": "已送达", "date": "2024-01-05"},
#                 {"order_id": "ORD005", "product": "Apple Watch", "status": "处理中", "date": "2024-01-06"},
#             ]
#         }
    
#     def get_customer(self, user_id: str) -> Optional[dict]:
#         """获取客户信息"""
#         return self.customers.get(user_id)
    
#     def get_orders(self, user_id: str) -> list:
#         """获取客户订单"""
#         return self.orders.get(user_id, [])


# class ConversationStorage:
#     """对话存储管理类"""
    
#     def __init__(self, storage_file: str = "customer_service_history.json"):
#         self.storage_file = storage_file
    
#     def save(self, user_id: str, session_id: str, messages: list, metadata: dict = None):
#         """保存对话记录"""
#         data = self._load()
        
#         if user_id not in data:
#             data[user_id] = {}
        
#         # 序列化消息
#         serialized = []
#         for msg in messages:
#             serialized.append({
#                 "type": msg.type,
#                 "content": msg.content,
#                 "timestamp": datetime.now().isoformat()
#             })
        
#         data[user_id][session_id] = {
#             "messages": serialized,
#             "metadata": metadata or {},
#             "created_at": datetime.now().isoformat()
#         }
        
#         self._save(data)
    
#     def load(self, user_id: str, session_id: str) -> list:
#         """加载指定的对话记录"""
#         data = self._load()
        
#         if user_id not in data or session_id not in data[user_id]:
#             return []
        
#         messages = []
#         for msg_data in data[user_id][session_id]["messages"]:
#             if msg_data["type"] == "human":
#                 messages.append(HumanMessage(content=msg_data["content"]))
#             elif msg_data["type"] == "ai":
#                 messages.append(AIMessage(content=msg_data["content"]))
#             elif msg_data["type"] == "system":
#                 messages.append(SystemMessage(content=msg_data["content"]))
        
#         return messages
    
#     def list_sessions(self, user_id: str) -> list:
#         """列出用户的所有会话ID"""
#         data = self._load()
#         if user_id not in data:
#             return []
#         return list(data[user_id].keys())
    
#     def get_session_history(self, user_id: str, session_id: str) -> list:
#         """获取格式化后的会话历史记录"""
#         data = self._load()
#         if user_id not in data or session_id not in data[user_id]:
#             return []
        
#         session_data = data[user_id][session_id]
#         history = []
#         for msg in session_data["messages"]:
#             history.append({
#                 "role": "用户" if msg["type"] == "human" else "客服",
#                 "content": msg["content"],
#                 "time": msg["timestamp"]
#             })
#         return history
    
#     def export_conversation(self, user_id: str, session_id: str) -> str:
#         """导出对话记录为文本格式"""
#         history = self.get_session_history(user_id, session_id)
#         if not history:
#             return "无对话记录"
        
#         export_text = f"对话导出 - 用户: {user_id}, 会话: {session_id}\n"
#         export_text += "=" * 50 + "\n"
        
#         for msg in history:
#             export_text += f"[{msg['time']}] {msg['role']}: {msg['content']}\n"
#             export_text += "-" * 30 + "\n"
        
#         return export_text
    
#     def _load(self) -> dict:
#         """从JSON文件加载数据"""
#         if not os.path.exists(self.storage_file):
#             return {}
#         try:
#             with open(self.storage_file, 'r', encoding='utf-8') as f:
#                 return json.load(f)
#         except:
#             return {}
    
#     def _save(self, data: dict):
#         """保存数据到JSON文件"""
#         try:
#             with open(self.storage_file, 'w', encoding='utf-8') as f:
#                 json.dump(data, f, ensure_ascii=False, indent=2)
#         except Exception as e:
#             print(f"保存失败: {e}")


# # ==================== 工具函数定义 ====================

# db = CustomerDatabase()


# @tool
# def get_customer_info(user_id: str) -> str:
#     """获取客户信息

#     Args:
#         user_id: 客户ID, 如 user001, user002
#     """
#     customer = db.get_customer(user_id)
#     if not customer:
#         return f"未找到客户 {user_id} 的信息"

#     return f"""客户信息:
# 姓名: {customer['name']}
# 会员等级: {customer['level']}
# 电话: {customer['phone']}
# 邮箱: {customer['email']}"""


# @tool
# def query_orders(user_id: str) -> str:
#     """查询客户订单

#     Args:
#         user_id: 客户ID
#     """
#     orders = db.get_orders(user_id)
#     if not orders:
#         return f"客户 {user_id} 暂无订单记录"

#     result = f"客户 {user_id} 的订单记录: \n\n"
#     for order in orders:
#         result += f"订单号: {order['order_id']}\n"
#         result += f"商品: {order['product']}\n"
#         result += f"状态: {order['status']}\n"
#         result += f"下单时间: {order['date']}\n"
#         result += "-" * 40 + "\n"
    
#     return result


# @tool
# def get_order_status(order_id: str) -> str:
#     """查询订单状态

#     Args:
#         order_id: 订单号，如 ORD001
#     """
#     for user_id, orders in db.orders.items():
#         for order in orders:
#             if order['order_id'] == order_id:
#                 return f"""订单 {order_id} 状态:
# 商品: {order['product']}
# 状态: {order['status']}
# 下单时间: {order['date']}
# {'预计明天送达' if order['status'] == '已发货' else ''}"""

#     return f"未找到订单 {order_id}"


# @tool
# def create_ticket(user_id: str, problem: str) -> str:
#     """创建客服工单

#     当客户问题无法立即解决时，创建工单记录

#     Args:
#         user_id: 客户ID
#         problem: 问题描述
#     """
#     ticket_id = f"TICKET_{datetime.now().strftime('%Y%m%d%H%M%S')}"

#     return f"""已为您创建工单:
# 工单号: {ticket_id}
# 问题: {problem}
# 状态: 待处理

# 我们的工作人员会在 24 小时内联系您。感谢您的耐心等待！"""


# @tool
# def search_knowledge_base(keyword: str) -> str:
#     """搜索知识库

#     Args:
#         keyword: 搜索关键词
#     """
#     knowledge = {
#         "退货": "退货政策:\n1. 7天无理由退货\n2. 商品需保持完好\n3. 提供订单号和退货原因\n4. 联系客服办理",
#         "发票": "发票申请:\n1. 登录账户\n2. 进入订单详情\n3. 点击【申请发票】\n4. 填写发票信息",
#         "配送": "配送说明:\n1. 全国包邮（偏远地区除外）\n2. 一般3-5个工作日送达\n3. 可选择上门自提",
#         "支付": "支付方式:\n1. 微信支付\n2. 支付宝\n3. 银行卡\n4. 货到付款（部分地区）",
#         "售后": "售后服务:\n1. 7天无理由退换货\n2. 1年质保\n3. 全国联保\n4. 24小时客服热线"
#     }

#     for key, value in knowledge.items():
#         if keyword in key or key in keyword:
#             return value

#     return f"未找到关于'{keyword}'的相关信息，请联系人工客服"


# # ==================== 客服机器人核心类 ====================

# class CustomerServiceBot:
#     """智能客服机器人"""

#     def __init__(self):
#         print("正在初始化客服机器人...")
        
#         # 初始化模型
#         self.model = init_chat_model(
#             "Qwen/Qwen3-8B",
#             model_provider='openai',
#             base_url='https://api.siliconflow.cn/v1',
#             api_key=API_KEY,
#             temperature=0
#         )

#         # 工具列表
#         self.tools = [
#             get_customer_info,
#             query_orders,
#             get_order_status,
#             create_ticket,
#             search_knowledge_base
#         ]

#         # 系统提示词
#         system_prompt = """你是一个专业的客服助手。

# 你的职责：
# 1. 礼貌、友好地回答客户问题
# 2. 使用工具查询订单、客户信息
# 3. 解答常见问题（退货、发票、配送等）
# 4. 无法解决时创建工单

# 工作流程：
# 1. 首先确认客户身份（询问客户ID或订单号）
# 2. 了解客户问题
# 3. 使用合适的工具查询信息或解决问题
# 4. 用通俗易懂的语言回复客户
# 5. 如果无法解决，创建工单

# 注意事项：
# - 始终保持专业和礼貌
# - 回答要准确，不要编造信息
# - 如果不确定，建议联系人工客服
# - 记住对话历史中的客户信息

# 请始终使用中文。"""

#         # 创建 agent
#         self.agent = create_agent(
#             model=self.model,
#             tools=self.tools,
#             system_prompt=system_prompt
#         )

#         # 存储
#         self.storage = ConversationStorage()

#         # 当前会话
#         self.current_user = None
#         self.current_session = None
#         self.messages = []
        
#         print("✅ 客服机器人初始化完成！\n")

#     def start_session(self, user_id: str, session_id: str = None):
#         """开始会话"""
#         self.current_user = user_id
#         self.current_session = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

#         # 加载历史对话
#         self.messages = self.storage.load(user_id, self.current_session)

#         if not self.messages:
#             # 新会话，添加欢迎消息
#             welcome = f"您好！我是智能客服助手。请问有什么可以帮您？\n\n提示：告诉我您的客户ID（如 user001 或 user002）"
#             self.messages.append(AIMessage(content=welcome))
#             self.storage.save(self.current_user, self.current_session, self.messages)

#     def chat(self, user_input: str) -> str:
#         """对话"""
#         # 添加用户消息
#         self.messages.append(HumanMessage(content=user_input))

#         # 调用 agent
#         try:
#             print("🤔 AI正在思考中...")
#             result = self.agent.invoke({"messages": self.messages})
#             self.messages = result["messages"]
#         except Exception as e:
#             error_msg = f"抱歉，处理您的请求时出现了错误：{str(e)}"
#             self.messages.append(AIMessage(content=error_msg))
#             return error_msg

#         # 自动保存
#         self.storage.save(self.current_user, self.current_session, self.messages)

#         # 返回 AI 回复
#         for msg in reversed(self.messages):
#             if msg.type == "ai" and msg.content:
#                 return msg.content

#         return "抱歉，我暂时无法处理您的请求。"

#     def end_session(self):
#         """结束会话"""
#         self.storage.save(
#             self.current_user,
#             self.current_session,
#             self.messages,
#             metadata={"ended_at": datetime.now().isoformat()}
#         )
    
#     def show_history(self):
#         """显示当前会话历史"""
#         if not self.messages:
#             print("暂无对话记录")
#             return
        
#         print("\n" + "=" * 70)
#         print("对话历史记录")
#         print("=" * 70)
#         for msg in self.messages:
#             if msg.type == "human":
#                 print(f"👤 用户: {msg.content}")
#             elif msg.type == "ai":
#                 print(f"🤖 客服: {msg.content}")
#             print("-" * 50)
#         print("=" * 70 + "\n")


# # ==================== 主程序 ====================

# def print_banner():
#     """打印欢迎横幅"""
#     print("=" * 70)
#     print("智能客服机器人 (LangChain 1.0)")
#     print("=" * 70)
#     print("功能：")
#     print("- 用户信息管理")
#     print("- 订单查询")
#     print("- 问题记录")
#     print("- 跨会话记忆")
#     print("- 对话历史导出")
#     print("=" * 70)
#     print()


# def print_help():
#     """打印帮助信息"""
#     print("\n📖 命令说明:")
#     print("  /help     - 显示帮助信息")
#     print("  /history  - 查看当前对话历史")
#     print("  /sessions - 查看所有历史会话")
#     print("  /export   - 导出当前对话到文件")
#     print("  /new      - 开始新会话")
#     print("  /quit     - 退出程序")
#     print()


# def main():
#     """主程序"""
#     print_banner()
    
#     # 检查API Key
#     if not API_KEY:
#         print("❌ 错误: 未找到 API_KEY，请检查.env文件")
#         print("请在项目根目录创建.env文件，内容为：API_KEY=你的密钥")
#         return
    
#     print(f"✅ API Key 已加载: {API_KEY[:20]}...")
#     print()
    
#     # 初始化机器人
#     bot = CustomerServiceBot()
    
#     # 用户身份选择
#     print("请选择用户:")
#     print("  1. user001 (VIP会员 - 张三)")
#     print("  2. user002 (普通会员 - 李四)")
#     print("  3. 自定义用户ID")
    
#     choice = input("\n请选择 (1/2/3): ").strip()
    
#     if choice == "1":
#         user_id = "user001"
#         user_name = "张三 (VIP会员)"
#     elif choice == "2":
#         user_id = "user002"
#         user_name = "李四 (普通会员)"
#     else:
#         user_id = input("请输入客户ID: ").strip()
#         user_name = user_id
    
#     # 检查历史会话
#     sessions = bot.storage.list_sessions(user_id)
    
#     if sessions:
#         print(f"\n📋 您有 {len(sessions)} 个历史会话:")
#         for i, session in enumerate(sessions[-5:], 1):
#             print(f"  {i}. {session}")
        
#         choice = input("\n是否继续上次对话？(y/n): ").strip().lower()
#         if choice == 'y':
#             session_id = sessions[-1]
#             bot.start_session(user_id, session_id)
#             print(f"✅ 已加载上次对话: {session_id}")
#         else:
#             bot.start_session(user_id, None)
#             print("✅ 开始新会话")
#     else:
#         bot.start_session(user_id, None)
#         print(f"✅ 欢迎新用户: {user_name}")
    
#     # 显示欢迎消息
#     if bot.messages:
#         print(f"\n🤖 {bot.messages[-1].content}\n")
    
#     print_help()
    
#     # 对话循环
#     while True:
#         try:
#             user_input = input("👤 您: ").strip()
            
#             if not user_input:
#                 continue
            
#             # 处理命令
#             if user_input == '/quit':
#                 bot.end_session()
#                 print(f"\n✅ 对话已保存")
#                 print(f"会话ID: {bot.current_session}")
#                 print("感谢使用，再见！")
#                 break
            
#             elif user_input == '/help':
#                 print_help()
#                 continue
            
#             elif user_input == '/history':
#                 bot.show_history()
#                 continue
            
#             elif user_input == '/sessions':
#                 sessions = bot.storage.list_sessions(bot.current_user)
#                 if sessions:
#                     print(f"\n📋 所有历史会话:")
#                     for i, session in enumerate(sessions, 1):
#                         print(f"  {i}. {session}")
#                     print()
#                 else:
#                     print("\n暂无历史会话\n")
#                 continue
            
#             elif user_input == '/export':
#                 export_text = bot.storage.export_conversation(
#                     bot.current_user, 
#                     bot.current_session
#                 )
#                 filename = f"export_{bot.current_user}_{bot.current_session}.txt"
#                 with open(filename, 'w', encoding='utf-8') as f:
#                     f.write(export_text)
#                 print(f"\n✅ 对话已导出到文件: {filename}\n")
#                 continue
            
#             elif user_input == '/new':
#                 bot.end_session()
#                 bot.start_session(bot.current_user, None)
#                 print("\n✅ 已开始新会话")
#                 if bot.messages:
#                     print(f"🤖 {bot.messages[-1].content}\n")
#                 continue
            
#             # 调用客服机器人
#             response = bot.chat(user_input)
#             print(f"🤖 客服: {response}\n")
            
#         except KeyboardInterrupt:
#             print("\n\n👋 再见！")
#             break
#         except Exception as e:
#             print(f"\n❌ 发生错误: {e}\n")


# if __name__ == "__main__":
#     main()

# customer_service_bot_streamlit.py
"""
实战项目：智能客服机器人（LangChain 1.0）- Streamlit 网页版
运行命令：streamlit run customer_service_bot_streamlit.py
公网访问：cpolar http 8501
"""

import os
import json
from datetime import datetime
from typing import Optional

import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv()
API_KEY = os.getenv("API_KEY")

# ==================== 数据管理类（完全保留原代码） ====================

class CustomerDatabase:
    """客户数据库（模拟）"""
    def __init__(self):
        self.customers = {
            "user001": {"name": "张三", "level": "VIP", "phone": "138****1234", "email": "zhangsan@example.com"},
            "user002": {"name": "李四", "level": "普通会员", "phone": "139****5678", "email": "lisi@example.com"}
        }
        self.orders = {
            "user001": [
                {"order_id": "ORD001", "product": "iPhone 15", "status": "已发货", "date": "2024-01-01"},
                {"order_id": "ORD002", "product": "AirPods Pro", "status": "已送达", "date": "2024-01-02"},
                {"order_id": "ORD003", "product": "MacBook Pro", "status": "已发货", "date": "2024-01-03"},
            ],
            "user002": [
                {"order_id": "ORD004", "product": "iPad Air", "status": "已送达", "date": "2024-01-05"},
                {"order_id": "ORD005", "product": "Apple Watch", "status": "处理中", "date": "2024-01-06"},
            ]
        }
    def get_customer(self, user_id: str) -> Optional[dict]:
        return self.customers.get(user_id)
    def get_orders(self, user_id: str) -> list:
        return self.orders.get(user_id, [])


class ConversationStorage:
    """对话存储管理类"""
    def __init__(self, storage_file: str = "customer_service_history.json"):
        self.storage_file = storage_file
    def save(self, user_id: str, session_id: str, messages: list, metadata: dict = None):
        data = self._load()
        if user_id not in data:
            data[user_id] = {}
        serialized = [{"type": msg.type, "content": msg.content, "timestamp": datetime.now().isoformat()} for msg in messages]
        data[user_id][session_id] = {"messages": serialized, "metadata": metadata or {}, "created_at": datetime.now().isoformat()}
        self._save(data)
    def load(self, user_id: str, session_id: str) -> list:
        data = self._load()
        if user_id not in data or session_id not in data[user_id]:
            return []
        messages = []
        for msg_data in data[user_id][session_id]["messages"]:
            if msg_data["type"] == "human":
                messages.append(HumanMessage(content=msg_data["content"]))
            elif msg_data["type"] == "ai":
                messages.append(AIMessage(content=msg_data["content"]))
        return messages
    def list_sessions(self, user_id: str) -> list:
        data = self._load()
        return list(data.get(user_id, {}).keys())
    def export_conversation(self, user_id: str, session_id: str) -> str:
        history = self.get_session_history(user_id, session_id)
        if not history:
            return "无对话记录"
        export_text = f"对话导出 - 用户: {user_id}, 会话: {session_id}\n{'='*50}\n"
        for msg in history:
            export_text += f"[{msg['time']}] {msg['role']}: {msg['content']}\n{'-'*30}\n"
        return export_text
    def get_session_history(self, user_id: str, session_id: str) -> list:
        data = self._load()
        if user_id not in data or session_id not in data[user_id]:
            return []
        return [{"role": "用户" if m["type"] == "human" else "客服", "content": m["content"], "time": m["timestamp"]} 
                for m in data[user_id][session_id]["messages"]]
    def _load(self) -> dict:
        if not os.path.exists(self.storage_file):
            return {}
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    def _save(self, data: dict):
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存失败: {e}")


db = CustomerDatabase()

# ==================== 工具函数（完全保留） ====================

@tool
def get_customer_info(user_id: str) -> str:
    """获取客户信息"""
    customer = db.get_customer(user_id)
    if not customer:
        return f"未找到客户 {user_id} 的信息"
    return f"""客户信息:
姓名: {customer['name']}
会员等级: {customer['level']}
电话: {customer['phone']}
邮箱: {customer['email']}"""

@tool
def query_orders(user_id: str) -> str:
    """查询客户订单"""
    orders = db.get_orders(user_id)
    if not orders:
        return f"客户 {user_id} 暂无订单记录"
    result = f"客户 {user_id} 的订单记录: \n\n"
    for order in orders:
        result += f"订单号: {order['order_id']}\n商品: {order['product']}\n状态: {order['status']}\n下单时间: {order['date']}\n{'-'*40}\n"
    return result

@tool
def get_order_status(order_id: str) -> str:
    """查询订单状态"""
    for user_id, orders in db.orders.items():
        for order in orders:
            if order['order_id'] == order_id:
                return f"""订单 {order_id} 状态:\n商品: {order['product']}\n状态: {order['status']}\n下单时间: {order['date']}\n{'预计明天送达' if order['status'] == '已发货' else ''}"""
    return f"未找到订单 {order_id}"

@tool
def create_ticket(user_id: str, problem: str) -> str:
    """创建客服工单"""
    ticket_id = f"TICKET_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    return f"""已为您创建工单:\n工单号: {ticket_id}\n问题: {problem}\n状态: 待处理\n\n我们的工作人员会在 24 小时内联系您。"""

@tool
def search_knowledge_base(keyword: str) -> str:
    """搜索知识库"""
    knowledge = {
        "退货": "退货政策:\n1. 7天无理由退货\n2. 商品需保持完好\n3. 提供订单号和退货原因",
        "发票": "发票申请:\n1. 登录账户\n2. 进入订单详情\n3. 点击【申请发票】",
        "配送": "配送说明:\n1. 全国包邮\n2. 一般3-5个工作日送达",
        "支付": "支付方式:\n1. 微信支付\n2. 支付宝\n3. 银行卡",
        "售后": "售后服务:\n1. 7天无理由退换货\n2. 1年质保"
    }
    for key, value in knowledge.items():
        if keyword in key or key in keyword:
            return value
    return f"未找到关于'{keyword}'的相关信息，请联系人工客服"


# ==================== 客服机器人核心类（完全保留） ====================

class CustomerServiceBot:
    """智能客服机器人"""
    def __init__(self):
        self.model = init_chat_model(
            "Qwen/Qwen3-8B", model_provider='openai',
            base_url='https://api.siliconflow.cn/v1', api_key=API_KEY, temperature=0
        )
        self.tools = [get_customer_info, query_orders, get_order_status, create_ticket, search_knowledge_base]
        system_prompt = """你是一个专业的客服助手。职责：礼貌回答客户问题，使用工具查询订单/客户信息，解答常见问题，无法解决时创建工单。流程：确认客户身份→了解问题→使用工具→通俗回复。请始终使用中文。"""
        self.agent = create_agent(model=self.model, tools=self.tools, system_prompt=system_prompt)
        self.storage = ConversationStorage()
        self.current_user = None
        self.current_session = None
        self.messages = []
    def start_session(self, user_id: str, session_id: str = None):
        self.current_user = user_id
        self.current_session = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.messages = self.storage.load(user_id, self.current_session)
        if not self.messages:
            welcome = "您好！我是智能客服助手。请问有什么可以帮您？\n\n提示：告诉我您的客户ID（如 user001）"
            self.messages.append(AIMessage(content=welcome))
            self.storage.save(self.current_user, self.current_session, self.messages)
    def chat(self, user_input: str) -> str:
        self.messages.append(HumanMessage(content=user_input))
        try:
            result = self.agent.invoke({"messages": self.messages})
            self.messages = result["messages"]
        except Exception as e:
            error_msg = f"抱歉，处理您的请求时出现了错误：{str(e)}"
            self.messages.append(AIMessage(content=error_msg))
            return error_msg
        self.storage.save(self.current_user, self.current_session, self.messages)
        for msg in reversed(self.messages):
            if msg.type == "ai" and msg.content:
                return msg.content
        return "抱歉，我暂时无法处理您的请求。"


# ==================== Streamlit 网页界面 ====================

st.set_page_config(page_title="智能客服机器人", page_icon="🤖", layout="wide")
st.title("🤖 智能客服机器人")
st.caption("基于 LangChain 1.0 + Qwen3-8B 构建 | 支持订单查询 · 知识问答 · 跨会话记忆")

# 初始化 session 状态
if "bot" not in st.session_state:
    st.session_state.bot = CustomerServiceBot()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "current_session" not in st.session_state:
    st.session_state.current_session = None
if "session_started" not in st.session_state:
    st.session_state.session_started = False

# 侧边栏配置
with st.sidebar:
    st.markdown("## 📋 用户设置")
    
    # 用户选择
    user_option = st.radio("选择用户", ["user001 (VIP会员)", "user002 (普通会员)", "自定义"])
    if user_option == "user001 (VIP会员)":
        user_id = "user001"
    elif user_option == "user002 (普通会员)":
        user_id = "user002"
    else:
        user_id = st.text_input("输入客户ID", value="user003")
    
    # 会话选项
    session_option = st.radio("会话选项", ["开始新会话", "继续上次会话"])
    
    # 开始对话按钮
    if st.button("🚀 开始对话", type="primary", use_container_width=True):
        bot = st.session_state.bot
        sessions = bot.storage.list_sessions(user_id)
        
        if session_option == "继续上次会话" and sessions:
            session_id = sessions[-1]
            bot.start_session(user_id, session_id)
            st.session_state.current_session = session_id
            st.success(f"已加载上次对话 | 会话ID: {session_id[:20]}...")
        else:
            bot.start_session(user_id, None)
            st.session_state.current_session = bot.current_session
            st.success(f"开始新会话 | 会话ID: {bot.current_session[:20]}...")
        
        st.session_state.current_user = user_id
        st.session_state.session_started = True
        # 加载历史消息到界面
        st.session_state.messages = []
        for msg in bot.messages:
            if msg.type == "human":
                st.session_state.messages.append({"role": "user", "content": msg.content})
            elif msg.type == "ai":
                st.session_state.messages.append({"role": "assistant", "content": msg.content})
        st.rerun()
    
    st.markdown("---")
    st.markdown("## 📊 历史记录")
    
    # 查看历史会话
    if st.session_state.current_user:
        sessions = st.session_state.bot.storage.list_sessions(st.session_state.current_user)
        if sessions:
            selected_session = st.selectbox("历史会话", sessions, index=len(sessions)-1 if sessions else 0)
            if st.button("加载此会话"):
                st.session_state.bot.start_session(st.session_state.current_user, selected_session)
                st.session_state.current_session = selected_session
                st.session_state.messages = []
                for msg in st.session_state.bot.messages:
                    if msg.type == "human":
                        st.session_state.messages.append({"role": "user", "content": msg.content})
                    elif msg.type == "ai":
                        st.session_state.messages.append({"role": "assistant", "content": msg.content})
                st.success(f"已加载会话: {selected_session[:30]}...")
                st.rerun()
    
    st.markdown("---")
    if st.button("💾 导出当前对话", use_container_width=True):
        if st.session_state.current_user and st.session_state.current_session:
            export_text = st.session_state.bot.storage.export_conversation(
                st.session_state.current_user, st.session_state.current_session
            )
            st.download_button("下载对话记录", export_text, file_name=f"chat_export_{st.session_state.current_session}.txt")
    
    if st.button("🗑️ 清除对话", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_started = False
        st.session_state.bot = CustomerServiceBot()
        st.success("对话已清除")

# 主对话区域
if not st.session_state.session_started:
    st.info("👈 请先在左侧选择用户并点击「开始对话」")
else:
    # 显示聊天历史
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # 输入框
    if prompt := st.chat_input("请输入您的问题..."):
        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 获取 AI 回复
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                response = st.session_state.bot.chat(prompt)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})