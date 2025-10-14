"""
Shopping lists API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from app.core.database import get_db
from app.models.shopping_list import ShoppingList, ShoppingListItem
from app.models.mongodb import Ingredient  # MongoDB ingredient model
import uuid

router = APIRouter()

# Request/Response Models
class ShoppingListItemCreate(BaseModel):
    """Create shopping list item"""
    ingredient_off_id: Optional[str] = None  # OpenFoodFacts ID like "en:tomato"
    ingredient_name: str  # Required for custom items or display
    quantity: Optional[float] = None
    unit: Optional[str] = None
    recipe_id: Optional[str] = None
    notes: Optional[str] = None

class ShoppingListItemResponse(BaseModel):
    """Shopping list item response"""
    id: str
    ingredient_off_id: Optional[str] = None
    ingredient_name: str
    ingredient_name_en: Optional[str] = None  # English name from MongoDB
    ingredient_name_fr: Optional[str] = None  # French name from MongoDB
    quantity: Optional[float] = None
    unit: Optional[str] = None
    is_purchased: bool
    recipe_id: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True

class ShoppingListCreate(BaseModel):
    """Create shopping list"""
    name: str
    items: Optional[List[ShoppingListItemCreate]] = []

class ShoppingListResponse(BaseModel):
    """Shopping list response"""
    id: str
    name: str
    items_count: int
    items: Optional[List[ShoppingListItemResponse]] = None
    
    class Config:
        from_attributes = True

class ShoppingListUpdate(BaseModel):
    """Update shopping list"""
    name: Optional[str] = None

# Endpoints
@router.get("/", response_model=List[ShoppingListResponse])
async def list_shopping_lists(db: Session = Depends(get_db)):
    """
    List user's shopping lists
    Requires authentication in production
    """
    # This would filter by authenticated user in production
    lists = db.query(ShoppingList).all()
    
    result = []
    for shopping_list in lists:
        items = db.query(ShoppingListItem).filter(
            ShoppingListItem.shopping_list_id == shopping_list.id
        ).all()
        
        result.append(ShoppingListResponse(
            id=str(shopping_list.id),
            name=shopping_list.name,
            items_count=len(items)
        ))
    
    return result

@router.post("/", response_model=ShoppingListResponse)
async def create_shopping_list(
    shopping_list_data: ShoppingListCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new shopping list with items
    Validates ingredients against MongoDB if ingredient_off_id provided
    """
    # Create shopping list
    shopping_list = ShoppingList(
        name=shopping_list_data.name,
        user_id=uuid.uuid4()  # TODO: Replace with authenticated user
    )
    db.add(shopping_list)
    db.flush()
    
    # Create items
    items_response = []
    for item_data in shopping_list_data.items:
        # Validate ingredient if off_id provided
        ingredient = None
        if item_data.ingredient_off_id:
            ingredient = await Ingredient.find_one({"off_id": item_data.ingredient_off_id})
            if not ingredient:
                raise HTTPException(
                    status_code=400,
                    detail=f"Ingredient {item_data.ingredient_off_id} not found in database"
                )
        
        # Create item
        item = ShoppingListItem(
            shopping_list_id=shopping_list.id,
            ingredient_off_id=item_data.ingredient_off_id,
            ingredient_name=item_data.ingredient_name,
            quantity=Decimal(str(item_data.quantity)) if item_data.quantity else None,
            unit=item_data.unit,
            recipe_id=uuid.UUID(item_data.recipe_id) if item_data.recipe_id else None,
            notes=item_data.notes
        )
        db.add(item)
        db.flush()
        
        # Build response with multilingual names
        items_response.append(ShoppingListItemResponse(
            id=str(item.id),
            ingredient_off_id=item.ingredient_off_id,
            ingredient_name=item.ingredient_name,
            ingredient_name_en=ingredient.get_name("en") if ingredient else None,
            ingredient_name_fr=ingredient.get_name("fr") if ingredient else None,
            quantity=float(item.quantity) if item.quantity else None,
            unit=item.unit,
            is_purchased=item.is_purchased,
            recipe_id=str(item.recipe_id) if item.recipe_id else None,
            notes=item.notes
        ))
    
    db.commit()
    
    return ShoppingListResponse(
        id=str(shopping_list.id),
        name=shopping_list.name,
        items_count=len(items_response),
        items=items_response
    )

@router.get("/{list_id}", response_model=ShoppingListResponse)
async def get_shopping_list(list_id: str, db: Session = Depends(get_db)):
    """
    Get shopping list with items and multilingual ingredient names
    """
    shopping_list = db.query(ShoppingList).filter(
        ShoppingList.id == uuid.UUID(list_id)
    ).first()
    
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    
    items = db.query(ShoppingListItem).filter(
        ShoppingListItem.shopping_list_id == shopping_list.id
    ).all()
    
    # Fetch ingredient data from MongoDB for multilingual names
    items_response = []
    for item in items:
        ingredient = None
        if item.ingredient_off_id:
            ingredient = await Ingredient.find_one({"off_id": item.ingredient_off_id})
        
        items_response.append(ShoppingListItemResponse(
            id=str(item.id),
            ingredient_off_id=item.ingredient_off_id,
            ingredient_name=item.ingredient_name,
            ingredient_name_en=ingredient.get_name("en") if ingredient else None,
            ingredient_name_fr=ingredient.get_name("fr") if ingredient else None,
            quantity=float(item.quantity) if item.quantity else None,
            unit=item.unit,
            is_purchased=item.is_purchased,
            recipe_id=str(item.recipe_id) if item.recipe_id else None,
            notes=item.notes
        ))
    
    return ShoppingListResponse(
        id=str(shopping_list.id),
        name=shopping_list.name,
        items_count=len(items_response),
        items=items_response
    )

@router.put("/{list_id}", response_model=ShoppingListResponse)
async def update_shopping_list(
    list_id: str,
    update_data: ShoppingListUpdate,
    db: Session = Depends(get_db)
):
    """
    Update shopping list name
    """
    shopping_list = db.query(ShoppingList).filter(
        ShoppingList.id == uuid.UUID(list_id)
    ).first()
    
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    
    if update_data.name:
        shopping_list.name = update_data.name
    
    db.commit()
    
    items = db.query(ShoppingListItem).filter(
        ShoppingListItem.shopping_list_id == shopping_list.id
    ).all()
    
    return ShoppingListResponse(
        id=str(shopping_list.id),
        name=shopping_list.name,
        items_count=len(items)
    )

@router.delete("/{list_id}")
async def delete_shopping_list(list_id: str, db: Session = Depends(get_db)):
    """
    Delete shopping list and all its items (cascades automatically)
    """
    shopping_list = db.query(ShoppingList).filter(
        ShoppingList.id == uuid.UUID(list_id)
    ).first()
    
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    
    db.delete(shopping_list)
    db.commit()
    
    return {"message": "Shopping list deleted successfully"}

@router.post("/{list_id}/items", response_model=ShoppingListItemResponse)
async def add_item_to_list(
    list_id: str,
    item_data: ShoppingListItemCreate,
    db: Session = Depends(get_db)
):
    """
    Add item to existing shopping list
    Validates ingredient against MongoDB if ingredient_off_id provided
    """
    shopping_list = db.query(ShoppingList).filter(
        ShoppingList.id == uuid.UUID(list_id)
    ).first()
    
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    
    # Validate ingredient if off_id provided
    ingredient = None
    if item_data.ingredient_off_id:
        ingredient = await Ingredient.find_one({"off_id": item_data.ingredient_off_id})
        if not ingredient:
            raise HTTPException(
                status_code=400,
                detail=f"Ingredient {item_data.ingredient_off_id} not found in database"
            )
    
    # Create item
    item = ShoppingListItem(
        shopping_list_id=shopping_list.id,
        ingredient_off_id=item_data.ingredient_off_id,
        ingredient_name=item_data.ingredient_name,
        quantity=Decimal(str(item_data.quantity)) if item_data.quantity else None,
        unit=item_data.unit,
        recipe_id=uuid.UUID(item_data.recipe_id) if item_data.recipe_id else None,
        notes=item_data.notes
    )
    db.add(item)
    db.commit()
    
    return ShoppingListItemResponse(
        id=str(item.id),
        ingredient_off_id=item.ingredient_off_id,
        ingredient_name=item.ingredient_name,
        ingredient_name_en=ingredient.get_name("en") if ingredient else None,
        ingredient_name_fr=ingredient.get_name("fr") if ingredient else None,
        quantity=float(item.quantity) if item.quantity else None,
        unit=item.unit,
        is_purchased=item.is_purchased,
        recipe_id=str(item.recipe_id) if item.recipe_id else None,
        notes=item.notes
    )

@router.patch("/{list_id}/items/{item_id}/purchase")
async def toggle_item_purchased(
    list_id: str,
    item_id: str,
    db: Session = Depends(get_db)
):
    """
    Toggle item purchased status
    """
    item = db.query(ShoppingListItem).filter(
        ShoppingListItem.id == uuid.UUID(item_id),
        ShoppingListItem.shopping_list_id == uuid.UUID(list_id)
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item.is_purchased = not item.is_purchased
    db.commit()
    
    return {"message": "Item updated", "is_purchased": item.is_purchased}

@router.delete("/{list_id}/items/{item_id}")
async def delete_item_from_list(
    list_id: str,
    item_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete item from shopping list
    """
    item = db.query(ShoppingListItem).filter(
        ShoppingListItem.id == uuid.UUID(item_id),
        ShoppingListItem.shopping_list_id == uuid.UUID(list_id)
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(item)
    db.commit()
    
    return {"message": "Item deleted successfully"}

@router.post("/generate")
async def generate_shopping_list(recipe_ids: List[str], db: Session = Depends(get_db)):
    """
    Generate shopping list from recipes with matched grocery specials
    Requires authentication in production
    """
    return {
        "message": "Shopping list generation - to be implemented",
        "recipe_ids": recipe_ids
    }
