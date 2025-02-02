from tool import flipkart_search,select_best_product
from langchain.llms import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


class Ecommerce_agent:
    def __init__(self):
        self.search_llm = Ollama(model="llama3.2-vision")
        self.answer_llm = Ollama(model="llama3.2")
        self.product_json = []
        self.search_prompt_template = PromptTemplate(
            input_variables=["query"],
            template=(
            "You are a fashion and clothing e-commerce assistant. "
            "You can only process queries related to clothing and shoes. "
            "If the query is about electronics, home appliances, or anything unrelated to fashion, reject the request.\n\n"
            
            "The **most important** element is the **product type** (e.g., shirt, jeans, dress, shoes). "
            "Make sure to **always** extract the product type from the query. If the product type is not clearly mentioned, respond with: "
            "'Product type is missing. Please specify the product type (e.g., shirt, jeans, dress, shoes).'\n\n"
        
            "For the other attributes (color, brand, size, price range), you should only extract them if they are clearly mentioned. "
            "If any attribute is missing, return it as an empty string (e.g., '' for missing color, brand, size, etc.).\n\n"
        
            "The query must **always** contain the product type, and you should ensure the following:\n"
            "1. Extract the product type first (e.g., shirt, dress, jeans, etc.).\n"
            "2. If available, extract color, brand, size, and price range as additional attributes.\n"
            "3. If the user ask for product type shoes or any footwear check size in integer.\n"
            "4. If size is missing, return an empty string for 'size'.\n"
            "5. Price Range should always have min-max format if user not given any one let's assume 0 for min and 500000 as max respectively.\n"
            "6. Remove all the special characters in the price range if present.\n\n"
        
            "If the query does not provide the product type, respond with: 'Product type is missing. Please specify the product type (e.g., shirt, jeans, dress, shoes).'\n\n"
            
        
            "The output should be a **JSON object** with the following keys: "
            "'product_type', 'color', 'brand', 'price_range', 'size', and 'discount'. If any attribute is missing, return it as an empty string.\n\n"
        
            "Query: {query}"
            )
        )
        self.answer_template = PromptTemplate(
        input_variables=[
        "search_result", "user_query"
    ],
    template=(
        "You are a knowledgeable and helpful e-commerce assistant. The user searched for a product, "
        "and we found a list of options based on **earliest delivery** and **lowest price**.\n\n"
        
        "Here are the details of the available products: {search_result}\n"
        "Each product has the following information:\n"
        "- **Brand_Name**: The brand of the product.\n"
        "- **Product_Type**: The type/category of the product.\n"
        "- **Product_Title**: The title of the product.\n"
        "- **Product_Color**: Available colors for the product.\n"
        "- **Product_Size**: Available sizes for the product.\n"
        "- **Product_Price**: Price of the product.\n"
        "- **Discount**: Any active discount on the product.\n"
        "- **Delivery_Date**: Estimated delivery date for the product.\n"
        "- **Product_URL**: Link to purchase the product.\n"
        "- **Availability**: Product available or not.\n"
        "- **Return**: Return policy for the product.\n\n"
        
        "The user has provided the following search query: {user_query}\n"
        
        "Your task is to **identify the best product** from the provided list based on the user's query. "
        "Please pay close attention to any product attributes (like size, color, price range, etc.) mentioned in the query. "
        "The product you choose should align with the user's preferences, ensuring the **earliest delivery** and the **lowest price**. "
        "Be sure to explain your choice clearly and professionally.\n\n"
        
        "### Response Format:\n"
        "Provide the best matching product details with its product name product brand price and return policy.\n\n"
        
        "### Why this product? Explain why this product was selected based on:\n"
        "1. **Price**: How it offers the best value for money.\n"
        "2. **Delivery Time**: Why this product has the best delivery time.\n"
        "3. **Product Fit**: How well it fits the user’s preferences (size, color, brand).\n"
        "4. **Return Policy**: How the return policy adds to the product's appeal.\n\n"
        
        "Ensure the response is **clear, concise, and friendly**, and help the user understand why this is the best option."
    )
        )
        self.search_chain = LLMChain(llm=self.search_llm,prompt=self.search_prompt_template)
        self.answer_chain = LLMChain(llm=self.answer_llm,prompt=self.answer_template)
    
    def add_data(self,data):
        for i in data:
            
                self.product_json.append(i)
    def return_data(self):
        return self.product_json
    
    def run_search_chain(self,query):
        return self.search_chain.run(query=query)
    
    def run_answer_chain(self,search_result,user_query):
        response = self.answer_chain.run(search_result=search_result,user_query=user_query)
        return response
    
    def handle_search_request(self,params):
        """
        Calls flipkart_search with parsed parameters.
        """
        print(params)
        search_query = params.get("product_type", "")
        color = params.get("color", "")
        # Capitalize first letter of color
        if len(color)!=0:
            color = str(color)[0].upper() + str(color)[1:]  
        price_range = params.get("price_range", "")
        size = params.get("size", "")
        brand = params.get("brand", "")

        # Call the function from tool.py
        product_data = flipkart_search(search_query, self ,color, price_range, size, brand)

        return product_data
