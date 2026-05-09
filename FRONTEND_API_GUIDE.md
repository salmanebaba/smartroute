# Smart Bin Route Optimizer - Frontend Integration Guide

## Overview

**Smart Route** is a Flask-powered API for optimizing smart bin collection routes using Azure Cosmos DB. It calculates the most efficient collection paths and generates interactive maps for drivers.

**Base URL:** `http://localhost:8000` (development) or `https://api.smartroute.com` (production)

---

## App Architecture

```
┌─────────────────────────────────────────────┐
│         Frontend (React/Vue/Angular)        │
└──────────────────┬──────────────────────────┘
                   │ HTTP REST API
┌──────────────────▼──────────────────────────┐
│   FastAPI Backend (app/routes/router.py)    │
├──────────────────────────────────────────────┤
│  Services Layer (Business Logic)             │
│  ├── BinService (bin operations)             │
│  ├── RouteOptimizer (algorithms)             │
│  └── MapGenerator (visualizations)           │
├──────────────────────────────────────────────┤
│  Data Layer (Azure Cosmos DB)                │
│  ├── Telemetry (fill levels)                 │
│  └── BinsInventory (locations)               │
└──────────────────────────────────────────────┘
```

---

## API Endpoints

### 1. Health Check
**GET** `/health`

**Description:** Check if the API is running

**Response (200 OK):**
```json
{
  "status": "ok",
  "service": "Smart Bin Route Optimizer"
}
```

---

### 2. Get All Bins
**GET** `/bins`

**Description:** Retrieve all bins with current telemetry data

**Response (200 OK):**
```json
[
  {
    "id": "bin_001",
    "latitude": 33.979,
    "longitude": -6.866,
    "fill_level": 75
  },
  {
    "id": "bin_002",
    "latitude": 33.980,
    "longitude": -6.865,
    "fill_level": 45
  }
]
```

**Error (500):**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

### 3. Get Bins Needing Collection
**GET** `/bins/needing-collection?threshold=70`

**Description:** Get bins above a fill level threshold (any bin with fill > 0 by default)

**Query Parameters:**
- `threshold` (optional, default: 70) - Fill level percentage (0-100)

**Response (200 OK):**
```json
[
  {
    "id": "bin_001",
    "latitude": 33.979,
    "longitude": -6.866,
    "fill_level": 75
  },
  {
    "id": "bin_003",
    "latitude": 33.981,
    "longitude": -6.864,
    "fill_level": 85
  }
]
```

---

### 4. Get Specific Bin
**GET** `/bins/{bin_id}`

**Description:** Get details for a specific bin

**Path Parameters:**
- `bin_id` - The bin identifier (e.g., "bin_001")

**Response (200 OK):**
```json
{
  "id": "bin_001",
  "latitude": 33.979,
  "longitude": -6.866,
  "fill_level": 75
}
```

**Error (404 Not Found):**
```json
{
  "detail": "Bin bin_999 not found"
}
```

---

### 5. Get Collection Statistics
**GET** `/bins/statistics`

**Description:** Get aggregated statistics about bin collection needs

**Response (200 OK):**
```json
{
  "total_bins": 15,
  "bins_needing_collection": 8,
  "average_fill_level": 62.5,
  "collection_percentage": 53.33
}
```

---

### 6. Optimize Route
**GET** `/route/optimize?strategy=distance`

**Description:** Generate an optimized collection route

**Query Parameters:**
- `strategy` (required) - One of:
  - `distance` - Nearest neighbor algorithm (minimize total distance)
  - `fill_level` - Prioritize bins by fill percentage (highest first)
  - `time` - Minimize travel time (based on average speed)

**Response (200 OK):**
```json
{
  "strategy": "distance",
  "total_distance": 12.5,
  "estimated_time": 25.0,
  "stops": [
    {
      "bin": {
        "id": "bin_001",
        "latitude": 33.979,
        "longitude": -6.866,
        "fill_level": 75
      },
      "order": 1,
      "distance_from_previous": 0.5
    },
    {
      "bin": {
        "id": "bin_003",
        "latitude": 33.981,
        "longitude": -6.864,
        "fill_level": 85
      },
      "order": 2,
      "distance_from_previous": 0.3
    }
  ]
}
```

---

### 7. Get Interactive Map (Optimized Route)
**GET** `/map?strategy=distance`

**Description:** Get an interactive Folium map showing the optimized route

**Query Parameters:**
- `strategy` (optional, default: "distance") - Optimization strategy

**Response (200 OK):**
- Returns HTML page with interactive map
- Use in an `<iframe>` or open in browser

**Example:**
```html
<iframe src="http://localhost:8000/map?strategy=distance" 
        width="100%" 
        height="600px" 
        frameborder="0">
</iframe>
```

**Map Features:**
- 🚚 Black truck marker = Depot/start point
- 🔴 Red circles = Urgent bins (85%+ full)
- 🟠 Orange circles = Medium bins (50-85% full)
- 🟢 Green circles = Low priority bins (<50% full)
- 📍 Distance label = Total route distance
- 💫 Blue animated lines = Optimized route path
- Numbers = Order of collection

---

### 8. Get Debug Map (All Bins)
**GET** `/map/debug`

**Description:** Get a map showing all bins without route optimization

**Response (200 OK):**
- Returns HTML page with interactive map showing all bins

**Example:**
```html
<iframe src="http://localhost:8000/map/debug" 
        width="100%" 
        height="600px" 
        frameborder="0">
</iframe>
```

---

### 9. Get Debug Data
**GET** `/debug-data`

**Description:** Get all bins with full telemetry information (for debugging)

**Response (200 OK):**
```json
{
  "total_bins": 15,
  "bins": [
    {
      "id": "bin_001",
      "latitude": 33.979,
      "longitude": -6.866,
      "fill_level": 75
    },
    {
      "id": "bin_002",
      "latitude": 33.980,
      "longitude": -6.865,
      "fill_level": 45
    }
  ]
}
```

---

## Data Models

### Bin Model
Represents a waste bin/container with location and fill level

```json
{
  "id": "bin_001",           // Unique identifier
  "latitude": 33.979,        // Geographic latitude
  "longitude": -6.866,       // Geographic longitude
  "fill_level": 75           // Fill percentage (0-100)
}
```

### RouteStop Model
Represents a single stop in an optimized route

```json
{
  "bin": { /* Bin object */ },
  "order": 1,                // Position in route (1 = first stop)
  "distance_from_previous": 0.5  // Distance in km from previous stop
}
```

### OptimizedRoute Model
Complete optimized collection route

```json
{
  "strategy": "distance",    // Strategy used (distance, fill_level, time)
  "total_distance": 12.5,    // Total route distance in km
  "estimated_time": 25.0,    // Estimated time in minutes (if strategy=time)
  "stops": [
    { /* RouteStop objects */ }
  ]
}
```

### DebugData Model
All bins with telemetry (debugging only)

```json
{
  "total_bins": 15,
  "bins": [
    { /* Bin objects */ }
  ]
}
```

---

## Common Use Cases

### 1. Display All Bins on Map
```javascript
// Frontend code
fetch('http://localhost:8000/map/debug')
  .then(response => response.text())
  .then(html => {
    document.getElementById('map-container').innerHTML = html;
  });
```

### 2. Get Optimized Route
```javascript
// Get route optimized by distance
fetch('http://localhost:8000/route/optimize?strategy=distance')
  .then(response => response.json())
  .then(data => {
    console.log(`Total distance: ${data.total_distance} km`);
    console.log(`Stops: ${data.stops.length}`);
    
    // Display stops in list
    data.stops.forEach(stop => {
      console.log(`Stop ${stop.order}: Bin ${stop.bin.id} (${stop.bin.fill_level}% full)`);
    });
  });
```

### 3. Display Optimized Route Map
```javascript
// Display interactive route map
const mapContainer = document.getElementById('map');
const iframe = document.createElement('iframe');
iframe.src = 'http://localhost:8000/map?strategy=distance';
iframe.style.width = '100%';
iframe.style.height = '600px';
iframe.frameBorder = '0';
mapContainer.appendChild(iframe);
```

### 4. Get Collection Statistics for Dashboard
```javascript
fetch('http://localhost:8000/bins/statistics')
  .then(response => response.json())
  .then(data => {
    // Display on dashboard
    document.getElementById('total-bins').textContent = data.total_bins;
    document.getElementById('needing-collection').textContent = data.bins_needing_collection;
    document.getElementById('avg-fill').textContent = data.average_fill_level.toFixed(1) + '%';
    document.getElementById('collection-rate').textContent = data.collection_percentage.toFixed(1) + '%';
  });
```

---

## Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success - Request completed successfully |
| 400 | Bad Request - Invalid query parameters |
| 404 | Not Found - Bin/resource not found |
| 500 | Server Error - Internal server error |

---

## Error Handling

All errors return a JSON response with a `detail` field:

```json
{
  "detail": "Description of what went wrong"
}
```

**Example:**
```javascript
fetch('http://localhost:8000/bins/nonexistent')
  .then(response => {
    if (!response.ok) {
      return response.json().then(error => {
        throw new Error(error.detail);
      });
    }
    return response.json();
  })
  .catch(error => {
    console.error('API Error:', error.message);
  });
```

---

## Rate Limiting & Performance

- No rate limiting currently implemented
- Response times: < 500ms for most endpoints
- Map generation: 1-2 seconds depending on bin count

---

## CORS Configuration

The API allows requests from any origin (`*` in development). For production, update `app/config.py`:

```python
CORS_ORIGINS = ["https://yourdomain.com", "https://www.yourdomain.com"]
```

---

## Interactive API Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Visit these URLs to explore the API interactively!

---

## Frontend Implementation Tips

### Best Practices

1. **Cache map displays** - Maps take time to generate, cache HTML
2. **Debounce strategy changes** - Don't call `/route/optimize` on every keystroke
3. **Update statistics periodically** - Call `/bins/statistics` every 30-60 seconds
4. **Handle network errors** - API may be temporarily unavailable
5. **Use responsive containers** - Maps should adapt to screen size

### Example React Hook

```javascript
import { useEffect, useState } from 'react';

export function useOptimizedRoute(strategy = 'distance') {
  const [route, setRoute] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    fetch(`http://localhost:8000/route/optimize?strategy=${strategy}`)
      .then(r => r.json())
      .then(data => {
        setRoute(data);
        setError(null);
      })
      .catch(err => {
        setError(err.message);
      })
      .finally(() => setLoading(false));
  }, [strategy]);

  return { route, loading, error };
}
```

---

## Support & Debugging

- **API Docs:** http://localhost:8000/docs
- **Debug Endpoint:** `/debug-data` - Returns all bins with telemetry
- **Debug Map:** `/map/debug` - Shows all bins without optimization
- **Health Check:** `/health` - Quick server status

For issues, check the backend logs and error responses carefully.

---

## Version History

- **v1.0** (May 2026) - Initial release with 3 optimization strategies
