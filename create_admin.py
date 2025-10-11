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
