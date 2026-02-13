# GreenCloud - Production Login Credentials

## Default Users

After deployment, the following users are automatically created:

### Admin User
- **Email**: `admin@greencloud.local`
- **Password**: `admin123`
- **Role**: Administrator
- **Access**: Full system access including user management

### Demo User
- **Email**: `demo@greencloud.local`
- **Password**: `demo123`
- **Role**: Regular User
- **Access**: Standard user features

---

## ⚠️ IMPORTANT: Change Default Passwords!

For security, please change these default passwords immediately after first login:

1. Log in with the credentials above
2. Go to Profile Settings
3. Change your password

---

## Creating New Users

### Option 1: Self Registration
Users can register at: `/auth/register`

### Option 2: Admin Creation (Recommended for Production)
1. Log in as admin
2. Go to Admin Dashboard
3. Create users with custom credentials

---

## First Time Login

When you first access your Render deployment:

1. Go to: `https://your-app.onrender.com`
2. Use one of the credentials above
3. Upload your first file!

---

## Troubleshooting Login Issues

If login doesn't work:

1. **Check the logs** in Render dashboard
2. **Verify database was initialized** - Look for "Database tables created" in logs
3. **Clear browser cache** and try again
4. **Check if users were created** - Look for "Admin user created" in logs

---

## Security Notes

- Never commit real passwords to Git
- Always use environment variables for sensitive data in production
- Enable 2FA for admin accounts (feature coming soon)
- Regularly backup your database
