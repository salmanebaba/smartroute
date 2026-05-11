# Smart Bin Route Optimizer - Backend

Modern, scalable backend API for optimizing smart bin collection routes using FastAPI and Azure Cosmos DB.

## Architecture

The backend follows a **layered architecture** pattern for maintainability and scalability:

```
app/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration and environment variables
├── models/
│   └── schemas.py       # Pydantic data models and schemas
├── data/
│   └── cosmos_client.py # Database access layer (DAL)
├── services/
│   ├── bin_service.py           # Business logic for bins
│   ├── route_optimizer.py       # Route optimization algorithms
│   └── map_generator.py         # Map visualization
├── routes/
│   └── router.py        # API endpoints
└── utils/
    └── constants.py     # Application constants
```

### Layers Explained

1. **Data Layer** (`data/`)
   - Manages all Azure Cosmos DB operations
   - Abstracts database queries
   - Handles telemetry and inventory data

2. **Models Layer** (`models/`)
   - Pydantic schemas for request/response validation
   - Type hints and documentation

3. **Services Layer** (`services/`)
   - Business logic and algorithms
   - Route optimization (distance, fill-level, time)
   - Map generation
   - Statistics and analytics

4. **Routes Layer** (`routes/`)
   - RESTful API endpoints
   - Request handling and validation
   - Error handling

5. **Configuration** (`config.py`)
   - Centralized environment variables
   - Application settings

## Setup

### Prerequisites
- Python 3.11+
- Azure Cosmos DB credentials
- Docker (optional)

### Installation

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Azure credentials
   ```

4. **Run application:**
   ```bash
   uvicorn app.main:app --reload
   ```

Visit `http://localhost:8000/docs` for interactive API documentation.

## Docker

### Build
```bash
docker build -t smartroute-backend .
```

### Run
```bash
docker run -p 8000:8000 --env-file .env smartroute-backend
```

### Docker Compose
```bash
docker-compose up -d
```

## API Endpoints

### Bins
- `GET /bins` - Get all bins with telemetry
- `GET /bins/{bin_id}` - Get specific bin details
- `GET /bins/needing-collection?threshold=70` - Get bins needing collection
- `GET /bins/statistics` - Get collection statistics

### Routes
- `GET /route/optimize?strategy=distance` - Generate optimized route
  - Strategies: `distance`, `fill_level`, `time`

### Visualization
- `GET /map?strategy=distance` - Get interactive route map
- `GET /map/debug` - Get debug map with all bins

### Debug
- `GET /debug-data` - Get all debug information
- `GET /health` - Health check

## Optimization Strategies

1. **Distance**: Nearest neighbor algorithm (minimize total distance)
2. **Fill Level**: Prioritize bins by fill percentage (highest first)
3. **Time**: Minimize travel time based on average speed

## Environment Variables

```env
COSMOS_URI=https://your-account.documents.azure.com:443/
COSMOS_KEY=your-cosmos-key
DATABASE_NAME=SmartBinDB
DEBUG=False
```

## Testing

```bash
pytest tests/
```

## Future Improvements

- [ ] TSP (Traveling Salesman Problem) solver for optimal routes
- [ ] Traffic-aware route optimization
- [ ] Real-time GPS tracking
- [ ] Machine learning for demand prediction
- [ ] Rate limiting and caching
- [ ] Authentication and authorization
- [ ] Comprehensive test suite
- [ ] API versioning
