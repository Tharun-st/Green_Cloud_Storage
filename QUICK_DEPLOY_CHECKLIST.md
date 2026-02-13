# ✅ Quick Deploy Checklist

Follow these steps to get your GreenCloud app live in ~15 minutes!

---

## 🎯 Pre-Deployment Checklist

- [ ] **GitHub account created** → [Sign up](https://github.com/join)
- [ ] **Render account created** → [Sign up](https://render.com/register)
- [ ] **Git installed on your computer** → [Download](https://git-scm.com/downloads)

---

## 📤 Step 1: Push to GitHub (5 minutes)

### 1.1 Create Repository on GitHub
1. Go to [github.com/new](https://github.com/new)
2. Repository name: `greencloud` (or your choice)
3. Set to **Public** or **Private** (both work)
4. **Don't** initialize with README (you already have files)
5. Click **"Create repository"**

### 1.2 Push Your Code

Open terminal/command prompt in your project folder:

```bash
# Initialize git (if not done)
git init

# Add all files
git add .

# Make first commit
git commit -m "Initial commit - GreenCloud app"

# Add GitHub as remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/greencloud.git

# Push to GitHub
git branch -M main
git push -u origin main
```

✅ **Checkpoint**: Your code is now on GitHub!

---

## 🚀 Step 2: Deploy on Render (10 minutes)

### 2.1 Connect GitHub to Render
1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Sign in with GitHub (easiest) or email
3. If using email, you'll need to connect GitHub:
   - Settings → Connected Accounts → Connect GitHub

### 2.2 Create Web Service
1. Click **"New +"** button (top right)
2. Select **"Web Service"**
3. Click **"Connect a repository"** or **"Configure account"**
4. Find and select your `greencloud` repository
5. Click **"Connect"**

### 2.3 Configure Service

Render will show a form. Most settings are auto-detected from `render.yaml`:

| Setting | Value |
|---------|-------|
| **Name** | `greencloud` (or customize) |
| **Region** | Oregon (or closest to you) |
| **Branch** | `main` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Plan** | **Free** |

**Environment Variables** (Optional - already in render.yaml):
- Click "Advanced" if you want to customize
- Or leave as-is (auto-configured)

### 2.4 Create Service
Click **"Create Web Service"** button at the bottom

---

## ⏳ Step 3: Wait for Build (5-10 minutes)

You'll see a build log streaming:

```
==> Building...
==> Installing dependencies
==> Starting gunicorn
==> Your service is live 🎉
```

✅ **Checkpoint**: Build completed successfully!

---

## 🎉 Step 4: Access Your App!

Your URL will be shown at the top:
```
https://greencloud.onrender.com
```
(or whatever name you chose)

### First Visit:
1. Click the URL
2. You'll see the login page
3. Click "Register" to create your first account
4. Start using your cloud storage!

---

## 🔧 Common Issues & Fixes

### ❌ Build Failed
**Check**: Build logs for error messages
**Fix**: Ensure all files are pushed to GitHub

### ❌ App shows "Application Error"
**Check**: Logs tab in Render dashboard
**Fix**: Verify database folder was created (check disk settings)

### ❌ App is slow/sleeping
**Expected**: Free tier sleeps after 15 min inactivity
**Wake time**: ~30 seconds on first request
**Fix**: Upgrade to paid ($7/mo) or use UptimeRobot to ping every 10 min

---

## 🔄 Making Updates Later

After your app is deployed, updates are automatic:

```bash
# Make changes to your code
# Then:
git add .
git commit -m "Description of changes"
git push origin main

# Render automatically rebuilds and deploys!
```

---

## 📱 Test Your App

Try these to verify everything works:

- [ ] Can access the public URL
- [ ] Can register a new account
- [ ] Can login
- [ ] Can upload a file
- [ ] Can download a file
- [ ] File persists after browser refresh

---

## 🎊 You're Done!

Your GreenCloud app is now:
- ✅ Live on the internet
- ✅ Accessible via HTTPS
- ✅ Auto-deploying from GitHub
- ✅ Running in production mode

---

## 🆘 Need Help?

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **GitHub Issues**: Create an issue in your repo

---

## 📈 Next Steps (Optional)

- [ ] Set up custom domain
- [ ] Configure environment variables for production
- [ ] Set up monitoring with UptimeRobot
- [ ] Upgrade to paid plan for 24/7 uptime
- [ ] Add CI/CD tests before deployment

---

**Happy Deploying! 🚀**
