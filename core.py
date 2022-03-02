import requests
import pandas as pd
from decimal import *
import math
import json
import pathlib
import os
import pytz
from datetime import datetime, date, time, timedelta

from decorator import Error_Handler

class ShopifyToolkit:
    """ShopifyToolKit.

    This module used to interact with the Shopify Exchange backend, which used mainly for inventory and order management

    """
    @Error_Handler
    def __init__(self, shop_url, api_secret, location="sales-record/", maxRetry=5, limit=250):
        """__init__

        The method initialize the object with its location, username, password and merchant id

        Note:
            Do not include the `self` parameter in the ``Args`` section.

        Args:
            shop_url   (str): The Shopify domain of your store (i.e. {store_name}.myshopify.com).
            api_secret (str): Your Shopify API Secret.
            location   (str): The path your sales report will be storing.
            maxRetry   (str): The max retry number.
        """
        self.shop_url = "https://" + shop_url
        self.api_secret = api_secret
        self.location = location
        self.maxRetry = maxRetry
        self.limit = limit

        # Create the location
        path = pathlib.Path(location)
        if not path.exists():
            # Create the location
            os.mkdir(location)

    @Error_Handler
    def __dict_clean(self,obj):
        result = {}
        for key, value in obj.items():
            if value == None:
                value = ""
            result[key] = value
        return result

    @Error_Handler
    def __processOrder(self, order):
        order_item = [
            self.__dict_clean({
            "shopify_id": str(order['id']),
            "order_id": order['name'],
            "order_amount": float(order['current_subtotal_price']),
            "order_created_at": order['created_at'],
            "order_financial_status": order['financial_status'],
            "order_fulfillment_status": order['fulfillment_status'],
            "discount_amount": float(order['current_total_discounts']),
            "discount_code": order['discount_codes'][0]['code'] if not len(order['discount_codes']) == 0 else "",
            "customer_id": str(order['customer']['id']),
            "customer_email": order['customer']['email'],
            "customer_emailIsValidated": True if order['customer']['verified_email'] == True else False,
            "customer_phone": str(order['billing_address']['phone']),
            "customer_first_name": order['customer']['first_name'],
            "customer_last_name": order['customer']['last_name'],
            "payment_gateway": order['gateway'],
            "referring_site": order['referring_site'],
            "landing_page": order['landing_site'],
            "user_agent": order['client_details']['user_agent'],
            "order_product_quantity": int(str(sum([int(item['quantity']) for item in order['line_items']]))),
            "order_product_total_original_price": float(str(sum([Decimal(item['price']) * Decimal(item['quantity']) for item in order['line_items']]))),
            "product_id": str(item['id']),
            "product_name": str(item['name']),
            "product_sku": str(item['sku']) if item['sku'] else "",
            "product_unit_price": float(item['price']),
            "product_quantity": int(item['quantity']),
            "product_total_discount": float(item['total_discount']),
            "product_net_amount": float(str(Decimal(item['price']) * Decimal(item['quantity']) - Decimal(item['total_discount']))),
            "product_mean_unit_selling_price": float(str(round((Decimal(item['price'])/Decimal(str(sum([Decimal(item['price']) * Decimal(item['quantity']) for item in order['line_items']]))) * Decimal(order['current_subtotal_price'])),2))),
            "product_mean_selling_price": float(str(round(((Decimal(item['price'])* Decimal(item['quantity']))/Decimal(str(sum([Decimal(item['price']) * Decimal(item['quantity']) for item in order['line_items']]))) * Decimal(order['current_subtotal_price'])),2))),
            }) for item in order["line_items"] ]

        return order_item

    @Error_Handler
    def __getShopifySales(self, query):
        """__getShopifySales

        The method will get the daily sales excel from the Shopify

        Args:
            query  (str) : The url of your api endpoint

        Return:
            orders (list): The orders of the given query
        """

        error_msg = ""
        for _ in range(self.maxRetry):
            try:
                isNext = True
                count = 1
                
                order_list = []
                orders_url = query
                while isNext:
                    r = requests.get(orders_url,headers={"X-Shopify-Access-Token":self.api_secret})
                    
                    # Get Metadata
                    if "Link" in r.headers:
                        link = r.headers['Link']
                        if "," in link:
                            link = link.split(',')
                            link = link[1].split(';')
                            orders_url = link[0].strip()[1:-1]
                            isNext = "next" in link[1]
                        else:
                            link = link.split(';')
                            orders_url = link[0].strip()[1:-1]
                            isNext = "next" in link[1]
                    else:
                        isNext = False

                    count = count + 1
                    
                    # Do work
                    for order in r.json()['orders']:
                        order_list += self.__processOrder(order)
                        
                return order_list
            except Exception as msg:
                # Succesfully Login, then break the for loop
                error_msg += repr(msg)

        raise Exception(f"Error Occured after max retry: {error_msg}")

    def __convertToUTCString(self, date):
        """__convertToUTC

        The method will convert the local datetime to utc time

        Args:
            date (date): The date obejct created using datetime package

        Return:
            date (datetime): The datetime object of the utc time

        Note: Datetime reference: https://stackoverflow.com/questions/373370/how-do-i-get-the-utc-time-of-midnight-for-a-given-timezone
        """
        tz = pytz.timezone("Asia/Hong_kong")
        midnight_without_tzinfo = datetime.combine(date, time())
        midnight_with_tzinfo = tz.localize(midnight_without_tzinfo)
        yesterday = midnight_with_tzinfo.astimezone(pytz.utc)

        return yesterday.strftime(f"%Y-%m-%dT%H:%M:%SZ")

    @Error_Handler
    def __getDay(self, last=1):
        """__getDay

        The method will return the date of n day before today.

        Args:
            last (int): How many day before to to day (e.g today is 20220210, if last=1, then return 20220209)

        Return:
            date (str): The date string in the format of {yyyymmdd}
        """
        today = date.today()
        yesterday = today - timedelta(days=last)

        # Generate UTC Time
        return yesterday.strftime(f"%Y-%m-%d")

    @Error_Handler
    def getSalesND(self, date=0):
        today = self.__getDay(-1)
        nday = self.__getDay(date)
        return self.getSales(start_date=nday, end_date=today)

    @Error_Handler
    def getSales(self, start_date="", end_date=""):
        """getSales

        The method will return the daily sales of a given day

        Args:
            start_date (int): The date of the sales report in the format of {yyyy-mm-dd}
            end_date (int): The date of the sales report in the format of {yyyy-mm-dd}

        Return:
            sales (list): The list of dict of each row of the sales listed items
        """

        api_url = self.shop_url + f"/admin/api/2022-01/orders.json?status=any&limit={self.limit}"

        if start_date != "":
            start_date = datetime.strptime(start_date,"%Y-%m-%d")
            start_date = self.__convertToUTCString(start_date)
            api_url += f"&created_at_min={start_date}"

        if end_date != "":
            end_date = datetime.strptime(end_date,"%Y-%m-%d")
            end_date = self.__convertToUTCString(end_date)
            api_url += f"&created_at_max={end_date}"

        print(api_url)

        result = self.__getShopifySales(query=api_url)

        return result


if __name__ == '__main__':
    try:
        shop_url = ""
        api_secret = ""

        tbox = ShopifyToolkit(shop_url=shop_url, api_secret=api_secret)
        sales_data = tbox.getSalesND(1)
        print(sales_data)

        # df = pd.DataFrame(sales_data)
        # df.to_excel("orders.xlsx")
    except Exception as msg:
        print(msg)
