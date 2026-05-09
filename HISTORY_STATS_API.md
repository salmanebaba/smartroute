# SmartRoute Backend API - History & Statistics Implementation

## Overview

The backend has been enhanced to provide real-time history tracking and statistical analysis of bin collection operations. The system now connects static frontend data to live Cosmos DB telemetry data.

---

## Architecture Changes

### 1. **Data Layer** (`backend/app/data/cosmos_client.py`)
Added methods to retrieve historical telemetry data from Azure Cosmos DB:

- `get_bin_fill_history(bin_id, days)` - Get fill level history for a specific bin
- `get_all_telemetry_records(days)` - Retrieve all telemetry records
- `get_daily_statistics(days)` - Aggregate daily statistics from telemetry

### 2. **Service Layer** (`backend/app/services/history_service.py`)
New service for business logic:

- `get_collection_history(range_days)` - Get historical collection statistics
- `get_bin_history(bin_id, days)` - Retrieve bin-specific history
- `get_trend_analysis(range_days)` - Analyze collection trends

### 3. **Data Models** (`backend/app/models/schemas.py`)
New Pydantic schemas for responses:

- `DailyStatistics` - Daily aggregated metrics
- `CollectionHistory` - Period collection data with daily breakdown
- `BinHistoryData` - Individual bin telemetry records

### 4. **API Routes** (`backend/app/routes/router.py`)
New endpoints added:

#### Statistics & History
- `GET /bins/statistics/history?range=7d|30d|90d` - Collection history
- `GET /statistics/trends?range=7d|30d|90d` - Trend analysis
- `GET /bins/{bin_id}/history?days=7` - Bin-specific history

---

## API Endpoints

### Get Collection History
```
GET /bins/statistics/history?range=7d
```

**Query Parameters:**
- `range` (string): Time range - `7d`, `30d`, or `90d` (default: `7d`)

**Response (200 OK):**
```json
{
  "range": "7d",
  "total_collections": 42,
  "average_daily_collections": 6.0,
  "peak_day": "2026-05-08",
  "daily_data": [
    {
      "date": "2026-05-09",
      "average_fill_level": 58.2,
      "bins_collected": 6,
      "urgent_count": 3,
      "peak_fill_level": 98
    },
    {
      "date": "2026-05-08",
      "average_fill_level": 62.5,
      "bins_collected": 5,
      "urgent_count": 2,
      "peak_fill_level": 95
    }
  ]
}
```

### Get Trend Analysis
```
GET /statistics/trends?range=7d
```

**Query Parameters:**
- `range` (string): Time range - `7d`, `30d`, or `90d` (default: `7d`)

**Response (200 OK):**
```json
{
  "trend": "increasing",
  "peak_day": "2026-05-08",
  "average_urgency": 2.5,
  "total_days_analyzed": 7,
  "total_collections": 42
}
```

**Trend Values:**
- `increasing` - Collection demand is rising
- `decreasing` - Collection demand is falling
- `stable` - Collection demand is consistent
- `insufficient_data` - Not enough data for analysis

### Get Bin History
```
GET /bins/{bin_id}/history?days=7
```

**Path Parameters:**
- `bin_id` (string): The bin identifier (e.g., `bin_001`)

**Query Parameters:**
- `days` (integer): Number of days to retrieve (1-90, default: 7)

**Response (200 OK):**
```json
[
  {
    "bin_id": "bin_001",
    "timestamp": "2026-05-09T12:00:00Z",
    "fill_level": 92
  },
  {
    "bin_id": "bin_001",
    "timestamp": "2026-05-08T18:00:00Z",
    "fill_level": 75
  }
]
```

---

## Frontend Integration

### Updated Components

**ManagerView.jsx:**
- Now uses `transformHistory()` to convert backend response to chart format
- Calls `/bins/statistics/history?range=7d` on component mount
- Falls back to mock data if API fails

**api.js:**
- Added `transformHistory()` function to normalize backend response
- Maps backend `CollectionHistory` format to frontend chart format
- Handles timestamp transformation for day display

### Data Flow
```
Frontend (ManagerView)
    ↓
apiFetch('/bins/statistics/history?range=7d')
    ↓
Backend Router
    ↓
HistoryService.get_collection_history()
    ↓
CosmosDataClient.get_daily_statistics()
    ↓
Azure Cosmos DB (Telemetry Container)
    ↓
Processed Response
    ↓
transformHistory() (Frontend)
    ↓
HistoryChart Component (Recharts)
```

---

## Data Processing Logic

### Fill Level Estimation
- **Bins Collected**: Bins with fill_level > 50%
- **Urgent Count**: Bins with fill_level > 85%
- **Average Fill Level**: Mean of all fill levels

### Trend Analysis
- Compares last 3 days vs. previous 3 days
- Calculates percentage change
- Classifies as: increasing (>10%), decreasing (<-10%), or stable

### Daily Statistics
- Aggregates fill level data by calendar day
- Groups by deviceId
- Calculates max, min, and average per day

---

## Backend Dependencies

### Required Packages
```
fastapi>=0.95.0
pydantic>=1.10.0
azure-cosmos>=4.3.0
python-dotenv
```

### Environment Variables
```
COSMOS_URI=<your-cosmos-db-uri>
COSMOS_KEY=<your-cosmos-db-key>
DATABASE_NAME=SmartBinDB
TELEMETRY_CONTAINER=Telemetry
INVENTORY_CONTAINER=BinsInventory
```

---

## Cosmos DB Schema Requirements

### Telemetry Container
Required fields for telemetry documents:
```json
{
  "id": "unique-uuid",
  "deviceId": "bin_001",
  "type": "fill_level_update",
  "timestamp": "2026-05-09T12:00:00Z",
  "fill_level": 92,
  "_ts": 1715258400
}
```

### Inventory Container
Required fields for bin inventory:
```json
{
  "id": "bin_001",
  "location": {
    "lat": 33.9810,
    "lng": -6.8690
  },
  "_ts": 1715258400
}
```

---

## Error Handling

### HTTP Status Codes
- `200 OK` - Successful response
- `404 Not Found` - Bin ID not found
- `500 Internal Server Error` - Database or processing error

### Fallback Behavior

**Frontend:**
- Falls back to `generateMockHistory()` if API returns null
- Displays "Loading history…" while fetching
- Continues operation with mock data

**Backend:**
- Returns empty `CollectionHistory` if query fails
- Logs warnings for individual record failures
- Returns `[]` for bin history queries with errors

---

## Performance Considerations

1. **Query Limits**: Telemetry queries limited to 10,000 records
2. **Time Window**: 7/30/90 day ranges to optimize query performance
3. **Caching**: Consider implementing Redis for frequently accessed history
4. **Aggregation**: Daily aggregation reduces data complexity

---

## Testing

### Manual API Tests

```bash
# Get weekly history
curl http://localhost:8000/bins/statistics/history?range=7d

# Get trends
curl http://localhost:8000/statistics/trends?range=30d

# Get specific bin history
curl http://localhost:8000/bins/bin_001/history?days=14
```

### Frontend Testing
1. Start backend: `python -m uvicorn app.main:app --reload`
2. Start frontend: `npm run dev` in frontend directory
3. Verify ManagerView loads history chart
4. Check browser console for API responses

---

## Future Enhancements

- [ ] Implement real-time WebSocket updates for live data
- [ ] Add data export (CSV/PDF) functionality
- [ ] Implement predictive analytics for collection scheduling
- [ ] Add benchmarking against historical averages
- [ ] Create admin dashboard for data analysis
- [ ] Implement caching layer for performance optimization

---

## Troubleshooting

### History not loading
1. Check Cosmos DB connection credentials
2. Verify telemetry container has data
3. Check browser console for API errors
4. Ensure date format in Cosmos DB is ISO 8601

### Incorrect trend analysis
1. Verify telemetry data is being recorded
2. Check that timestamp field is properly formatted
3. Ensure fill_level is 0-100 range

### Empty response
1. Verify bin inventory exists in Inventory container
2. Check telemetry records for selected time range
3. Verify deviceId matches between containers
