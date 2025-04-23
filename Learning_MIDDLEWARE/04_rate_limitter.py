from flask import Flask, request, g, jsonify
from functools import wraps
import time
from collections import defaultdict

app = Flask(__name__)

# Simple in-memory rate limiter
class RateLimiter:
    def __init__(self, limit=2, window=60):
        self.limit = limit  # Max requests
        self.window = window  # Time window in seconds
        self.clients = defaultdict(list)  # client_id -> list of timestamps
    
    def is_rate_limited(self, client_id):
        now = time.time()
        
        # Remove timestamps outside current window
        self.clients[client_id] = [ts for ts in self.clients[client_id] if now - ts < self.window]
        
        # Check if the client is over the limit
        if len(self.clients[client_id]) >= self.limit:
            return True
        
        # Record this request
        self.clients[client_id].append(now)
        return False

# Create a limiter with 5 requests per minute
limiter = RateLimiter(limit=5, window=60)

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get client identifier (typically IP address)
        client_id = request.remote_addr
        
        # Check if client is rate limited
        if limiter.is_rate_limited(client_id):
            return jsonify({
                'error': 'Rate limit exceeded',
                'retry_after': 60  # Seconds to wait
            }), 429
        
        return f(*args, **kwargs)
    return decorated_function


@app.route('/api/limited')
@rate_limit
def limited_endpoint():
    return {'message': 'This endpoint is rate limited'}

@app.route('/api/unlimited')
def unlimited_endpoint():
    return {'message': 'This endpoint is not rate limited'}

if __name__ == '__main__':
    app.run(debug=True)