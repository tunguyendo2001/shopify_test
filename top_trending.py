import shopify
import os
import binascii
# import requests
import json
import numpy as np
# from .serializers import ShopifyOauthSerializer

# from .serializers import ShopifyOauthSerializer

shopify.Session.setup(api_key="dc2e36badea90f1496592303b1181023", secret="1decb802b98954f8fd7c476887a1d5fa")
shop_url = "applevn.myshopify.com"
api_version = "2022-04"

state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
redirect_uri = "https://5b84-27-79-160-86.ngrok.io/auth/shopify/callback"
scopes = ['write_products', 'write_customers', 'write_draft_orders']
newSession = shopify.Session(shop_url, api_version)
auth_url = newSession.create_permission_url(scopes, redirect_uri, state)
print("auth_url:\n", auth_url)

session = shopify.Session(shop_url, api_version)
access_token = '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'

session = shopify.Session(shop_url, api_version, access_token)
shopify.ShopifyResource.activate_session(session)

# shop = shopify.Shop.current() # Get the current shop
# product = shopify.Product.find(7222354870449)
# print(shop, product)


# get all customers, productVariants
query = """{
  customers(first: 20) {
    edges {
      node {
        id
        displayName
        numberOfOrders
        updatedAt
        amountSpent {
          amount
          currencyCode
        }
      }
    }
  }
  productVariants(first:20) {
        edges {
        node {
        id
        price
        sku
      }
    }
  }
}"""
# filename1 = './products.json'
# target1 = open(filename1, 'w')
# target1.write(results1)
# target1.close()

# filename2 = './orders.json'
# target2 = open(filename2, 'w')
# target2.write(results)
# target2.close()

results = shopify.GraphQL().execute(query)
# Processing results to get data
results = json.loads(results)
customers = results['data']['customers']
productVariants = results['data']['productVariants']

customers_id = []
edges_customers = customers['edges']
for edge in edges_customers:
        node = edge['node']
        customers_id.append(node['id'])


productVars_id = []
productVars_sku = []
edge_productVars = productVariants['edges']
for edge in edge_productVars:
        node = edge['node']
        productVars_id.append(node['id'])
        sku = int(node['sku'])
        productVars_sku.append(sku)


productVars_name = []
productVars_inventoryQtt = []
for i in range(len(productVars_id)):
        product_id = productVars_id[i]
        query_getProductData = "{{ productVariant(id: \"{product_id}\") {{ displayName inventoryQuantity }} }}".format(product_id=product_id)
        res = json.loads(shopify.GraphQL().execute(query_getProductData))['data']['productVariant']
        # print(res)
        productVars_name.append(res['displayName'][:len(res['displayName'])-16])
        productVars_inventoryQtt.append(res['inventoryQuantity'])


# GET ORDER DATA ONLINE, BUT SHOPIFY DIDN'T GRANT THE ACCESS FOR TESTING/DEVELOPMENT ENVIRONMENTS BUILTS AS A PUBLIC APPS
# customers_name = []
# customers_order = []
# customers_order_createdAt = []
# for i in range(len(customers_id)):
#     _a = []
#     customers_order.append(_a)
    
# for i in range(len(customers_id)):
#         customer_id = customers_id[i]
#         query_getOrderData = """
#           {{
#           customer(id: "{customer_id}") {{
#                 displayName
#             orders(first:10, query:"created_at:>=2022-05-09 AND created_at:<=2022-05-13") {{
#               edges {{
#                 node {{
#                   lineItems(first:10) {{
#                     edges {{
#                       node {{
#                         quantity
#                         product {{
#                           title
#                         }}
#                       }}
#                     }}
#                   }}
#                 }}
#               }}
#             }}
#           }}
#         }}
#         """.format(customer_id=customer_id)
#         print(query_getOrderData)
#         res = json.loads(shopify.GraphQL().execute(query_getOrderData))['data']['customer']
#         customers_name.append(res['displayName'])
#         res = res['orders']['edges']
#         for edge in res:
#                 _order = {}
#                 LineItems = edge['node']['LineItems']['edges']
#                 for _edge in LineItems:
#                         _quantity = _edge['node']['quantity']
#                         _product_name = _edge['node']['product']['title']
#                         _order[_product_name] = _quantity
#                 customers_order[i].append(_order)


customers_name = []
customers_order = []
product_sales = {}
for i in range(len(productVars_id)):
    product_sales[productVars_name[i]] = ["", 0]

for i in range(len(customers_id)):
    _a = []
    customers_order.append(_a)
    
for i in range(7):
    filename = "./"+str(i+1)+"_order.json"
    f = open(filename, 'r')
    res = json.loads(f.read())['data']['customer']
    customers_name.append(res['displayName'])
    res = res['orders']['edges']
    for edge in res:
        _order = {}
        _order[customers_name[-1]] = []
        customers_order_createdAt = edge['node']['createdAt']
        LineItems = edge['node']['lineItems']['edges']
        for _edge in LineItems:
            _quantity = _edge['node']['quantity']
            _product_name = _edge['node']['product']['title']
            if product_sales[_product_name][0] == "":    
                product_sales[_product_name] = [customers_name[-1]]
            else:
                if customers_name[-1] not in product_sales[_product_name]:
                    product_sales[_product_name].append(customers_name[-1])
            value = [_product_name, _quantity, customers_order_createdAt]
            _order[customers_name[-1]].append(value)
        customers_order[i].append(_order)


# tăng đột biến => so sánh số lượng bán được trong 3 ngày
sold_products = {}
sold = np.array(productVars_sku) - np.array(productVars_inventoryQtt)
for i in range(len(productVars_id)):
    sold_products[productVars_name[i]] = sold[i]
sold_products = sorted(sold_products.items(), key=lambda item:item[1], reverse=True)


# số lượng khách mua hàng chiếm hơn 30% ∑ khách hàng
# for i in range(len(product_sales)):
#     print(productVars_name[i], len(product_sales[productVars_name[i]]))
        

# pick top 3 hot trend products
count = 0
for product in sold_products:
    if len(product_sales[product[0]]) > 0.3*len(customers_id):
        print(product[0])
        count += 1
    if count == 3: break








