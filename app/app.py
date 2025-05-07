from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from redis import Redis
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import List
import logging
import time
app = FastAPI()


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Inventory Management API", version="1.0.0")

import psycopg2
from psycopg2.extras import RealDictCursor
import time

while True:
    try:
        conn = psycopg2.connect(
            host="postgres",            
            database="mydb",           
            user="user",                
            password="password",        
            cursor_factory=RealDictCursor
        )
        print(" Connected to DB successfully!")
        break
    except Exception as error:
        print(" Database connection failed:", error)
        time.sleep(2)


# Redis connection
redis = Redis(host=os.getenv("REDIS_HOST"), port=6379, decode_responses=True)

# Pydantic models
class ItemCreate(BaseModel):
    name: str
    description: str
    price: float
    quantity: int

class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    quantity: int | None = None

class Item(BaseModel):
    id: int
    name: str
    description: str
    price: float
    quantity: int

# Database initialization
def init_db():
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                price FLOAT NOT NULL,
                quantity INTEGER NOT NULL
            )
        """)
        conn.commit()
    logger.info("Database initialized")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/")
async def root():
    return {"message": "Welcome to the Inventory Management API"}

@app.post("/items/", response_model=Item)
async def create_item(item: ItemCreate):
    try:
        start_time = time.time()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO items (name, description, price, quantity)
                VALUES (%s, %s, %s, %s)
                RETURNING *
            """, (item.name, item.description, item.price, item.quantity))
            new_item = cur.fetchone()
            conn.commit()
        
        # Clear cache
        redis.delete("items_all")
        logger.info(f"Created item {new_item['id']} in {time.time() - start_time:.2f}s")
        return new_item
    except Exception as e:
        logger.error(f"Error creating item: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/items/", response_model=List[Item])
async def get_items():
    try:
        # Check cache
        cached = redis.get("items_all")
        if cached:
            logger.info("Returning items from cache")
            return JSONResponse(content=cached)

        start_time = time.time()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM items")
            items = cur.fetchall()
        
        # Cache result for 60 seconds
        redis.setex("items_all", 60, JSONResponse(content=items).body.decode())
        logger.info(f"Retrieved {len(items)} items in {time.time() - start_time:.2f}s")
        return items
    except Exception as e:
        logger.error(f"Error retrieving items: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    try:
        # Check cache
        cached = redis.get(f"item_{item_id}")
        if cached:
            logger.info(f"Returning item {item_id} from cache")
            return JSONResponse(content=cached)

        start_time = time.time()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM items WHERE id = %s", (item_id,))
            item = cur.fetchone()
        
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Cache result for 60 seconds
        redis.setex(f"item_{item_id}", 60, JSONResponse(content=item).body.decode())
        logger.info(f"Retrieved item {item_id} in {time.time() - start_time:.2f}s")
        return item
    except Exception as e:
        logger.error(f"Error retrieving item {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemUpdate):
    try:
        start_time = time.time()
        update_data = item.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        set_clause = ", ".join(f"{k} = %s" for k in update_data.keys())
        values = list(update_data.values()) + [item_id]
        
        with conn.cursor() as cur:
            cur.execute(f"""
                UPDATE items
                SET {set_clause}
                WHERE id = %s
                RETURNING *
            """, values)
            updated_item = cur.fetchone()
            conn.commit()
        
        if not updated_item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Clear caches
        redis.delete("items_all")
        redis.delete(f"item_{item_id}")
        logger.info(f"Updated item {item_id} in {time.time() - start_time:.2f}s")
        return updated_item
    except Exception as e:
        logger.error(f"Error updating item {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    try:
        start_time = time.time()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM items WHERE id = %s RETURNING id", (item_id,))
            deleted = cur.fetchone()
            conn.commit()
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Clear caches
        redis.delete("items_all")
        redis.delete(f"item_{item_id}")
        logger.info(f"Deleted item {item_id} in {time.time() - start_time:.2f}s")
        return {"message": f"Item {item_id} deleted"}
    except Exception as e:
        logger.error(f"Error deleting item {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")