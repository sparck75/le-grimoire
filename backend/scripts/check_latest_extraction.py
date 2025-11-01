import asyncio
import sys
sys.path.insert(0, '/app')

from app.core.database import init_mongodb
from app.models.mongodb import AIExtractionLog


async def check_extraction():
    await init_mongodb()
    
    # Get latest wine extraction
    log = await AIExtractionLog.find(
        {'extraction_type': 'wine'}
    ).sort('-created_at').first_or_none()
    
    if log:
        print(f'Latest wine extraction: {log.created_at}')
        print(f'Success: {log.success}')
        print(f'Provider: {log.provider}/{log.model_name}')
        print(f'Tokens: {log.total_tokens}')
        print(f'Confidence: {log.confidence_score}')
        print(f'\nModel metadata:')
        if log.model_metadata:
            for key, value in log.model_metadata.items():
                print(f'  {key}: {value}')
        
        # Check all fields in log
        log_dict = log.model_dump()
        print(f'\nAll available fields: {list(log_dict.keys())}')
        
        if 'extracted_data' in log_dict:
            extracted = log_dict['extracted_data']
            print(f'\nExtracted data keys: {list(extracted.keys())}')
            if 'suggested_lwin7' in extracted:
                print(f'✅ LWIN7: {extracted["suggested_lwin7"]}')
            else:
                print('❌ No suggested_lwin7 in extracted data')
            if 'name' in extracted:
                print(f'Name: {extracted["name"]}')
            if 'producer' in extracted:
                print(f'Producer: {extracted["producer"]}')
        else:
            print('\n❌ No extracted_data field found in log')
    else:
        print('No wine extractions found')


asyncio.run(check_extraction())
