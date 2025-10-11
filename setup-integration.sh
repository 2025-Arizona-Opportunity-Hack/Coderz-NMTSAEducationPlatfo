#!/bin/bash
# Setup script for NMTSA LMS Integration

set -e  # Exit on error

echo "=========================================="
echo "NMTSA LMS - Frontend-Backend Integration"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

echo "Step 1: Installing backend dependencies..."
cd backend/nmtsa_lms
if command -v uv &> /dev/null; then
    echo "Using uv to install dependencies..."
    uv sync
else
    echo "Using pip to install dependencies..."
    pip install -e .
fi

echo ""
echo "Step 2: Creating database migrations..."
python manage.py makemigrations
python manage.py migrate

echo ""
echo "Step 3: Creating admin user..."
echo "Please create an admin user for testing:"
python manage.py shell << EOF
from authentication.models import User

# Check if admin user already exists
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='admin123',
        role='admin',
        onboarding_complete=True,
        first_name='Admin',
        last_name='User'
    )
    print("✓ Admin user created successfully!")
    print("  Username: admin")
    print("  Password: admin123")
else:
    print("✓ Admin user already exists")
    
EOF

echo ""
echo "Step 4: Installing frontend dependencies..."
cd ../../frontend
if command -v pnpm &> /dev/null; then
    echo "Using pnpm to install dependencies..."
    pnpm install
elif command -v npm &> /dev/null; then
    echo "Using npm to install dependencies..."
    npm install
else
    echo "Error: Neither npm nor pnpm found. Please install Node.js"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ Setup completed successfully!"
echo "=========================================="
echo ""
echo "To start the development servers:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend/nmtsa_lms"
echo "  python manage.py runserver"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then visit:"
echo "  Frontend: http://localhost:5173"
echo "  Admin Login: http://localhost:5173/admin-login"
echo "  API: http://localhost:8000/api/"
echo ""
echo "Admin credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo "=========================================="
