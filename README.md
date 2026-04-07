# ShopVerse — Full-Stack E-Commerce Platform

A modern, production-ready e-commerce application built with **Flask** (Python) + **SQLite** + **Vanilla JS**.

---

## ✨ Features

- 🛍️ **Product Catalog** — Browse, search, and filter products
- 🛒 **Shopping Cart** — Add/remove items, update quantities
- 👤 **Auth System** — JWT-based register/login
- 💳 **Checkout** — Mock payment integration (Razorpay-ready)
- 📦 **Order History** — Track past orders
- 🔑 **Admin Panel** — Full product/order/user management
- 🖼️ **Image Upload** — Upload product images
- 📱 **Responsive** — Works on mobile and desktop

---

## 🗂️ Project Structure

```
ecommerce/
├── backend/
│   ├── app.py              # Flask app entry point
│   ├── database.py         # SQLAlchemy models + seed data
│   ├── requirements.txt    # Python dependencies
│   └── routes/
│       ├── auth.py         # /api/auth — login, register
│       ├── products.py     # /api/products — CRUD, search, upload
│       ├── cart.py         # /api/cart — cart management
│       ├── orders.py       # /api/orders — checkout, history
│       └── admin.py        # /api/admin — dashboard, user mgmt
└── frontend/
    ├── index.html          # SPA shell with all page templates
    ├── css/
    │   ├── main.css        # Design system, layout, hero
    │   └── components.css  # Cart, admin, auth, checkout styles
    └── js/
        ├── api.js          # API client (all fetch calls)
        ├── store.js        # State management
        └── app.js          # SPA router + page renderers
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Step 1 — Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2 — Run the Server

```bash
python app.py
```

The app will be available at **http://localhost:5000**

The database is created automatically at `backend/shopverse.db` with demo products and an admin account.

---

## 🔑 Demo Credentials

| Role  | Email                   | Password  |
|-------|-------------------------|-----------|
| Admin | admin@shopverse.com     | admin123  |

---

## 📡 API Reference

### Auth
| Method | Endpoint              | Description         |
|--------|-----------------------|---------------------|
| POST   | /api/auth/register    | Create account      |
| POST   | /api/auth/login       | Login → JWT token   |
| GET    | /api/auth/me          | Get current user    |

### Products
| Method | Endpoint                      | Description              |
|--------|-------------------------------|--------------------------|
| GET    | /api/products/                | List/search products     |
| GET    | /api/products/:id             | Get single product       |
| GET    | /api/products/categories      | List categories          |
| POST   | /api/products/                | Create product (admin)   |
| PUT    | /api/products/:id             | Update product (admin)   |
| DELETE | /api/products/:id             | Delete product (admin)   |
| POST   | /api/products/upload-image    | Upload image (admin)     |

**Query params for listing:**
- `q` — search query
- `category` — filter by category
- `min_price`, `max_price` — price range
- `sort` — `created_at` | `price_asc` | `price_desc` | `rating` | `name`
- `page`, `per_page` — pagination

### Cart (requires auth)
| Method | Endpoint              | Description         |
|--------|-----------------------|---------------------|
| GET    | /api/cart/            | Get user's cart     |
| POST   | /api/cart/add         | Add item            |
| PUT    | /api/cart/update/:id  | Update quantity     |
| DELETE | /api/cart/remove/:id  | Remove item         |
| DELETE | /api/cart/clear       | Clear cart          |

### Orders (requires auth)
| Method | Endpoint              | Description         |
|--------|-----------------------|---------------------|
| POST   | /api/orders/checkout  | Place order         |
| GET    | /api/orders/history   | Order history       |

### Admin (requires admin JWT)
| Method | Endpoint                          | Description           |
|--------|-----------------------------------|-----------------------|
| GET    | /api/admin/stats                  | Dashboard stats       |
| GET    | /api/admin/users                  | List users            |
| DELETE | /api/admin/users/:id              | Delete user           |
| GET    | /api/admin/orders                 | All orders            |
| PUT    | /api/admin/orders/:id/status      | Update order status   |

---

## 🔐 Authentication

All protected endpoints require a Bearer JWT token:

```
Authorization: Bearer <token>
```

The token is returned on login/register and stored in `localStorage`.

---

## 💳 Payment Integration

Currently uses a **mock payment system** that generates a fake `PAY-XXXXXXXX` ID.

To integrate **Razorpay**:
1. Add `razorpay` to `requirements.txt`
2. In `routes/orders.py`, replace the mock payment section with Razorpay order creation
3. In `frontend/js/app.js`, use the Razorpay JS SDK for the payment modal

---

## 🌐 Production Deployment

1. Set environment variables:
   ```bash
   export SECRET_KEY=your-super-secret-key
   export JWT_SECRET_KEY=your-jwt-secret
   ```

2. Use gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 'app:create_app()'
   ```

3. Serve via Nginx as reverse proxy

---

## 🎨 Tech Stack

| Layer     | Technology         |
|-----------|--------------------|
| Frontend  | HTML5, CSS3, Vanilla JS (SPA) |
| Backend   | Python Flask       |
| Database  | SQLite (via SQLAlchemy) |
| Auth      | JWT (flask-jwt-extended) |
| Fonts     | Cormorant Garamond + DM Sans |

---

Built with ❤️ by ShopVerse
