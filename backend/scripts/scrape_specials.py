"""
Script to scrape grocery store specials and update database
Can be run manually or scheduled as a cron job
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.grocery import GroceryStore, GrocerySpecial
from app.services.scraper_service import grocery_scraper

def scrape_and_save_specials():
    """Scrape specials from all stores and save to database"""
    db = SessionLocal()
    
    try:
        # Get all specials
        all_specials = grocery_scraper.scrape_all_stores()
        
        # Get store mappings
        stores = {store.code: store for store in db.query(GroceryStore).all()}
        
        total_saved = 0
        
        for store_code, specials in all_specials.items():
            if store_code not in stores:
                print(f"Warning: Store {store_code} not found in database")
                continue
            
            store = stores[store_code]
            
            for special_data in specials:
                # Check if special already exists
                existing = db.query(GrocerySpecial).filter(
                    GrocerySpecial.store_id == store.id,
                    GrocerySpecial.product_name == special_data['product_name'],
                    GrocerySpecial.valid_from == special_data['valid_from'],
                    GrocerySpecial.valid_until == special_data['valid_until']
                ).first()
                
                if existing:
                    # Update existing special
                    existing.special_price = special_data['special_price']
                    existing.discount_percentage = special_data.get('discount_percentage')
                    existing.description = special_data.get('description')
                else:
                    # Create new special
                    special = GrocerySpecial(
                        store_id=store.id,
                        product_name=special_data['product_name'],
                        product_category=special_data.get('product_category'),
                        original_price=special_data.get('original_price'),
                        special_price=special_data['special_price'],
                        discount_percentage=special_data.get('discount_percentage'),
                        unit=special_data.get('unit'),
                        description=special_data.get('description'),
                        valid_from=special_data['valid_from'],
                        valid_until=special_data['valid_until']
                    )
                    db.add(special)
                    total_saved += 1
            
            db.commit()
            print(f"Processed {len(specials)} specials from {store.name}")
        
        print(f"Total new specials saved: {total_saved}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting grocery specials scraper...")
    scrape_and_save_specials()
    print("Done!")
