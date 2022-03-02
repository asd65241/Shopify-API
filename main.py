from typing import Optional

from fastapi import FastAPI, HTTPException

from schema import Query
from core import ShopifyToolkit as Toolkit

app = FastAPI(
    title="Shopify Sales API",
    description="This API used to interact with the Shopify API backend",
    version="1.0.0",
    contact={
        "name": "Tom Mong from Stocksgram",
        "url": "https://stocksgram.com",
        "email": "tom@stocksgram.com",
    },
    docs_url='/'
)

@app.post("/sales/nday/")
async def get_Sales_with_nday_with_login(nday: int, q: Query):
    """
    Get the sales of nday before today
    """
    try:
        tkit = Toolkit(shop_url=q.shop_url, api_secret=q.api_secret)

        results = tkit.getSalesND(nday)
        return results
    except Exception as msg:
        raise HTTPException(status_code=500, detail=repr(msg))

@app.post("/sales/date/")
async def get_Sales_with_date_with_login(q: Query, start_date: Optional[str] = "", end_date: Optional[str] = ""):
    """
    Get the sales of a particular day
    """
    try:
        tkit = Toolkit(shop_url=q.shop_url, api_secret=q.api_secret)

        results = tkit.getSales(start_date, end_date)
        return results
    except Exception as msg:
        raise HTTPException(status_code=500, detail=repr(msg))

