# Deployment Guide

This guide walks you through deploying Crate Digging to the internet using free tiers.

## Architecture

- **Frontend**: Vercel (free tier) - hosts the Vue.js static site
- **Backend**: Render (free tier) - hosts the FastAPI Python backend

## Prerequisites

1. A GitHub account (to host your code)
2. A Vercel account (sign up at https://vercel.com - free with GitHub)
3. A Render account (sign up at https://render.com - free with GitHub)

## Step 1: Push to GitHub

First, create a new repository on GitHub and push your code:

```bash
cd /home/robert/Projects/crate-digging
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/crate-digging.git
git push -u origin main
```

## Step 2: Deploy Backend to Render

1. Go to https://render.com and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `crate-digging-api`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Select the **Free** plan
6. Click **"Create Web Service"**

Wait for the deployment to complete. Your backend URL will be something like:
`https://crate-digging-api.onrender.com`

**Note**: On the free tier, the service sleeps after 15 minutes of inactivity. The first request after sleeping takes ~30 seconds to wake up.

## Step 3: Deploy Frontend to Vercel

1. Go to https://vercel.com and sign in
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure the project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
5. Add Environment Variable:
   - **Name**: `VITE_API_URL`
   - **Value**: Your Render backend URL (e.g., `https://crate-digging-api.onrender.com`)
6. Click **"Deploy"**

Your frontend will be live at something like:
`https://crate-digging.vercel.app`

## Step 4: Update Backend CORS (Optional)

If you want to restrict CORS to only your frontend domain:

1. Go to your Render dashboard
2. Select your backend service
3. Go to **Environment** tab
4. Add variable:
   - **Key**: `FRONTEND_URL`
   - **Value**: Your Vercel URL (e.g., `https://crate-digging.vercel.app`)
5. Click **"Save Changes"** - the service will redeploy

## Cost Summary

| Service | Tier | Cost | Limitations |
|---------|------|------|-------------|
| Vercel | Hobby | **Free** | 100GB bandwidth/month |
| Render | Free | **Free** | Sleeps after 15min inactivity |

**Total: $0/month** for hobby/personal use!

## Upgrading (If Needed)

If your app gets popular:

- **Render Starter** ($7/month): No sleep, better performance
- **Vercel Pro** ($20/month): More bandwidth, team features

## Troubleshooting

### Backend sleeping on Render
The free tier sleeps after 15 minutes. First request takes ~30s to wake up. This is normal.

### CORS errors
Make sure your `VITE_API_URL` in Vercel matches your Render URL exactly (including `https://`).

### Build failures
Check that all dependencies are listed in `requirements.txt` (backend) and `package.json` (frontend).

## Local Development After Deployment

To run locally after deployment:

```bash
# Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload

# Frontend (in new terminal)
cd frontend
npm run dev
```

The frontend will use `http://localhost:8000` by default for local development.
