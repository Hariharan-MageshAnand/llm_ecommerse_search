import random
import requests
import sys
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json
from pydantic import BaseModel
from typing import Optional

class ProductSearchInput(BaseModel):
    product_type: str
    color: Optional[str] = ""
    brand: Optional[str] = ""
    price_range: Optional[str] = ""
    size: Optional[str] = ""
    discount: Optional[str] = ""
products = []
class Agent_tool:
    def __init__(self,agent):
        self.product_data = []
        self.agent = agent
    def handle_search_request(self,params):
        """
        Calls flipkart_search with parsed parameters.
        """
        
        params = str(params)
        params = params.replace("'",'"')
        params = json.loads(params)
        search_query = params.get("product_type", "")
        color = params.get("color", "")
        # Capitalize first letter of color
        if len(color)!=0:
            color = str(color)[0].upper() + str(color)[1:]  
        price_range = params.get("price_range", "")
        size = params.get("size", "")
        brand = params.get("brand", "")

        # Call the function from tool.py
        product_data = self.flipkart_search(search_query,color, price_range, size, brand)
        print("total data",len(product_data))
        return product_data
    
    def return_policy_check(self,params):
        product_data = self.agent.return_data()
        for product in product_data:
            if product["Return"]!=0:
                return f"The maximum return day for this product {product['Product_Title']} is {product['Return']} days"
        return f"No return for this product {product['Product_Title']}"


    def select_best_product(self,products):
    
        # Sort products by earliest delivery and lowest price
        sorted_products = sorted(products, key=lambda p: (p["Return"], p["Product_Price"]))
        # Select the best product
        best_product = sorted_products[0]

        return best_product
    def delivery_policy_check(self,params):
        product_data  = self.agent.return_data()
        product_data= product_data[0]
        return f"The delivery time are approximately {product_data['Delivery_Date']}"
    def site_compare_check(self,params):
        product_data  = self.agent.return_data()
        siteA=None
        siteB=None
        for product in product_data:
            if product["Site"]=="Site A":
                siteA=product
            else:
                siteB=product
        if siteA["Product_Price"]>siteB["Product_Price"]:
            return f"The product {siteA['Product_Title']} from Site A is better"
        else:
            return f"The product {siteB['Product_Title']} from Site B is better"
    def best_discount(self,discount_code = ""):
        
        product_data = self.agent.return_data()
        if discount_code=="":
            sorted_products = sorted(product_data, key=lambda p: (p["Discount"]))
    
            best_product = sorted_products[0]
            return f"this product {best_product['Product_Title']} from brand {best_product['Brand_Name']} on site {best_product['Site']} have the best discount with product prize {best_product['Product_Price']}"
        else:
            discount_code = discount_code["tool_input"]
            print("discount code",discount_code)
            for product in product_data:
                if product["Discount"]==discount_code:
                    return f"this product {product['Product_Title']} from brand {product['Brand_Name']} on site {product['Site']} have the discount with product prize {product['Product_Price']}"
                else:
                    return f"the Discount is not available try different discount"

    def flipkart_search(self,search_query,color="", price_range="", size="",brand=""):
        in_query_list = str(search_query).split(" ")
        api_url = "https://www.flipkart.com/search?q="
        for q in in_query_list:
            api_url+=q
            api_url+="%20"
        
        if color:
            api_url += f'&p%5B%5D=facets.color%255B%255D%3D{color}'
        if price_range:
            try:
                min_price, max_price = price_range.split('-')
                min_price=min_price.replace("$","")
                min_price=min_price.replace("₹","")
                max_price=max_price.replace("$","")
                max_price=max_price.replace("₹","")
            except:
                price_range = list(map(int, price_range.strip("[]").split(", ")))
                min_price,max_price = price_range[0],price_range[1]
            api_url += f'&p%5B%5D=facets.price_range.from%3D{min_price}&p%5B%5D=facets.price_range.to%3D{max_price}'
        if size:
            if search_query=="shoes" or search_query=="sneakers":
                api_url+=f'&p%5B%5D=facets.uk_india_size%255B%255D%3D{size}'
            else:
                size = size.capitalize()
                api_url += f'&p%5B%5D=facets.size%255B%255D%3D{size}'
        if brand:
            api_url += f'&p%5B%5D=facets.brand%255B%255D%3D{brand}'
    
        print(f"Fetching data from: {api_url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
    
        response = requests.get(api_url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")
        data = soup.find_all('div', class_='DOjaWF gdgoEp')
        data  = BeautifulSoup(str(data), "lxml")
        columns = data.find_all('div', class_='cPHDOP col-12-12')
        #print(len(columns))
        total_products = 0
        product_data_list = []
        discount_inc = 0
        min_price=0
        max_price=10000
        
        for col in columns:
            product_data = col.find_all('div', class_='_1sdMkc LFEi7Z') 
            #print(len(product_data))
            for product in product_data:
                    brand_name  =product.find('div', class_='syl9yP') # brand name
                    product_price = product.find('div', class_='Nx9bqj') # product price   
                    product_meta_data = product.find('a', class_='WKTcLC') # product meta data
                    html = BeautifulSoup(str(product_meta_data), "lxml")
                    link_tag = html.find('a', class_="WKTcLC")
                    if link_tag:
                        product_url = link_tag.get("href")
                        product_title = link_tag.get("title")
                        
                        product_request = requests.get("https://www.flipkart.com" + product_url, headers=headers)
                        product_soup = BeautifulSoup(product_request.text, "lxml")
                        delivery_date = product_soup.find('div', class_="hVvnXm")
                        product_row = product_soup.findAll('div', class_="row")
                        return_policy_class = product_soup.find_all('div',class_="YhUgfO")
                        return_policy =None
                        for rr in return_policy_class:
                            if "return policy" in rr.text:
                                return_policy = rr
                        try:
                            return_policy = int(str(return_policy.text).split(" ")[0])
                        except:
                            return_policy = 0
                        product_color = None
                        for row in product_row:
                            temp_row = BeautifulSoup(str(row), "lxml")  
                            #print(temp_row)
                            temp_col = temp_row.find_all('div', class_="col col-3-12 _9NUIO9")
                            temp_row = temp_row.find_all('div', class_="col col-9-12 -gXFvC")
                            for i in range(len(temp_col)):
                                if temp_col[i].text == "Color":
                                    product_color = str(temp_row[i].text).split(", ")
                                    break
                    discount = None
                    site = None
                    if discount_inc%6 == 0:
                        discount = 'SAVE10'
                        site = "Site A"
                    else:
                        rand_int = random.randint(1, 100)
                        discount = f'SAVE{rand_int}'
                        site = "Site B"
                    final_product_data = {
                        "Index": total_products+1,
                        "Brand_Name": brand_name.text,
                        "Product_Type":search_query,
                        "Product_Title": product_title,
                        "Product_URL": "https://www.flipkart.com" + product_url,
                        "Product_Color": product_color,
                        "Product_Size": size,
                        "Discount": discount,
                        "Site":site,
                        "Return":return_policy,
                        "Availability":"available"
                        
                    }
                    try:
                        #final_product_data["Product Price"]= str(product_price.text)    
                        final_product_data["Product_Price"]=float(str(product_price.text).replace("₹", "").replace(",", ""))
                    except:
                        final_product_data['Product_Price'] = random.uniform(float(min_price),float(max_price))
                    try:
                        final_product_data["Delivery_Date"] = delivery_date.text
                        #remove Delivery by from the date
                        final_product_data["Delivery_Date"] = final_product_data["Delivery Date"].replace("Delivery by", "")
                        #find | and accept value before it
                        final_product_data["Delivery_Date"] = final_product_data["Delivery Date"].split("|")[0]
                    except:
                        final_product_data['Delivery_Date'] = '8 Feb'
                    product_data_list.append(final_product_data)
                    total_products +=1
                    discount_inc+=1
        self.product_data = product_data_list
        return product_data_list

    def myntra_search(self,search_query,color="", price_range="", size="",brand=""):
        in_query_list = str(search_query).split(" ")
        api_url = "https://www.myntra.com/"
        for q in in_query_list:
                api_url+=q
                api_url+="%20"
        api_url+="?"
        if brand:
            if "f=" not in api_url:
                api_url+='f='
            api_url+=f'Brand%3A{brand}'
        if color:
            if "f=" not in api_url:
                api_url+='f='
            else:
                api_url+='%3A%3A'
            api_url+= f'Color%3A{color}'
        
        if size:
            if "f=" not in api_url:
                api_url+="f="
            else:
                api_url+="%3A%3A"
            if "sneaker" in search_query or "shoe" in search_query:
                size = f"UK{size}"
            else:
                size = str(size).capitalize()
            api_url+=f'size_facet%3A{size}'
        if price_range:
            try:
                min_price, max_price = price_range.split('-')
                min_price=min_price.replace("$","")
                min_price=min_price.replace("₹","")
                max_price=max_price.replace("$","")
                max_price=max_price.replace("₹","")
            except:
                price_range = list(map(int, price_range.strip("[]").split(", ")))
                min_price,max_price = price_range[0],price_range[1]
            if "f=" not in api_url:
                api_url+="f="
            api_url+=f'&rf=Price%3A{float(min_price)}_{float(max_price)}_{float(min_price)}%20TO%20{float(max_price)}'
            #api_url.replace("Price%3A","Price3A")
        print(api_url)
        print(f"Fetching data from: {api_url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        response = requests.get(api_url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")
        data = soup.find_all('div',class_=' row-base')
        for i in data:
            print(i)