# 🤖 智能客服机器人

基于 LangChain 和 Streamlit 构建的智能客服系统，支持订单查询、客户管理、知识问答、工单创建等多种实用功能。

## ✨ 功能特性

| 功能 | 描述 | 示例 |
|------|------|------|
| 👤 客户信息查询 | 获取客户姓名、会员等级、联系方式 | "查询user001的信息" |
| 📦 订单查询 | 查询客户所有历史订单 | "查询我的订单" |
| 🚚 订单状态 | 查询指定订单的物流状态 | "ORD001现在到哪了" |
| 📚 知识库问答 | 退货、发票、配送、支付等常见问题 | "怎么退货" |
| 🎫 工单创建 | 无法解决的问题自动创建工单 | "我遇到问题了" |
| 💬 多会话管理 | 支持多用户多会话独立保存 | 自动功能 |
| 📄 对话导出 | 导出完整对话记录为文本 | 侧边栏导出按钮 |

## 🚀 快速开始

### 📋 环境要求

- Python 3.11+
- SiliconFlow API Key

### 📥 安装步骤

1. 克隆仓库
   git clone https://github.com/M1dnat/Intelligent-customer-service-robot.git
   cd Intelligent-customer-service-robot

2. 安装依赖
   pip install streamlit langchain langchain-core python-dotenv

3. 配置 API Key
   echo "API_KEY=your_api_key_here" > .env

4. 运行应用
   streamlit run customer_service_bot.py

5. 访问界面
   打开浏览器访问：http://localhost:8501

## 📁 项目结构

Intelligent-customer-service-robot/
├── 📄 customer_service_bot.py         # 主程序文件
├── 💾 customer_service_history.json   # 对话历史存储
├── 🔐 .env                             # 配置文件
└── 📦 requirements.txt                 # 依赖列表

## 🌐 公网访问

cpolar http 8501

## 📄 License

MIT
