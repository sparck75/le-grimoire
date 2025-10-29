# AI Extraction Tracking System

## Overview

Complete tracking and traceability system for AI-powered recipe extractions with usage statistics, cost monitoring, and audit trails.

## Features

### Automatic Tracking

Every AI extraction is automatically logged with:
- **Image Information**: Path, URL, size in bytes
- **Extraction Metadata**: Method (AI/OCR/fallback), provider, model name
- **Recipe Information**: Title, ID (when saved), confidence score
- **Performance Metrics**: Processing time (ms), success/failure status
- **Cost Data**: Token usage (prompt, completion, total), estimated cost (USD)
- **Debugging Data**: Raw response, model metadata, error messages
- **User Information**: User ID, email (ready for auth integration)
- **Timestamps**: Creation time (UTC)

### Cost Calculation

Automatic cost estimation based on provider pricing:
- **GPT-4o**: $2.50 per 1M input tokens, $10 per 1M output tokens
- **Tesseract**: $0 (free)
- **Future providers**: Easy to add pricing

### Database Model

**Collection**: `ai_extraction_logs`

```python
{
  "_id": ObjectId,
  "extraction_method": "ai" | "ocr" | "ocr_fallback",
  "provider": "openai" | "tesseract" | "gemini",
  "model_name": "gpt-4o",
  "user_id": Optional[str],
  "user_email": Optional[str],
  "original_image_path": "/app/uploads/...",
  "image_url": "/uploads/...",
  "image_size_bytes": 2048576,
  "recipe_id": Optional[str],
  "recipe_title": "Tomates vertes frites",
  "confidence_score": 0.92,
  "success": true,
  "error_message": Optional[str],
  "prompt_tokens": 1245,
  "completion_tokens": 602,
  "total_tokens": 1847,
  "estimated_cost_usd": 0.0425,
  "processing_time_ms": 3250,
  "raw_response": "...",
  "model_metadata": {...},
  "created_at": ISODate("2025-01-29T14:30:25Z")
}
```

**Indexes**: `extraction_method`, `provider`, `user_id`, `recipe_id`, `created_at`, `success`

## API Endpoints

### Statistics

**GET `/api/admin/ai/stats`**

Query Parameters:
- `days`: Period for analysis (default: 30)
- `provider`: Filter by provider (optional)

Response:
```json
{
  "period": {
    "days": 30,
    "start_date": "2025-01-01T00:00:00Z",
    "end_date": "2025-01-30T00:00:00Z"
  },
  "summary": {
    "total_extractions": 150,
    "successful": 145,
    "failed": 5,
    "success_rate": 96.67,
    "average_confidence": 0.89,
    "average_processing_time_ms": 3250
  },
  "by_provider": {
    "openai": {
      "count": 100,
      "successful": 98,
      "failed": 2,
      "total_tokens": 185000,
      "total_cost_usd": 4.25
    },
    "tesseract": {
      "count": 50,
      "successful": 47,
      "failed": 3,
      "total_tokens": 0,
      "total_cost_usd": 0
    }
  },
  "tokens": {
    "total": 185000,
    "prompt": 124500,
    "completion": 60500,
    "ai_extractions": 100
  },
  "costs": {
    "total_usd": 4.25,
    "average_per_extraction_usd": 0.0425,
    "by_provider": {
      "openai": 4.25,
      "tesseract": 0
    }
  },
  "daily_breakdown": [
    {
      "date": "2025-01-29",
      "total": 25,
      "successful": 24,
      "failed": 1,
      "cost_usd": 1.05
    }
  ]
}
```

### Extraction Logs

**GET `/api/admin/ai/logs`**

Query Parameters:
- `limit`: Max results (1-500, default: 50)
- `skip`: Pagination offset (default: 0)
- `success_only`: Filter by success (true/false/null for all)
- `provider`: Filter by provider (openai/tesseract/etc.)

Response:
```json
[
  {
    "id": "507f1f77bcf86cd799439011",
    "extraction_method": "ai",
    "provider": "openai",
    "model_name": "gpt-4o",
    "recipe_title": "Tomates vertes frites",
    "recipe_id": "507f1f77bcf86cd799439012",
    "confidence_score": 0.92,
    "success": true,
    "error_message": null,
    "total_tokens": 1847,
    "estimated_cost_usd": 0.0425,
    "processing_time_ms": 3250,
    "image_url": "/uploads/abc123_recipe.jpg",
    "created_at": "2025-01-29T14:30:25Z"
  }
]
```

## Admin UI

### Statistics Dashboard

**URL**: `/admin/ai/stats`

**Access**: Admin only

**Features**:
1. **Period Selector**: 7, 30, 90, 365 days
2. **Summary Cards**: 
   - Total extractions with success/failure counts
   - Success rate with average confidence
   - Total cost with per-extraction average
   - Tokens used with AI extraction count
3. **Provider Comparison**: Cards showing stats per provider
4. **Daily Breakdown**: Table showing last 7 days trend
5. **Recent Extractions**: Paginated table with filters

**Filters**:
- Provider: All, OpenAI, Tesseract
- Success Status: All, Successful only, Failed only
- Limit: 25, 50, 100 entries

**Table Columns**:
- Date/time (French locale)
- Recipe title with link to recipe
- Method (provider + model)
- Confidence score (%)
- Tokens used
- Cost (USD to 4 decimals)
- Processing time (seconds)
- Status (success/failure with error tooltip)

## Use Cases

### Cost Monitoring

Track AI costs in real-time:
- View total costs per period
- Average cost per extraction
- Cost breakdown by provider
- Daily cost trends
- Set budgets and alerts (future)

### Performance Analysis

Monitor extraction quality:
- Success rates over time
- Average confidence scores
- Processing time trends
- Error patterns
- Provider comparison

### Debugging

Troubleshoot failed extractions:
- View error messages
- Access raw response data
- Check model metadata
- Analyze failure patterns
- Identify problematic images

### Audit Trail

Complete traceability:
- When extraction performed
- Who performed it (when auth enabled)
- What image was used
- Which model/provider used
- What recipe was created
- Cost incurred
- Success/failure status

### User Analytics

Per-user tracking (ready for auth):
- Extractions per user
- Costs per user
- Success rates per user
- Usage patterns
- Quota management (future)

## Image Preservation

Original images are preserved:
- Saved to disk at upload
- Path stored in extraction log
- URL stored for frontend access
- Linked to created recipe
- Available for re-processing
- Included in backups

## Data Retention

Current policy:
- All extraction logs kept permanently
- No automatic cleanup
- Admins can implement custom retention policies
- Useful for historical analysis and trends

Recommended retention:
- Keep detailed logs: 90 days
- Keep aggregated stats: Forever
- Archive old images: After 1 year

## Security & Privacy

**Access Control**:
- Statistics API: Admin only
- Logs API: Admin only
- Frontend dashboard: Admin only
- No user-accessible logs (prevents data leakage)

**Data Privacy**:
- User IDs/emails stored (ready for auth)
- Image paths not exposed to non-admins
- API keys never logged
- Raw responses contain no sensitive data

**GDPR Compliance** (when users added):
- Ability to export user's extractions
- Ability to delete user's data
- Anonymization options
- Clear data usage policies

## Integration Points

### Recipe Creation

When a recipe is saved:
1. Get extraction data from sessionStorage
2. Create recipe via API
3. Update extraction log with recipe_id:
   ```python
   await AIExtractionLog.find_one(
       {"image_url": extraction_data["image_url"]}
   ).update({"$set": {"recipe_id": recipe_id}})
   ```

### User Authentication (Future)

When auth is implemented:
1. Add user_id and user_email to extraction logs
2. Filter stats/logs by user
3. Show per-user usage in profile
4. Implement user quotas if needed

### Backup System

Extraction logs should be included in backups:
1. MongoDB backup includes `ai_extraction_logs` collection
2. Uploaded images backed up separately
3. Restore process restores both
4. Test restore procedures regularly

## Performance Considerations

**Database Queries**:
- Indexed fields for fast filtering
- Pagination for large result sets
- Aggregation pipelines for statistics
- Caching for frequently accessed data (future)

**Optimization Tips**:
- Query specific date ranges
- Use indexes effectively
- Limit result sets
- Archive old data periodically

## Future Enhancements

### Planned Features

1. **Charts & Visualizations**
   - Line charts for cost trends
   - Bar charts for provider comparison
   - Pie charts for method distribution
   - Success rate trends

2. **Cost Alerts**
   - Email notifications on threshold
   - Daily/weekly cost summaries
   - Budget warnings
   - Unusual spending alerts

3. **Export Functionality**
   - CSV export of logs
   - PDF reports
   - Excel format for analysis
   - Scheduled email reports

4. **Advanced Analytics**
   - Prediction of future costs
   - Anomaly detection
   - Performance recommendations
   - A/B testing results

5. **Per-User Tracking**
   - User-specific dashboards
   - Usage quotas
   - Cost allocation
   - Activity logs

6. **Data Retention Policies**
   - Automatic archival
   - Configurable retention periods
   - Storage optimization
   - Legal compliance

## Troubleshooting

### No Data Showing

Check:
1. MongoDB connection working
2. Extractions being performed
3. Date range includes recent data
4. Filters not too restrictive

### Cost Calculation Wrong

Verify:
1. Token counts in logs
2. Pricing constants in code
3. Model names match pricing
4. Currency conversion if needed

### Performance Issues

Solutions:
1. Add more indexes
2. Reduce result set size
3. Implement caching
4. Archive old data

## Summary

The AI tracking system provides:
- ✅ Complete audit trail for all extractions
- ✅ Real-time cost monitoring and budgeting
- ✅ Performance analytics and insights
- ✅ Debugging support with full context
- ✅ Image preservation and traceability
- ✅ Ready for per-user tracking
- ✅ Extensible for future features
- ✅ GDPR compliance ready
- ✅ Admin-friendly dashboard
- ✅ Secure and privacy-conscious

This comprehensive tracking system ensures full transparency and control over AI usage while providing valuable insights for optimization and cost management.
