import json
from tool import Agent_tool,ProductSearchInput
from langchain.llms import Ollama
from langchain.agents import AgentExecutor
from langchain.chains import LLMChain
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool,StructuredTool
from langchain.prompts import PromptTemplate


class Ecommerce_agent:
    def __init__(self):
        self.search_llm = Ollama(model="llama3.2-vision")
        self.answer_llm = Ollama(model="llama3.2")
        self.agent_tool = Agent_tool(self)
        self.tool_dict = {
            "DiscountChecker":self.agent_tool.best_discount,
            "ReturnChecker":self.agent_tool.return_policy_check,
            "DeliveryChecker":self.agent_tool.delivery_policy_check,
            "SiteCompare":self.agent_tool.site_compare_check
        }
        self.product_json = []
        self.search_tool = Tool(
            name="ProductSearch",
            func=self.agent_tool.handle_search_request,
            description="Fetch product data based on user queries. Accepts only a JSON or dictionary with keys: 'product_type', 'color', 'brand', 'price_range', 'size', and 'discount'. No additional keys are allowed. The price range must be in 'min-max' format; if 'min' is missing, assume 0, and if 'max' is missing, assume 10000. The action should be a single line."
        )
        self.discount_tool = Tool(
            name="DiscountChecker",
            func=self.agent_tool.best_discount,
            description="Use this tool **only** when the user asks about a discount **AND** provides a discount code. "
                        "Input must be a JSON with a single key: 'discount_code'. No other keys are allowed."
        )
        self.return_tool = Tool(
            name="ReturnChecker",
            func=self.agent_tool.return_policy_check,
            description="Use this tool when the user asks whether a product has a return policy. "
                        "Example: 'Does this product have a return policy?'"
        )
        self.delivery_tool = Tool(
            name="DeliveryChecker",
            func=self.agent_tool.delivery_policy_check,
            description="Use this tool when the user asks about estimated delivery time. "
                        "Example: 'When will this product be delivered?'"
        )
        self.site_compare_tool = Tool(
            name="SiteCompare",
            func=self.agent_tool.site_compare_check,
            description="Use this tool when the user wants to compare a product across multiple e-commerce sites "
                        "to determine the best option. Example: 'Which site has the best price for this product?'"
        )
        self.agent = initialize_agent(
            tools=[self.search_tool],
            llm=self.search_llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,  # Enables tool use
            verbose=True,
            memory=ConversationBufferMemory(memory_key="history", return_messages=True),
        )
        
        self.tool_agent = initialize_agent(
            tools=[self.discount_tool,self.return_tool,self.delivery_tool,self.site_compare_tool],
            llm=self.search_llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,  # Enables tool use
            verbose=True,
            memory=ConversationBufferMemory(memory_key="history", return_messages=True),
        )
    
    def add_data(self,data):
        for i in data:
            self.product_json.append(i)
    def return_data(self):
        return self.product_json
    def handle_search(self,data):
        return self.agent_tool.handle_search_request(data)
    def run_search_chain(self,query):
        return self.agent.run(query)
    def run_tool_chain(self,query):
        data = self.tool_agent.run(query)
        print("lsdnfslafasf",data)
        data=str(data).replace("Action: ","")
        data = data.replace("'",'"')
        print("ksjdhfa",data)
        params = json.loads(data)
        print("asdfhasd",params)
        return self.tool_dict[params["action"]](params["action_input"])
    
    
