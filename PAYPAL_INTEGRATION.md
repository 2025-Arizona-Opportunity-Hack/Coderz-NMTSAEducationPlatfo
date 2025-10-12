# PayPal Payment Integration Documentation

This document describes the PayPal payment integration for course purchases in the NMTSA LMS.

## Overview

The application now supports paid courses through PayPal integration. Students can purchase courses using PayPal's secure payment gateway, and the system automatically enrolls them upon successful payment.

## Architecture

### Backend Components

#### 1. Payment Model (`authentication/models.py`)
Tracks all payment transactions with the following fields:
- `user`: ForeignKey to User (who made the payment)
- `course`: ForeignKey to Course (what was purchased)
- `paypal_order_id`: Unique PayPal order identifier
- `paypal_payment_id`: PayPal payment/capture identifier
- `payer_email`: PayPal payer's email
- `payer_name`: PayPal payer's name
- `amount`: Payment amount (Decimal)
- `currency`: Currency code (default: USD)
- `status`: Payment status (pending, completed, failed, refunded)
- `created_at`: When payment was initiated
- `completed_at`: When payment was completed
- `paypal_response`: Full PayPal API response (JSON)

#### 2. Payment API Views (`student_dash/payment_views.py`)

**CreatePaymentOrderView**
- Endpoint: `POST /api/v1/student/payments/create-order/`
- Purpose: Creates a PayPal order for a course
- Authentication: Required (Student role)
- Request body: `{ "course_id": "1" }`
- Returns: `{ "order_id": "...", "amount": "...", "currency": "USD" }`

**CapturePaymentOrderView**
- Endpoint: `POST /api/v1/student/payments/capture-order/`
- Purpose: Captures a PayPal payment after user approval
- Authentication: Required (Student role)
- Request body: `{ "order_id": "..." }`
- Returns: `{ "success": true, "payment_id": "...", "enrollment_id": "..." }`
- Side effects: Creates enrollment, increments course enrollment count

**PaymentHistoryView**
- Endpoint: `GET /api/v1/student/payments/`
- Purpose: Retrieves user's payment history
- Authentication: Required (Student role)
- Returns: Array of payment records

#### 3. PayPal Configuration (`nmtsa_lms/settings.py`)
```python
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID', '')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET', '')
PAYPAL_MODE = os.getenv('PAYPAL_MODE', 'sandbox')  # 'sandbox' or 'live'
PAYPAL_BASE_URL = 'https://api-m.sandbox.paypal.com' if PAYPAL_MODE == 'sandbox' else 'https://api-m.paypal.com'
```

### Frontend Components

#### 1. PayPal Provider Setup (`src/provider.tsx`)
Wraps the application with `PayPalScriptProvider`:
```tsx
<PayPalScriptProvider options={{
  clientId: import.meta.env.VITE_PAYPAL_CLIENT_ID || "test",
  currency: "USD",
  intent: "capture",
}}>
  {children}
</PayPalScriptProvider>
```

#### 2. Payment Button Component (`src/components/payment/PaymentButton.tsx`)
Reusable component that handles PayPal button rendering and payment flow:
- Creates PayPal order via backend API
- Handles user approval/cancellation
- Captures payment and triggers success callback
- Shows loading states and error messages

#### 3. Payment Service (`src/services/payment.service.ts`)
API client for payment operations:
- `createOrder(courseId)`: Creates PayPal order
- `captureOrder(orderId)`: Captures payment
- `getPaymentHistory()`: Gets user's payments

#### 4. Updated Course Types (`src/types/api.ts`)
Extended Course interface with:
- `price?: number`
- `isPaid?: boolean`

Added payment interfaces:
- `Payment`: Payment record
- `CreatePaymentOrderResponse`: Order creation response
- `CapturePaymentOrderResponse`: Payment capture response

#### 5. Course Hero Component (`src/components/course/CourseHero.tsx`)
Enhanced to show:
- Price display for paid courses
- "Buy Now" button for paid courses
- PayPal payment buttons when user clicks "Buy Now"
- Automatic enrollment refresh after successful payment

## Setup Instructions

### Backend Setup

1. **Get PayPal Credentials**
   - Sign up at https://developer.paypal.com
   - Create a new app in the Dashboard
   - Copy Client ID and Secret

2. **Configure Environment Variables**
   Create/update `.env` file in `backend/nmtsa_lms/`:
   ```env
   PAYPAL_CLIENT_ID=your_client_id_here
   PAYPAL_CLIENT_SECRET=your_client_secret_here
   PAYPAL_MODE=sandbox  # or 'live' for production
   ```

3. **Run Migrations**
   ```bash
   cd backend/nmtsa_lms
   python manage.py migrate
   ```

4. **Restart Django Server**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Configure Environment Variables**
   Create/update `.env` file in `frontend/`:
   ```env
   VITE_PAYPAL_CLIENT_ID=your_client_id_here
   ```
   **Note:** Use the same Client ID as backend

2. **Install Dependencies** (Already done)
   ```bash
   cd frontend
   pnpm install
   ```

3. **Start Development Server**
   ```bash
   pnpm dev
   ```

## Usage Flow

### Creating a Paid Course (Admin/Teacher)

1. Create or edit a course
2. Set `is_paid = True`
3. Set `price` field (e.g., 49.99)
4. Publish the course

### Student Purchase Flow

1. Student browses to course detail page
2. If course is paid and not enrolled:
   - See price displayed (e.g., "$49.99")
   - Click "Buy Now" button
   - PayPal buttons appear
3. Student clicks PayPal button
4. Redirected to PayPal (or PayPal popup)
5. Student logs into PayPal and approves payment
6. Redirected back to course page
7. Backend captures payment
8. Student automatically enrolled
9. Course page refreshes showing enrollment

## Payment Flow Diagram

```
┌─────────┐         ┌──────────┐         ┌─────────┐         ┌─────────┐
│ Student │         │ Frontend │         │ Backend │         │ PayPal  │
└────┬────┘         └────┬─────┘         └────┬────┘         └────┬────┘
     │                   │                     │                    │
     │ Click "Buy Now"   │                     │                    │
     ├──────────────────>│                     │                    │
     │                   │                     │                    │
     │                   │ createOrder(courseId)                    │
     │                   ├────────────────────>│                    │
     │                   │                     │                    │
     │                   │                     │ Create Order       │
     │                   │                     ├───────────────────>│
     │                   │                     │                    │
     │                   │                     │ Order ID           │
     │                   │                     │<───────────────────┤
     │                   │                     │                    │
     │                   │    Order ID         │                    │
     │                   │<────────────────────┤                    │
     │                   │                     │                    │
     │                   │ Show PayPal Button  │                    │
     │<──────────────────┤                     │                    │
     │                   │                     │                    │
     │ Click PayPal      │                     │                    │
     ├──────────────────>│                     │                    │
     │                   │                     │                    │
     │                   │              Redirect to PayPal          │
     ├──────────────────────────────────────────────────────────────>│
     │                   │                     │                    │
     │                   │              PayPal Login/Approval       │
     │<───────────────────────────────────────────────────────────────┤
     │                   │                     │                    │
     │                   │              Return to Site               │
     │<──────────────────────────────────────────────────────────────┤
     │                   │                     │                    │
     │                   │ captureOrder(orderId)                    │
     │                   ├────────────────────>│                    │
     │                   │                     │                    │
     │                   │                     │ Capture Payment    │
     │                   │                     ├───────────────────>│
     │                   │                     │                    │
     │                   │                     │ Payment Details    │
     │                   │                     │<───────────────────┤
     │                   │                     │                    │
     │                   │                     │ Create Enrollment  │
     │                   │                     ├──┐                 │
     │                   │                     │  │ (Internal)      │
     │                   │                     │<─┘                 │
     │                   │                     │                    │
     │                   │    Success          │                    │
     │                   │<────────────────────┤                    │
     │                   │                     │                    │
     │ Refresh Page      │                     │                    │
     │<──────────────────┤                     │                    │
     │                   │                     │                    │
```

## Database Schema

### Payment Table
```sql
CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    course_id INTEGER NOT NULL REFERENCES courses(id),
    paypal_order_id VARCHAR(255) UNIQUE NOT NULL,
    paypal_payment_id VARCHAR(255),
    payer_email VARCHAR(254),
    payer_name VARCHAR(255),
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'pending',
    created_at DATETIME NOT NULL,
    completed_at DATETIME,
    updated_at DATETIME NOT NULL,
    paypal_response JSON,
    
    INDEX idx_user_created (user_id, created_at),
    INDEX idx_course_created (course_id, created_at),
    INDEX idx_paypal_order (paypal_order_id)
);
```

## Testing

### Testing with PayPal Sandbox

1. **Create Sandbox Accounts**
   - Go to https://developer.paypal.com/dashboard/accounts
   - Create a test buyer account
   - Create a test merchant account

2. **Test Purchase Flow**
   - Set course as paid with price
   - As student, navigate to course
   - Click "Buy Now"
   - Use sandbox buyer credentials to pay
   - Verify enrollment created

3. **Check Payment Records**
   - Django Admin: Authentication > Payments
   - Verify payment status is "completed"
   - Check PayPal response JSON

### Common Test Scenarios

- ✅ Free course enrollment (no payment)
- ✅ Paid course purchase flow
- ✅ Payment cancellation
- ✅ Already enrolled user (should not show payment)
- ✅ Unauthenticated user (redirect to login)
- ✅ Payment failure handling
- ✅ Duplicate payment prevention

## Security Considerations

1. **API Keys Protection**
   - Never commit `.env` files
   - Use environment variables
   - Keep Client Secret secure

2. **Payment Verification**
   - All payments verified server-side
   - PayPal order capture on backend only
   - User authorization checked before enrollment

3. **HTTPS Required**
   - Production must use HTTPS
   - PayPal requires secure connections

4. **CORS Configuration**
   - Backend allows frontend origin
   - PayPal domains whitelisted

## Troubleshooting

### Payment Button Not Showing
- Check `VITE_PAYPAL_CLIENT_ID` in frontend `.env`
- Verify course has `isPaid: true` and valid `price`
- Check browser console for errors

### Payment Creation Fails
- Verify `PAYPAL_CLIENT_ID` and `PAYPAL_CLIENT_SECRET` in backend `.env`
- Check PayPal API credentials are valid
- Ensure `PAYPAL_MODE` matches credentials (sandbox/live)

### Payment Capture Fails
- Check backend logs for PayPal API errors
- Verify order was created successfully
- Ensure user hasn't already paid

### Enrollment Not Created
- Check payment status in database
- Verify transaction succeeded
- Look for errors in backend logs

## Production Deployment

1. **Switch to Live Mode**
   ```env
   PAYPAL_MODE=live
   PAYPAL_CLIENT_ID=<live_client_id>
   PAYPAL_CLIENT_SECRET=<live_client_secret>
   ```

2. **Update PayPal Base URL**
   - Automatically set based on `PAYPAL_MODE`
   - Live: `https://api-m.paypal.com`

3. **Security Checklist**
   - [ ] HTTPS enabled
   - [ ] Environment variables secured
   - [ ] Debug mode disabled
   - [ ] CORS properly configured
   - [ ] PayPal webhooks configured (optional)

## Future Enhancements

- [ ] PayPal webhook integration for async notifications
- [ ] Refund support
- [ ] Subscription-based courses
- [ ] Multiple payment methods (Stripe, etc.)
- [ ] Payment receipts via email
- [ ] Coupon/discount codes
- [ ] Payment analytics dashboard

## Support

For issues or questions:
- Check Django logs: `backend/nmtsa_lms/logs/`
- Browser console for frontend errors
- PayPal Developer Dashboard for transaction details
- Django Admin for payment records
