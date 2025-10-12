"""
Grocery specials API routes
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from app.core.database import get_db
from app.models.grocery import GroceryStore, GrocerySpecial

router = APIRouter()

class GroceryStoreResponse(BaseModel):
    """Grocery store response"""
    id: str
    name: str
    code: str
    
    class Config:
        from_attributes = True

class GrocerySpecialResponse(BaseModel):
    """Grocery special response"""
    id: str
    store_name: str
    product_name: str
    product_category: Optional[str]
    original_price: Optional[float]
    special_price: float
    discount_percentage: Optional[float]
    unit: Optional[str]
    description: Optional[str]
    valid_from: date
    valid_until: date
    
    class Config:
        from_attributes = True

@router.get("/stores", response_model=List[GroceryStoreResponse])
async def list_stores(db: Session = Depends(get_db)):
    """
    List all grocery stores
    """
    stores = db.query(GroceryStore).all()
    return [
        GroceryStoreResponse(
            id=str(store.id),
            name=store.name,
            code=store.code
        )
        for store in stores
    ]

@router.get("/specials", response_model=List[GrocerySpecialResponse])
async def list_specials(
    store_code: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List current grocery specials with filtering
    """
    query = db.query(GrocerySpecial, GroceryStore).join(
        GroceryStore, GrocerySpecial.store_id == GroceryStore.id
    ).filter(
        GrocerySpecial.valid_from <= date.today(),
        GrocerySpecial.valid_until >= date.today()
    )
    
    if store_code:
        query = query.filter(GroceryStore.code == store_code)
    if category:
        query = query.filter(GrocerySpecial.product_category == category)
    if search:
        query = query.filter(GrocerySpecial.product_name.ilike(f"%{search}%"))
    
    results = query.order_by(GrocerySpecial.discount_percentage.desc()).offset(skip).limit(limit).all()
    
    return [
        GrocerySpecialResponse(
            id=str(special.id),
            store_name=store.name,
            product_name=special.product_name,
            product_category=special.product_category,
            original_price=float(special.original_price) if special.original_price else None,
            special_price=float(special.special_price),
            discount_percentage=float(special.discount_percentage) if special.discount_percentage else None,
            unit=special.unit,
            description=special.description,
            valid_from=special.valid_from,
            valid_until=special.valid_until
        )
        for special, store in results
    ]
