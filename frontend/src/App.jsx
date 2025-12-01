import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [order, setOrder] = useState(null)
  const [menuItems, setMenuItems] = useState([])
  const [remainingSeconds, setRemainingSeconds] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [tableNumber, setTableNumber] = useState('')

  // Fetch menu items
  const fetchMenuItems = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/menu`)
      setMenuItems(response.data)
    } catch (err) {
      console.error('Error fetching menu:', err)
      setError('ไม่สามารถโหลดเมนูได้')
    }
  }, [])

  // Start order
  const startOrder = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await axios.post(`${API_BASE_URL}/api/orders/start`, {
        table_number: tableNumber || null
      })
      setOrder(response.data)
      setRemainingSeconds(response.data.remaining_seconds)
      await fetchMenuItems()
    } catch (err) {
      console.error('Error starting order:', err)
      setError('ไม่สามารถเริ่มออเดอร์ได้')
    } finally {
      setLoading(false)
    }
  }

  // Add item to order
  const addItemToOrder = async (menuItemId) => {
    if (!order || !order.is_active || order.is_checked_out) {
      setError('ไม่สามารถเพิ่มรายการได้ เนื่องจากหมดเวลาหรือเช็คบิลแล้ว')
      return
    }

    try {
      await axios.post(`${API_BASE_URL}/api/orders/${order.id}/items`, {
        menu_item_id: menuItemId,
        quantity: 1
      })
      
      // Refresh order
      const response = await axios.get(`${API_BASE_URL}/api/orders/${order.id}`)
      setOrder(response.data)
      setRemainingSeconds(response.data.remaining_seconds)
    } catch (err) {
      console.error('Error adding item:', err)
      if (err.response?.status === 400) {
        setError(err.response.data.detail)
        // Refresh order to get updated status
        const response = await axios.get(`${API_BASE_URL}/api/orders/${order.id}`)
        setOrder(response.data)
        setRemainingSeconds(response.data.remaining_seconds)
      } else {
        setError('ไม่สามารถเพิ่มรายการได้')
      }
    }
  }

  // Checkout
  const checkoutOrder = async () => {
    if (!order) return

    try {
      await axios.post(`${API_BASE_URL}/api/orders/${order.id}/checkout`)
      
      // Refresh order
      const response = await axios.get(`${API_BASE_URL}/api/orders/${order.id}`)
      setOrder(response.data)
      setRemainingSeconds(0)
    } catch (err) {
      console.error('Error checking out:', err)
      setError('ไม่สามารถเช็คบิลได้')
    }
  }

  // Timer countdown
  useEffect(() => {
    if (!order || !order.is_active || order.is_checked_out) return

    const interval = setInterval(() => {
      setRemainingSeconds(prev => {
        if (prev <= 1) {
          // Time's up
          if (order) {
            axios.get(`${API_BASE_URL}/api/orders/${order.id}`)
              .then(response => {
                setOrder(response.data)
              })
          }
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(interval)
  }, [order])

  // Format time display
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  // Get grouped menu items by category
  const groupedMenuItems = menuItems.reduce((acc, item) => {
    if (!acc[item.category]) {
      acc[item.category] = []
    }
    acc[item.category].push(item)
    return acc
  }, {})

  // Start screen
  if (!order) {
    return (
      <div className="app">
        <div className="container">
          <div className="start-screen">
            <h2>🍽️ ยินดีต้อนรับสู่ Buffet Ordering System</h2>
            <p style={{ color: '#666', marginBottom: '30px' }}>
              เวลาในการสั่งอาหาร: <strong>1 ชั่วโมง 45 นาที</strong>
            </p>
            <input
              type="text"
              placeholder="หมายเลขโต๊ะ (ไม่จำเป็น)"
              value={tableNumber}
              onChange={(e) => setTableNumber(e.target.value)}
            />
            <button 
              className="btn btn-primary"
              onClick={startOrder}
              disabled={loading}
            >
              {loading ? 'กำลังเริ่มต้น...' : 'เริ่มสั่งอาหาร'}
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Checked out screen
  if (order.is_checked_out) {
    return (
      <div className="app">
        <div className="container">
          <div className="checked-out-screen">
            <h2>✅ เช็คบิลเรียบร้อยแล้ว</h2>
            <p>ขอบคุณที่ใช้บริการ</p>
            {order.table_number && (
              <p>โต๊ะหมายเลข: <strong>{order.table_number}</strong></p>
            )}
            <div className="total">
              รายการทั้งหมด: {order.items?.length || 0} รายการ
            </div>
            <button 
              className="btn btn-primary"
              onClick={() => {
                setOrder(null)
                setTableNumber('')
              }}
            >
              เริ่มออเดอร์ใหม่
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Expired screen
  if (!order.is_active) {
    return (
      <div className="app">
        <div className="container">
          <div className="expired-screen">
            <h2>⏰ หมดเวลาแล้ว</h2>
            <p>เวลาในการสั่งอาหารหมดแล้ว</p>
            {order.table_number && (
              <p>โต๊ะหมายเลข: <strong>{order.table_number}</strong></p>
            )}
            <div className="total" style={{ color: '#f45c43' }}>
              รายการทั้งหมด: {order.items?.length || 0} รายการ
            </div>
            <button 
              className="btn btn-primary"
              onClick={() => {
                setOrder(null)
                setTableNumber('')
              }}
            >
              เริ่มออเดอร์ใหม่
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Main ordering screen
  return (
    <div className="app">
      <div className="container">
        <div className="header">
          <h1>🍽️ Buffet Ordering System</h1>
          {order.table_number && (
            <p style={{ color: '#666' }}>โต๊ะหมายเลข: <strong>{order.table_number}</strong></p>
          )}
          
          <div className="timer-container">
            <div className={`timer ${remainingSeconds < 300 ? 'warning' : ''}`}>
              {formatTime(remainingSeconds)}
            </div>
            <div className="timer-label">
              {remainingSeconds < 300 ? '⚠️ เหลือเวลาไม่ถึง 5 นาที!' : 'เวลาที่เหลือ'}
            </div>
          </div>
        </div>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '30px' }}>
          <div className="menu-container">
            <h2>📋 เมนูอาหาร</h2>
            
            {Object.keys(groupedMenuItems).map(category => (
              <div key={category}>
                <h3 style={{ color: '#764ba2', marginTop: '20px', marginBottom: '15px' }}>
                  {category}
                </h3>
                <div className="menu-grid">
                  {groupedMenuItems[category].map(item => (
                    <div 
                      key={item.id}
                      className="menu-item"
                      onClick={() => addItemToOrder(item.id)}
                    >
                      <img src={item.image_url} alt={item.name} />
                      <h3>{item.name}</h3>
                      <p className="category">{item.category}</p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="order-summary">
            <h2>🛒 รายการที่สั่ง</h2>
            
            {order.items && order.items.length > 0 ? (
              <>
                <div className="order-items">
                  {order.items.map(item => (
                    <div key={item.id} className="order-item">
                      <div className="order-item-info">
                        <h4>{item.menu_item.name}</h4>
                        <p>{item.menu_item.category}</p>
                      </div>
                      <div className="order-item-quantity">
                        x{item.quantity}
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="order-total">
                  <h3>รายการทั้งหมด: {order.items.length} รายการ</h3>
                </div>

                <div className="checkout-container">
                  <button 
                    className="btn btn-success"
                    onClick={checkoutOrder}
                    style={{ width: '100%' }}
                  >
                    เช็คบิล
                  </button>
                </div>
              </>
            ) : (
              <p style={{ textAlign: 'center', color: '#999', padding: '40px 0' }}>
                ยังไม่มีรายการที่สั่ง<br />กรุณาเลือกเมนูอาหาร
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
