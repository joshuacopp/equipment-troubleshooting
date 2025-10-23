# DEPLOYMENT CHECKLIST

## ✅ Step-by-Step Deployment Guide

### 1. Update GitHub Repository

Upload these files to your GitHub repo (replace old ones):
- [ ] app.py
- [ ] models.py
- [ ] init_db.py
- [ ] requirements.txt
- [ ] decision_tree.yaml
- [ ] README.md
- [ ] templates/ folder (with all 6 HTML files)

### 2. Configure Render Environment Variables

Go to Render → Your Service → Environment

Add these 4 environment variables:

**DATABASE_URL** (required)
```
postgresql://postgres:[YOUR_PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
```
☝️ Use your actual Supabase connection string!

**SECRET_KEY** (required)
```
put-a-long-random-string-here-for-security
```
☝️ Generate a random string (30+ characters)

**ADMIN_USERNAME** (optional, defaults to "admin")
```
admin
```

**ADMIN_PASSWORD** (optional, defaults to "changeme")  
```
your-secure-password
```
☝️ CHANGE THIS! Don't use the default!

Click "Save Changes" after adding all variables.

### 3. Wait for Deployment

Render will automatically deploy when you:
- Push to GitHub, OR
- Save environment variables

Watch the logs - wait for "Deploy live 🎉"

### 4. Initialize Database (ONE TIME ONLY!)

After first deployment:

1. Go to your Render service
2. Click the **"Shell"** tab at the top
3. Type this command and press Enter:
   ```bash
   python init_db.py
   ```
4. Wait for it to complete (should see "✅ Migration complete!")

**IMPORTANT**: Only run this ONCE! Running it again will wipe your database.

### 5. Test Everything

**Test user-facing app:**
- [ ] Visit your app URL
- [ ] Click "Start Troubleshooting"
- [ ] Go through a few questions
- [ ] Verify answers work correctly

**Test admin interface:**
- [ ] Go to `/admin/login`
- [ ] Log in with your credentials
- [ ] Try adding a new question
- [ ] Try editing an existing question
- [ ] Try adding an answer

### 6. Customize

Now you can:
- Edit questions through the admin interface
- Add new troubleshooting paths
- Organize by categories
- Delete the old YAML workflows

## 🔧 Quick Reference

**Your App URL:**
```
https://your-app-name.onrender.com
```

**Admin Login:**
```
https://your-app-name.onrender.com/admin/login
```

**If Something Goes Wrong:**

1. Check Render logs for errors
2. Verify DATABASE_URL is correct in environment variables
3. Make sure init_db.py was run successfully
4. Check Supabase dashboard to see if tables were created

## 📝 After Deployment

Once everything works:
- [ ] Change admin password (in environment variables)
- [ ] Test on mobile devices
- [ ] Share URL with your team
- [ ] Train team on using admin interface
- [ ] Consider deleting decision_tree.yaml from GitHub (data is now in database)

## 🆘 Common Issues

**"Question 'start' not found"**
→ Run init_db.py to create initial questions

**"Can't connect to database"**
→ Check DATABASE_URL environment variable

**"Invalid credentials" when logging into admin**
→ Check ADMIN_USERNAME and ADMIN_PASSWORD environment variables

**Changes not saving**
→ Check Supabase dashboard to verify database connection is working

---

You're all set! Enjoy your new database-powered troubleshooting tool! 🎉
