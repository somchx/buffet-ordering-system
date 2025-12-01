# API Testing Examples

## Using curl

### 1. Check API is running
```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "message": "Buffet Ordering System API",
  "version": "1.0"
}
```

### 2. Seed sample menu data
```bash
curl -X POST http://localhost:8000/api/seed
```

### 3. Get all menu items
```bash
curl http://localhost:8000/api/menu | python -m json.tool
```

### 4. Start a new order
```bash
curl -X POST http://localhost:8000/api/orders/start \
  -H "Content-Type: application/json" \
  -d '{"table_number": "A1"}'
```

Save the `id` from the response (e.g., 1)

### 5. Get order details
```bash
curl http://localhost:8000/api/orders/1 | python -m json.tool
```

### 6. Add items to order
```bash
# Add ข้าวผัด (menu_item_id: 1)
curl -X POST http://localhost:8000/api/orders/1/items \
  -H "Content-Type: application/json" \
  -d '{"menu_item_id": 1, "quantity": 2}'

# Add ผัดไทย (menu_item_id: 2)
curl -X POST http://localhost:8000/api/orders/1/items \
  -H "Content-Type: application/json" \
  -d '{"menu_item_id": 2, "quantity": 1}'

# Add ไก่ทอด (menu_item_id: 4)
curl -X POST http://localhost:8000/api/orders/1/items \
  -H "Content-Type: application/json" \
  -d '{"menu_item_id": 4, "quantity": 3}'
```

### 7. Check order status
```bash
curl http://localhost:8000/api/orders/1 | python -m json.tool
```

### 8. Checkout order
```bash
curl -X POST http://localhost:8000/api/orders/1/checkout
```

### 9. Create a new menu item
```bash
curl -X POST http://localhost:8000/api/menu \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ข้าวมันไก่",
    "category": "อาหารจานหลัก",
    "price": 0,
    "image_url": "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=400",
    "is_available": true
  }'
```

### 10. Update menu item
```bash
curl -X PUT http://localhost:8000/api/menu/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ข้าวผัดพิเศษ",
    "category": "อาหารจานหลัก",
    "price": 0,
    "image_url": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=400",
    "is_available": true
  }'
```

### 11. Delete menu item (soft delete)
```bash
curl -X DELETE http://localhost:8000/api/menu/1
```

---

## Using Python requests

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# 1. Seed data
response = requests.post(f"{BASE_URL}/api/seed")
print("Seed:", response.json())

# 2. Get menu
response = requests.get(f"{BASE_URL}/api/menu")
menu = response.json()
print(f"Menu items: {len(menu)}")

# 3. Start order
response = requests.post(
    f"{BASE_URL}/api/orders/start",
    json={"table_number": "B5"}
)
order = response.json()
order_id = order['id']
print(f"Order created: {order_id}")

# 4. Add items
for item_id in [1, 2, 3, 4, 5]:
    response = requests.post(
        f"{BASE_URL}/api/orders/{order_id}/items",
        json={"menu_item_id": item_id, "quantity": 1}
    )
    print(f"Added item {item_id}")

# 5. Get order
response = requests.get(f"{BASE_URL}/api/orders/{order_id}")
order = response.json()
print(f"Order items: {len(order['items'])}")
print(f"Remaining time: {order['remaining_seconds']} seconds")

# 6. Wait a bit
time.sleep(5)

# 7. Checkout
response = requests.post(f"{BASE_URL}/api/orders/{order_id}/checkout")
print("Checkout:", response.json())
```

---

## Using JavaScript fetch

```javascript
const BASE_URL = "http://localhost:8000";

// Start order
async function startOrder() {
  const response = await fetch(`${BASE_URL}/api/orders/start`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({table_number: 'C10'})
  });
  const order = await response.json();
  console.log('Order created:', order);
  return order.id;
}

// Add item
async function addItem(orderId, menuItemId, quantity) {
  const response = await fetch(`${BASE_URL}/api/orders/${orderId}/items`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({menu_item_id: menuItemId, quantity: quantity})
  });
  const item = await response.json();
  console.log('Item added:', item);
}

// Checkout
async function checkout(orderId) {
  const response = await fetch(`${BASE_URL}/api/orders/${orderId}/checkout`, {
    method: 'POST'
  });
  const result = await response.json();
  console.log('Checkout:', result);
}

// Run
(async () => {
  const orderId = await startOrder();
  await addItem(orderId, 1, 2);
  await addItem(orderId, 2, 1);
  await addItem(orderId, 3, 1);
  await checkout(orderId);
})();
```

---

## Postman Collection

You can import these requests into Postman:

### Base URL
```
http://localhost:8000
```

### Requests

1. **GET** `/` - Health check
2. **POST** `/api/seed` - Seed data
3. **GET** `/api/menu` - Get menu
4. **POST** `/api/menu` - Create menu item
5. **PUT** `/api/menu/{item_id}` - Update menu item
6. **DELETE** `/api/menu/{item_id}` - Delete menu item
7. **POST** `/api/orders/start` - Start order
8. **GET** `/api/orders/{order_id}` - Get order
9. **POST** `/api/orders/{order_id}/items` - Add item
10. **POST** `/api/orders/{order_id}/checkout` - Checkout

---

## Testing Timer

### Test 1: Normal checkout before time expires
```bash
# Start order
ORDER_ID=$(curl -s -X POST http://localhost:8000/api/orders/start -H "Content-Type: application/json" -d '{}' | python -c "import sys, json; print(json.load(sys.stdin)['id'])")

# Add items
curl -X POST http://localhost:8000/api/orders/$ORDER_ID/items -H "Content-Type: application/json" -d '{"menu_item_id": 1, "quantity": 1}'

# Wait 5 seconds
sleep 5

# Checkout
curl -X POST http://localhost:8000/api/orders/$ORDER_ID/checkout

# Try to add more items (should fail)
curl -X POST http://localhost:8000/api/orders/$ORDER_ID/items -H "Content-Type: application/json" -d '{"menu_item_id": 2, "quantity": 1}'
```

### Test 2: Check remaining time
```bash
ORDER_ID=1

# Check every 10 seconds
for i in {1..10}; do
  echo "Check $i:"
  curl -s http://localhost:8000/api/orders/$ORDER_ID | python -m json.tool | grep remaining_seconds
  sleep 10
done
```

### Test 3: Simulate time expiration
To test time expiration, you need to modify the timer in the code or wait 105 minutes.

For testing purposes, you can temporarily change the time limit in `backend/main.py`:
```python
# Line in start_order function
end_time = start_time + timedelta(minutes=2)  # Change from 105 to 2 minutes

# Line in calculate_remaining_time function
remaining = (2 * 60) - elapsed  # Change from 105 to 2 minutes
```

Then:
```bash
# Start order
ORDER_ID=$(curl -s -X POST http://localhost:8000/api/orders/start -H "Content-Type: application/json" -d '{}' | python -c "import sys, json; print(json.load(sys.stdin)['id'])")

# Add items
curl -X POST http://localhost:8000/api/orders/$ORDER_ID/items -H "Content-Type: application/json" -d '{"menu_item_id": 1, "quantity": 1}'

# Wait 2 minutes
sleep 120

# Try to add more items (should fail)
curl -X POST http://localhost:8000/api/orders/$ORDER_ID/items -H "Content-Type: application/json" -d '{"menu_item_id": 2, "quantity": 1}'

# Check order status
curl http://localhost:8000/api/orders/$ORDER_ID | python -m json.tool
```

---

## Load Testing

### Using Apache Bench (ab)
```bash
# Install ab (if not installed)
# macOS: comes with Apache
# Linux: sudo apt-get install apache2-utils

# Test GET /api/menu
ab -n 1000 -c 10 http://localhost:8000/api/menu

# Test POST /api/orders/start
ab -n 100 -c 5 -p order.json -T application/json http://localhost:8000/api/orders/start
```

### Using wrk
```bash
# Install wrk
# macOS: brew install wrk
# Linux: sudo apt-get install wrk

# Test
wrk -t4 -c100 -d30s http://localhost:8000/api/menu
```

---

## Database Inspection

### SQLite
```bash
cd backend
sqlite3 buffet.db

# List tables
.tables

# Show orders
SELECT * FROM orders;

# Show menu items
SELECT * FROM menu_items;

# Show order items with details
SELECT oi.*, mi.name, o.table_number 
FROM order_items oi 
JOIN menu_items mi ON oi.menu_item_id = mi.id 
JOIN orders o ON oi.order_id = o.id;

# Exit
.quit
```

### PostgreSQL (Production)
```bash
psql -h your-rds-endpoint -U admin -d postgres

# List tables
\dt

# Show data
SELECT * FROM orders;
SELECT * FROM menu_items;
SELECT * FROM order_items;

# Exit
\q
```
