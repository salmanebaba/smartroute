"""
Application constants and utility values.
"""

# Route optimization strategies
OPTIMIZATION_STRATEGIES = {
    "distance": "Minimize total distance",
    "time": "Minimize total travel time",
    "fill_level": "Prioritize bins by fill level",
}

# Default values
DEFAULT_OPTIMIZATION_STRATEGY = "distance"
EMPTY_THRESHOLD = 30  # Fill level below which bin is considered empty
FULL_THRESHOLD = 70   # Fill level above which bin is considered full

# API Response codes
SUCCESS_CODE = 200
ERROR_CODE = 500
NOT_FOUND_CODE = 404
