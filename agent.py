import json
from tool import Agent_tool
from langchain.llms import Ollama
from langchain.chains import LLMChain
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool


class Ecommerce_agent:
    """
    The Ecommerce_agent class is designed to facilitate e-commerce operations using language models (LLMs) and various tools. 
    It provides functionalities for product search, discount checking, return policy checking, delivery policy checking, 
    and site comparison. The class initializes with specific LLM models and tools, and it supports running search and tool 
    chains based on user queries.
    Attributes:
        search_llm (Ollama): The language model used for search operations.
        answer_llm (Ollama): The language model used for answering queries.
        agent_tool (Agent_tool): An instance of Agent_tool to handle various tool operations.
        tool_dict (dict): A dictionary mapping tool names to their corresponding functions.
        product_json (list): A list to store product data in JSON format.
        search_tool (Tool): A tool for handling product search requests.
        discount_tool (Tool): A tool for checking discounts based on user-provided discount codes.
        return_tool (Tool): A tool for checking return policies of products.
        delivery_tool (Tool): A tool for checking estimated delivery times of products.
        site_compare_tool (Tool): A tool for comparing products across multiple e-commerce sites.
        agent (Agent): An initialized agent for handling search operations.
        tool_agent (Agent): An initialized agent for handling tool operations.
    Methods:
        add_data(data): Adds product data to the product_json list.
        return_data(): Returns the product data stored in product_json.
        handle_search(data): Handles search requests using the agent_tool.
        run_search_chain(query): Runs the search chain based on the user query.
        run_tool_chain(query): Runs the tool chain based on the user query and returns the result.
        (comments generated by copilot)
    """
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
        data=str(data).replace("Action: ","")
        data = data.replace("'",'"')
        params = json.loads(data)
        return self.tool_dict[params["action"]](params["action_input"])
    
    
