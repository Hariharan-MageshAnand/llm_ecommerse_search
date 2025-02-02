import random
import requests
import sys
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

products = []


def select_best_product(products):
    
    # Sort products by earliest delivery and lowest price
    sorted_products = sorted(products, key=lambda p: (p["Return"], p["Product_Price"]))

    # Select the best product
    best_product = sorted_products[0]

    return best_product

def flipkart_search(search_query, existing_product,color="", price_range="", size="",brand=""):
    existing_data = existing_product.return_data()
    if len(existing_data)!=0:
        req_data = []
        type = search_query

        # Filter products by type and clean price format
        for prod in existing_data:
            if prod["Product_Type"] == type:
                req_data.append(prod)
        req_data = [
            prod for prod in req_data
            if (not color or color in prod["Product_Color"]) and
                (not size or prod["Product_Size"] == size) and
                (not brand or prod["Brand_Name"] == brand) 
        ]

        if req_data:
            print(len(req_data))
            return req_data
        else:
            pass
    in_query_list = str(search_query).split(" ")
    api_url = "https://www.flipkart.com/search?q="
    for q in in_query_list:
        api_url+=q
        api_url+="%20"
    
    if color:
        api_url += f'&p%5B%5D=facets.color%255B%255D%3D{color}'
    if price_range:
        min_price, max_price = price_range.split('-')
        min_price=min_price.replace("$","")
        min_price=min_price.replace("₹","")
        max_price=max_price.replace("$","")
        max_price=max_price.replace("₹","")
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
                        return_policy = 9999
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
                if discount_inc%6 == 0:
                    discount = 'SAVE10'
                else:
                    rand_int = random.randint(1, 100)
                    discount = f'SAVE{rand_int}'
                final_product_data = {
                    "Index": total_products+1,
                    "Brand_Name": brand_name.text,
                    "Product_Type":search_query,
                    "Product_Title": product_title,
                    "Product_URL": "https://www.flipkart.com" + product_url,
                    "Product_Color": product_color,
                    "Product_Size": size,
                    "Discount": discount,
                    "Site":"Flipkart",
                    "Return":return_policy,
                    "Availability":"available"
                    
                }
                try:
                    #final_product_data["Product Price"]= str(product_price.text)    
                    final_product_data["Product_Price"]=float(str(product_price.text).replace("₹", "").replace(",", ""))
                except:
                    final_product_data["Product_Price"]= "Not Found"
                try:
                    final_product_data["Delivery_Date"] = delivery_date.text
                    #remove Delivery by from the date
                    final_product_data["Delivery_Date"] = final_product_data["Delivery Date"].replace("Delivery by", "")
                    #find | and accept value before it
                    final_product_data["Delivery_Date"] = final_product_data["Delivery Date"].split("|")[0]
                except:
                    final_product_data["Delivery_Date"] = ""
                product_data_list.append(final_product_data)
                total_products +=1
                discount_inc+=1
    existing_product.add_data(product_data_list)
    return product_data_list
