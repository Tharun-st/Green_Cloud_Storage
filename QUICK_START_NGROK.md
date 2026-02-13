# 🚀 Quick Start: Make Your App Public with ngrok

This is the **fastest way** to get a public link for your GreenCloud app!

## What is ngrok?

ngrok creates a secure tunnel from a public URL to your local computer. Perfect for:
- 🎯 Quick demos
- 🧪 Testing webhooks
- 👥 Sharing with friends
- 📱 Testing on mobile devices

## Steps

### 1. Download ngrok

Go to: [https://ngrok.com/download](https://ngrok.com/download)

Or download directly:
- **Windows**: [Download ZIP](https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip)

### 2. Extract and Run

1. Extract `ngrok.exe` to any folder (e.g., `C:\ngrok\`)
2. Open Command Prompt in that folder

### 3. Start Your Flask App

Your app is already running! Keep it running on port 5000.

### 4. Run ngrok

In a **new** Command Prompt window:

```cmd
cd C:\ngrok
ngrok http 5000
```

### 5. Get Your Public URL

You'll see something like:

```
ngrok

Session Status                online
Account                       Free (Sign up for more)
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123xyz.ngrok.io -> http://localhost:5000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**Your public link is:** `https://abc123xyz.ngrok.io`

### 6. Share Your Link!

Anyone can now access your app at that URL! 🎉

## Important Notes

⚠️ **Free Tier Limitations:**
- URL changes every time you restart ngrok
- 40 connections/minute limit
- Session expires after 2 hours

✅ **To Get a Permanent URL:**
1. Sign up at [ngrok.com](https://ngrok.com)
2. Get your auth token
3. Run: `ngrok config add-authtoken YOUR_TOKEN`
4. Use: `ngrok http 5000 --domain=your-custom-name.ngrok.io`

## Keep Both Running

You need **TWO** command prompts open:

**Terminal 1:** Your Flask app
```cmd
cd d:\Downloads\OneDrive\Desktop\cloud-storage-system-main
python app.py
```

**Terminal 2:** ngrok
```cmd
cd C:\ngrok
ngrok http 5000
```

## Monitoring

ngrok provides a web interface to see all requests:

Open in browser: `http://localhost:4040`

## Stop ngrok

Press `Ctrl+C` in the ngrok terminal.

---

**That's it!** You now have a public URL for your cloud storage system! 🌐
