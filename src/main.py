from __future__ import annotations
import hashlib, math, os, random, time
from datetime import datetime, timezone
from typing import Any
import requests
from fastapi import FastAPI, Query
from pydantic import BaseModel

SERVICE_NAME = os.getenv("SERVICE_NAME", "frontend")
DEFAULT_DELAY_MS = int(os.getenv("DEFAULT_DELAY_MS", "0"))
ERROR_RATE = float(os.getenv("ERROR_RATE", "0"))
CATALOG_URL = os.getenv("CATALOG_URL", "http://catalog:8080")
CART_URL = os.getenv("CART_URL", "http://cart:8080")
CHECKOUT_URL = os.getenv("CHECKOUT_URL", "http://checkout:8080")
PAYMENT_URL = os.getenv("PAYMENT_URL", "http://payment:8080")
INVENTORY_URL = os.getenv("INVENTORY_URL", "http://inventory:8080")
RECOMMENDATION_URL = os.getenv("RECOMMENDATION_URL", "http://recommendation:8080")
app = FastAPI(title="CompanyCloud ShopLab", version="1.0.0")

PRODUCTS = [
    {"id":"p-100","name":"Cloud Hoodie","price":59.0},
    {"id":"p-200","name":"DevOps Mug","price":14.0},
    {"id":"p-300","name":"Observability Notebook","price":9.0},
    {"id":"p-400","name":"Kubernetes Stickers","price":5.0},
]
class CartRequest(BaseModel):
    product_id: str = "p-100"
    quantity: int = 1
class CheckoutRequest(BaseModel):
    user_id: str = "demo-user"
    product_id: str = "p-100"
    quantity: int = 1

def maybe_delay(extra_ms:int=0):
    ms=max(0, DEFAULT_DELAY_MS+extra_ms)
    if ms: time.sleep(ms/1000)
def maybe_error():
    if ERROR_RATE and random.random() < ERROR_RATE: raise RuntimeError("simulated error")
def resp(payload:dict[str,Any]|None=None):
    maybe_error(); d={"ok":True,"service":SERVICE_NAME,"ts":datetime.now(timezone.utc).isoformat()}
    if payload: d.update(payload)
    return d
def get_json(base,path):
    r=requests.get(base+path, timeout=5); r.raise_for_status(); return r.json()
def post_json(base,path,body):
    r=requests.post(base+path, json=body, timeout=5); r.raise_for_status(); return r.json()

@app.get("/health")
def health(): return {"ok": True, "service": SERVICE_NAME}
@app.get("/status")
def status(): return resp({"default_delay_ms":DEFAULT_DELAY_MS,"error_rate":ERROR_RATE})
@app.get("/")
def home():
    maybe_delay()
    return resp({"app":"CompanyCloud ShopLab","purpose":"controlled microservices testbed","endpoints":["/products","/checkout","/work?delay_ms=100","/cpu?level=medium"]})
@app.get("/products")
def products(limit:int=Query(4,ge=1,le=5000), delay_ms:int=Query(0,ge=0,le=5000)):
    maybe_delay(delay_ms)
    if SERVICE_NAME=="frontend": return get_json(CATALOG_URL, f"/products?limit={limit}&delay_ms={delay_ms}")
    items=(PRODUCTS*((limit//len(PRODUCTS))+1))[:limit]
    return resp({"count":len(items),"products":items})
@app.post("/cart/add")
def cart_add(req:CartRequest):
    maybe_delay(20)
    if SERVICE_NAME=="frontend": return post_json(CART_URL,"/cart/add",req.model_dump())
    return resp({"cart_action":"add","product_id":req.product_id,"quantity":req.quantity})
@app.get("/recommendations")
def recommendations(delay_ms:int=Query(20,ge=0,le=5000)):
    maybe_delay(delay_ms)
    if SERVICE_NAME=="frontend": return get_json(RECOMMENDATION_URL, f"/recommendations?delay_ms={delay_ms}")
    return resp({"recommended":["p-100","p-200"],"model":"simple-popularity"})
@app.post("/checkout")
def checkout(req:CheckoutRequest):
    maybe_delay(30)
    if SERVICE_NAME=="frontend": return post_json(CHECKOUT_URL,"/checkout",req.model_dump())
    if SERVICE_NAME=="checkout":
        catalog=get_json(CATALOG_URL,"/products?limit=1&delay_ms=20")
        inv=post_json(INVENTORY_URL,"/reserve",{"product_id":req.product_id,"quantity":req.quantity})
        pay=post_json(PAYMENT_URL,"/charge",{"amount":59.0*req.quantity,"user_id":req.user_id})
        return resp({"checkout":"accepted","catalog_count":catalog.get("count"),"inventory":inv,"payment":pay})
    return resp({"checkout":"noop"})
@app.get("/checkout")
def checkout_get(delay_ms:int=Query(50,ge=0,le=5000)):
    maybe_delay(delay_ms)
    if SERVICE_NAME=="frontend": return post_json(CHECKOUT_URL,"/checkout",{"user_id":"demo-user","product_id":"p-100","quantity":1})
    return resp({"checkout_get":True})
@app.post("/charge")
def charge(body:dict[str,Any]):
    maybe_delay(40); return resp({"payment_status":"approved","amount":body.get("amount",0)})
@app.post("/reserve")
def reserve(body:dict[str,Any]):
    maybe_delay(25); return resp({"reserved":True,"product_id":body.get("product_id"),"quantity":body.get("quantity",1)})
@app.get("/work")
def work(delay_ms:int=Query(100,ge=0,le=10000)):
    maybe_delay(delay_ms); return resp({"work_type":"controlled_delay","delay_ms":delay_ms})
@app.get("/cpu")
def cpu(level:str=Query("medium", pattern="^(low|medium|high)$")):
    loops={"low":40000,"medium":160000,"high":500000}[level]
    val=0.0
    for i in range(loops): val += math.sqrt((i%100)+1)
    return resp({"work_type":"cpu","level":level,"loops":loops,"digest":hashlib.sha256(str(val).encode()).hexdigest()[:12]})
@app.get("/worker/run")
def worker_run(delay_ms:int=Query(200,ge=0,le=10000)):
    maybe_delay(delay_ms); return resp({"worker_job":"completed","delay_ms":delay_ms})
