# Backend Refactoring & Migration Guide

## Overview

The backend has been completely restructured from a monolithic design to a modern layered architecture. All code is now organized under the `app/` directory with clear separation of concerns.

## What Changed

### Old Structure (Monolithic)
```
backend/
├── main.py        # Mixed FastAPI setup
├── models.py      # Single models file
├── routes.py      # Routes with hardcoded logic
├── services.py    # Mixed database, business logic, and map generation
├── Dockerfile
└── requirements.txt
```

### New Structure (Layered)
```
backend/
├── app/
│   ├── main.py                  # Clean FastAPI setup
│   ├── config.py                # Centralized configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py           # All Pydantic models
│   ├── data/
│   │   ├── __init__.py
│   │   └── cosmos_client.py     # Database abstraction layer
│   ├── services/
│   │   ├── __init__.py
│   │   ├── bin_service.py       # Bin business logic
│   │   ├── route_optimizer.py   # Route optimization algorithms
│   │   └── map_generator.py     # Map visualization
│   ├── routes/
│   │   ├── __init__.py
│   │   └── router.py            # All API endpoints
│   └── utils/
│       ├── __init__.py
│       └── constants.py         # Application constants
├── .env.example
├── .dockerignore
├── Dockerfile      # Updated
├── requirements.txt # Updated with better versions
└── README.md       # Comprehensive documentation
```

## Migration Steps (Already Done)

✅ **Data Layer Separation**
- All Cosmos DB operations moved to `app/data/cosmos_client.py`
- Clean, reusable `CosmosDataClient` class
- Queries abstracted away from business logic

✅ **Services Layer**
- `BinService`: Manages bin operations and statistics
- `RouteOptimizer`: Three optimization strategies (distance, fill_level, time)
- `MapGenerator`: Folium map generation with visualization

✅ **Routes Reorganization**
- All endpoints moved to `app/routes/router.py`
- Clean endpoint organization with tags
- Improved error handling and validation

✅ **Configuration Centralization**
- All environment variables in `app/config.py`
- Constants in `app/utils/constants.py`
- Better maintainability

## Key Improvements

### 1. **Separation of Concerns**
- Each layer has a single responsibility
- Easy to test individual components
- Changes to one layer don't affect others

### 2. **Scalability**
- Easy to add new services
- New optimization strategies can be added to `RouteOptimizer`
- Database operations centralized for easy migration to other DBs

### 3. **Maintainability**
- Clear code organization
- Better documentation
- Easier debugging

### 4. **Testability**
- Each layer can be tested independently
- Mock data clients for unit tests
- Service logic decoupled from database

### 5. **Reusability**
- Services can be used by multiple routes
- Data client can be reused across services
- Consistent models throughout the application

## API Changes

**Good news:** The API endpoints remain the same! All existing client code will continue to work:

```
GET  /bins
GET  /bins/{bin_id}
GET  /bins/needing-collection
GET  /bins/statistics
GET  /route/optimize?strategy=distance
GET  /map?strategy=distance
GET  /map/debug
GET  /debug-data
GET  /health
```

## Running the Application

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your credentials

# Run
uvicorn app.main:app --reload
```

### Docker
```bash
# Build
docker build -t smartroute-backend .

# Run
docker run -p 8000:8000 --env-file .env smartroute-backend
```

### Docker Compose
```bash
docker-compose up -d backend
```

## Old Files to Remove

The following files are now integrated into the new structure and can be safely removed:

- `backend/main.py` (replaced by `app/main.py`)
- `backend/models.py` (replaced by `app/models/schemas.py`)
- `backend/routes.py` (replaced by `app/routes/router.py`)
- `backend/services.py` (split into multiple services)

**Note:** Git will handle this automatically once you commit the changes.

## Dependency Updates

Requirements have been updated to use more recent, stable versions:
- FastAPI 0.104.0+ (improved performance and features)
- Pydantic 2.0+ (better validation and speed)
- Azure Cosmos 4.5.0+ (bug fixes and improvements)
- Added health checks and logging

## Testing the New Structure

Test the API:
```bash
# Get all bins
curl http://localhost:8000/bins

# Get optimized route
curl http://localhost:8000/route/optimize?strategy=distance

# View interactive map
open http://localhost:8000/map
```

## Future Enhancements

The new structure enables easy implementation of:
- 🧪 Comprehensive unit and integration tests
- 🔐 Authentication/authorization layer
- 📊 Caching and performance optimization
- 📈 Advanced route optimization (TSP solver)
- 🔔 Real-time notifications
- 📱 Mobile app backend support
- 🌍 Multi-region support

## Support

For questions or issues with the new structure:
1. Check the README.md in the backend directory
2. Review the docstrings in each module
3. Visit http://localhost:8000/docs for interactive API docs
