# 🚀 Deploy GreenCloud to Render

## What You'll Get
- **Permanent Public URL**: `https://greencloud.onrender.com` (or your custom name)
- **Free Hosting**: Runs 24/7 (sleeps after 15 min inactivity on free tier)
- **Auto-Deploy**: Push to GitHub → Auto updates
- **HTTPS**: Secure by default

---

## 📋 Prerequisites

1. **GitHub Account** - [Sign up free](https://github.com/join)
2. **Render Account** - [Sign up free](https://render.com/register)
3. Your code needs to be on GitHub

---

## 🎯 Step-by-Step Deployment

### Step 1: Push Your Code to GitHub

If you haven't already:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - GreenCloud ready for deployment"

# Create a new repository on GitHub (via website)
# Then connect and push:
git remote add origin https://github.com/YOUR_USERNAME/greencloud.git
git branch -M main
git push -u origin main
```

---

### Step 2: Deploy on Render

1. **Go to Render Dashboard**
   - Visit: [https://dashboard.render.com](https://dashboard.render.com)
   - Sign in with GitHub

2. **Create New Web Service**
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository
   - Select your `greencloud` repository

3. **Configure the Service**
   
   Render will auto-detect the `render.yaml` file! You'll see:
   
   - **Name**: `greencloud` (or change it)
   - **Region**: Oregon (or closest to you)
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free

4. **Environment Variables** (Auto-configured)
   
   These are already set in `render.yaml`:
   - `PYTHON_VERSION`: 3.11.0
   - `SECRET_KEY`: Auto-generated
   - `FLASK_ENV`: production

5. **Click "Create Web Service"**

---

### Step 3: Wait for Deployment

- First deploy takes ~5-10 minutes
- Watch the build logs in real-time
- When you see "Your service is live 🎉" → You're done!

---

### Step 4: Access Your App

Your app will be available at:
```
https://greencloud.onrender.com
```
(or whatever name you chose)

---

## 🔧 Important Configuration Notes

### Database Persistence

The `render.yaml` includes a persistent disk mounted at `/opt/render/project/src/database`:
- Your SQLite database persists across deploys
- 1GB free storage included

### First Time Setup

When you first visit your app:
1. The database will be auto-created
2. You can register a new account
3. Start using your cloud storage!

---

## 📊 Free Tier Limitations

- **Sleep After Inactivity**: App sleeps after 15 minutes of no requests
- **Wake-Up Time**: ~30 seconds to wake up when someone visits
- **Bandwidth**: 100GB/month
- **Build Time**: 400 minutes/month

**To keep it awake 24/7**: Upgrade to paid plan ($7/month) or use a service like [UptimeRobot](https://uptimerobot.com) to ping your app every 10 minutes.

---

## 🔄 Updating Your App

After deployment, updates are automatic:

```bash
# Make your changes locally
git add .
git commit -m "Updated feature X"
git push origin main
```

Render automatically detects the push and redeploys! ✨

---

## 🛠️ Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Ensure all dependencies are in `requirements.txt`

### App Won't Start
- Check the logs in Render dashboard
- Verify `gunicorn app:app` command is correct

### Database Issues
- Ensure the disk is properly mounted
- Check that `database/` folder exists

### Port Issues
- Render uses port 10000 by default
- Our `gunicorn_config.py` handles this automatically

---

## 🎉 Success!

You now have:
- ✅ Public URL accessible from anywhere
- ✅ HTTPS security
- ✅ Auto-deployments from GitHub
- ✅ Professional production hosting

---

## 🔗 Useful Links

- **Render Dashboard**: https://dashboard.render.com
- **Render Docs**: https://render.com/docs
- **Your Logs**: Check in Render dashboard → Your service → Logs tab

---

## 💡 Optional: Custom Domain

Want `storage.yourdomain.com` instead of `greencloud.onrender.com`?

1. Go to your service settings in Render
2. Click "Custom Domains"
3. Add your domain
4. Update your DNS records as instructed
5. Render provides free SSL certificates!

---

**Need help?** Check the Render documentation or their community forum!
