# Quick Test Guide - PayPal Sandbox Integration

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependency
```powershell
cd nmtsa_lms
uv pip install paypal-checkout-serversdk
```

### 2. Add Environment Variables
Add to your `.env` file in the root directory:
```env
PAYPAL_CLIENT_ID=your_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_sandbox_client_secret
PAYPAL_MODE=sandbox
```

Get these from: https://developer.paypal.com/dashboard/ → Apps & Credentials → Sandbox

### 3. Start Server
```powershell
python manage.py runserver
```

---

## 🧪 Testing Checklist

### Quick Test (Happy Path)
1. ✅ Login as teacher → Create paid course ($49.99)
2. ✅ Logout → Login as student
3. ✅ Go to catalog → Find the paid course
4. ✅ Click "Checkout"
5. ✅ See PayPal button appear (after loading)
6. ✅ Click PayPal button
7. ✅ Login with sandbox account in popup
8. ✅ Complete payment
9. ✅ See success message
10. ✅ Auto-redirect to course learning page

### PayPal Sandbox Test Account
- Email: Found in PayPal Dashboard → Sandbox → Accounts
- Password: Same location (click "View/Edit" on account)
- Use the **PERSONAL** account (buyer), not business

---

## 🎯 What to Look For

### ✅ Success Indicators
- PayPal button renders (gold/blue button)
- Popup opens with PayPal login
- Payment completes without errors
- Enrollment created in database
- Payment record created with status='completed'
- Course shows in "My Courses"

### ❌ Potential Issues
- Button doesn't show → Check console for errors, verify PAYPAL_CLIENT_ID
- "Failed to create order" → Check Django logs, verify credentials
- Payment succeeds but no enrollment → Check Django logs for transaction errors

---

## 🔍 Where to Find Test Accounts

**PayPal Developer Dashboard:**
https://developer.paypal.com/dashboard/accounts

**You'll see two accounts:**
1. **Business** (sb-xxxxx@business.example.com) - Merchant/Seller - DON'T USE THIS
2. **Personal** (sb-xxxxx@personal.example.com) - Buyer - USE THIS ONE

Click "View/Edit" to see password.

**Test Account Has:**
- Fake balance: ~$9,999
- Test credit card
- No real money involved

---

## 📊 Verify Success

### In Django Admin
1. Go to: http://localhost:8000/admin/
2. Check `Payments` - Should show new record with:
   - Status: completed
   - PayPal Order ID: populated
   - Payer Email: from sandbox account
3. Check `Enrollments` - Student enrolled in course

### In PayPal Dashboard
1. Go to: https://developer.paypal.com/dashboard/
2. Navigate to: Sandbox → Transactions
3. See your test payment listed

---

## 🔧 Common Commands

**Install dependency:**
```powershell
uv pip install paypal-checkout-serversdk
```

**Check if dependency installed:**
```powershell
uv pip list | Select-String paypal
```

**Run server:**
```powershell
cd nmtsa_lms
python manage.py runserver
```

**View logs:**
Check terminal where runserver is running - look for PayPal-related messages

---

## 💡 Testing Tips

1. **Use Incognito/Private Window** to test as different users
2. **Clear browser cache** if button doesn't load
3. **Check browser console** (F12) for JavaScript errors
4. **Check Django terminal** for backend errors
5. **Keep PayPal dashboard open** to verify transactions

---

## 🎬 Demo Flow for Presentation

1. Show catalog with paid course
2. Click checkout as student
3. Show clean PayPal integration (no card fields)
4. Click PayPal button → login appears
5. Complete test payment
6. Show successful enrollment
7. Show PayPal dashboard with transaction

**Time:** ~2 minutes for full demo

---

## 🆘 Quick Fixes

**Button not showing?**
- Check `.env` has PAYPAL_CLIENT_ID
- Restart Django server after adding .env variables
- Check browser console for errors

**"Order already captured" error?**
- This is normal if you retry same payment
- Just create a new test payment attempt

**Sandbox login fails?**
- Verify you're using correct sandbox account
- Check password in PayPal Dashboard → Accounts
- Try different sandbox account

---

## 📝 Environment File Template

```env
# Auth0 (existing)
AUTH0_DOMAIN=your_domain
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_secret

# PayPal Sandbox (new)
PAYPAL_CLIENT_ID=AYourSandboxClientIdHere123456
PAYPAL_CLIENT_SECRET=YourSandboxSecretHere123456
PAYPAL_MODE=sandbox

# Other settings (existing)
SUPERMEMORY_API_KEY=your_key
```

---

That's it! You're ready to test PayPal Sandbox integration. 🚀
