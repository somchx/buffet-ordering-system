from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./buffet.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(String, nullable=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    is_active = Column(Boolean, default=True)
    is_checked_out = Column(Boolean, default=False)
    total_amount = Column(Float, default=0.0)
    items = relationship("OrderItem", back_populates="order")

class MenuItem(Base):
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, default=0.0)
    image_url = Column(String, nullable=True)
    is_available = Column(Boolean, default=True)

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class MenuItemCreate(BaseModel):
    name: str
    category: str
    price: float = 0.0
    image_url: Optional[str] = None
    is_available: bool = True

class MenuItemResponse(BaseModel):
    id: int
    name: str
    category: str
    price: float
    image_url: Optional[str]
    is_available: bool
    
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    table_number: Optional[str] = None

class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = 1

class OrderItemResponse(BaseModel):
    id: int
    menu_item_id: int
    quantity: int
    created_at: datetime
    menu_item: MenuItemResponse
    
    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    table_number: Optional[str]
    start_time: datetime
    end_time: datetime
    is_active: bool
    is_checked_out: bool
    total_amount: float
    items: List[OrderItemResponse]
    remaining_seconds: int
    
    class Config:
        from_attributes = True

# FastAPI app
app = FastAPI(title="Buffet Ordering System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function
def calculate_remaining_time(order: Order) -> int:
    if not order.is_active or order.is_checked_out:
        return 0
    now = datetime.utcnow()
    elapsed = (now - order.start_time).total_seconds()
    remaining = (105 * 60) - elapsed  # 105 minutes = 6300 seconds
    return max(0, int(remaining))

def check_and_expire_order(order: Order, db: Session):
    if order.is_active and not order.is_checked_out:
        remaining = calculate_remaining_time(order)
        if remaining <= 0:
            order.is_active = False
            db.commit()
            return False
    return order.is_active and not order.is_checked_out

# API Endpoints
@app.get("/")
def read_root():
    return {"message": "Buffet Ordering System API", "version": "1.0"}

@app.post("/api/orders/start", response_model=OrderResponse)
def start_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """สร้างออเดอร์ใหม่และเริ่มจับเวลา 1 ชม 45 นาที"""
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(minutes=105)
    
    new_order = Order(
        table_number=order_data.table_number,
        start_time=start_time,
        end_time=end_time,
        is_active=True,
        is_checked_out=False
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    return {
        **new_order.__dict__,
        "items": [],
        "remaining_seconds": 6300  # 105 minutes
    }

@app.get("/api/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """ดึงข้อมูลออเดอร์"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if order has expired
    check_and_expire_order(order, db)
    
    remaining = calculate_remaining_time(order)
    
    return {
        **order.__dict__,
        "remaining_seconds": remaining
    }

@app.post("/api/orders/{order_id}/items", response_model=OrderItemResponse)
def add_order_item(order_id: int, item_data: OrderItemCreate, db: Session = Depends(get_db)):
    """เพิ่มรายการอาหารในออเดอร์"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if order is still active
    if not check_and_expire_order(order, db):
        raise HTTPException(status_code=400, detail="Order has expired or been checked out")
    
    # Check if menu item exists
    menu_item = db.query(MenuItem).filter(MenuItem.id == item_data.menu_item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    if not menu_item.is_available:
        raise HTTPException(status_code=400, detail="Menu item is not available")
    
    # Create order item
    order_item = OrderItem(
        order_id=order_id,
        menu_item_id=item_data.menu_item_id,
        quantity=item_data.quantity
    )
    db.add(order_item)
    
    # Update total amount
    order.total_amount += menu_item.price * item_data.quantity
    
    db.commit()
    db.refresh(order_item)
    
    return order_item

@app.post("/api/orders/{order_id}/checkout")
def checkout_order(order_id: int, db: Session = Depends(get_db)):
    """เช็คบิลและปิดการรับออเดอร์"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.is_checked_out:
        raise HTTPException(status_code=400, detail="Order already checked out")
    
    order.is_checked_out = True
    order.is_active = False
    db.commit()
    
    return {
        "message": "Order checked out successfully",
        "order_id": order_id,
        "total_amount": order.total_amount
    }

@app.get("/api/menu", response_model=List[MenuItemResponse])
def get_menu(db: Session = Depends(get_db)):
    """ดึงรายการเมนูอาหารทั้งหมด"""
    menu_items = db.query(MenuItem).filter(MenuItem.is_available == True).all()
    return menu_items

@app.post("/api/menu", response_model=MenuItemResponse)
def create_menu_item(item_data: MenuItemCreate, db: Session = Depends(get_db)):
    """เพิ่มเมนูอาหารใหม่"""
    menu_item = MenuItem(**item_data.dict())
    db.add(menu_item)
    db.commit()
    db.refresh(menu_item)
    return menu_item

@app.put("/api/menu/{item_id}", response_model=MenuItemResponse)
def update_menu_item(item_id: int, item_data: MenuItemCreate, db: Session = Depends(get_db)):
    """แก้ไขเมนูอาหาร"""
    menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    for key, value in item_data.dict().items():
        setattr(menu_item, key, value)
    
    db.commit()
    db.refresh(menu_item)
    return menu_item

@app.delete("/api/menu/{item_id}")
def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    """ลบเมนูอาหาร"""
    menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    menu_item.is_available = False
    db.commit()
    return {"message": "Menu item deleted successfully"}

# Seed data
@app.post("/api/seed")
def seed_data(db: Session = Depends(get_db)):
    """สร้างข้อมูลตัวอย่าง"""
    # Check if data already exists
    if db.query(MenuItem).count() > 0:
        return {"message": "Data already exists"}
    
    menu_items = [
        MenuItem(name="ข้าวผัด", category="อาหารจานหลัก", price=0, image_url="https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=400"),
        MenuItem(name="ผัดไทย", category="อาหารจานหลัก", price=0, image_url="https://images.unsplash.com/photo-1559314809-0d155014e29e?w=400"),
        MenuItem(name="ส้มตำ", category="อาหารจานหลัก", price=0, image_url="https://images.unsplash.com/photo-1559847844-d3c037269e93?w=400"),
        MenuItem(name="ไก่ทอด", category="อาหารจานหลัก", price=0, image_url="https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=400"),
        MenuItem(name="ปลาทอด", category="อาหารจานหลัก", price=0, image_url="https://images.unsplash.com/photo-1534604973900-c43ab4c2e0ab?w=400"),
        MenuItem(name="ยำวุ้นเส้น", category="ยำ", price=0, image_url="https://images.unsplash.com/photo-1559847844-56910d405dad?w=400"),
        MenuItem(name="ต้มยำกุ้ง", category="ต้ม", price=0, image_url="https://images.unsplash.com/photo-1548943487-a2e4e43b4853?w=400"),
        MenuItem(name="น้ำอัดลม", category="เครื่องดื่ม", price=0, image_url="https://images.unsplash.com/photo-1581006852262-e4307cf6283a?w=400"),
        MenuItem(name="น้ำผลไม้", category="เครื่องดื่ม", price=0, image_url="https://images.unsplash.com/photo-1546173159-315724a31696?w=400"),
        MenuItem(name="ไอศกรีม", category="ของหวาน", price=0, image_url="https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400"),
    ]
    
    db.add_all(menu_items)
    db.commit()
    
    return {"message": "Seed data created successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
