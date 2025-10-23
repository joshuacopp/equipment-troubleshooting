# Equipment Troubleshooting Tool - PostgreSQL Version

A Flask web application with PostgreSQL database and admin interface for managing troubleshooting decision trees.

## What's New

- ✅ **PostgreSQL database** instead of YAML
- ✅ **Admin interface** at `/admin` for managing questions
- ✅ **Supabase integration** for cloud database
- ✅ **Scalable** - handles thousands of questions easily
- ✅ **User-friendly** - edit questions through web forms

## Files

- **app.py** - Main Flask application with admin routes
- **models.py** - Database models (Question and Answer tables)
- **init_db.py** - Database initialization and YAML migration script
- **decision_tree.yaml** - Your existing questions (for migration)
- **templates/** - HTML templates (user-facing and admin)
- **requirements.txt** - Python dependencies

## Deployment to Render with Supabase

### Step 1: Set Up Supabase Database

You already have this! Your connection string:
```
postgresql://postgres:[YOUR_PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
```

### Step 2: Push Code to GitHub

1. Delete your old files from GitHub repo
2. Upload all these new files:
   - app.py
   - models.py
   - init_db.py
   - requirements.txt
   - templates/ (entire folder with all HTML files)
   - decision_tree.yaml (for initial migration)

### Step 3: Configure Render

1. Go to your Render service
2. Click **"Environment"** in the left sidebar
3. Add these environment variables:

**DATABASE_URL**
```
postgresql://postgres:[YOUR_PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
```
(Replace with your actual Supabase connection string)

**SECRET_KEY**
```
your-random-secret-key-here-make-it-long-and-random
```
(Generate a random string - this secures sessions)

**ADMIN_USERNAME** (optional, defaults to "admin")
```
admin
```

**ADMIN_PASSWORD** (optional, defaults to "changeme")
```
your-secure-password-here
```

4. Click "Save Changes"

### Step 4: Initialize Database (ONE TIME ONLY)

After your first deployment completes:

1. In Render, go to your service
2. Click **"Shell"** tab at the top
3. Run this command:
```bash
python init_db.py
```

This will:
- Create the database tables
- Migrate your YAML data to PostgreSQL
- Set everything up

You only need to do this ONCE!

### Step 5: Test It

1. Visit your app URL: `https://your-app.onrender.com`
2. Test the troubleshooting flow
3. Visit `/admin/login` and log in with your admin credentials
4. Try adding/editing questions

## Using the Admin Interface

### Accessing Admin

Go to: `https://your-app.onrender.com/admin/login`

Default credentials:
- Username: `admin`
- Password: `changeme` (or whatever you set in environment variables)

### Managing Questions

1. **View All Questions**: Dashboard shows all questions organized by category
2. **Add Question**: Click "Add New Question" button
3. **Edit Question**: Click "Edit" on any question
4. **Add Answers**: After creating a question, add answer options
5. **Delete**: Remove questions/answers you don't need

### Question Structure

Each question needs:
- **Question ID**: Unique identifier (e.g., `start`, `brush_check`)
- **Question Text**: What users see
- **Category**: Optional grouping

Each answer needs:
- **Answer Text**: The option users select
- **Either**:
  - **Next Question ID**: To continue the flow, OR
  - **Conclusion**: To end with a diagnosis/solution

### Tips

- Start with question ID: `start` (this is the entry point)
- Use descriptive IDs: `check_motor_temp` not `q1`
- Categories help organize long lists: "Brush", "Chemical", "HP"
- You can link back to earlier questions to create loops if needed

## Local Development

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export DATABASE_URL="postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres"

# Initialize database (first time only)
python init_db.py

# Run app
python app.py
```

Visit: `http://localhost:5000`

## Database Schema

### questions table
- id (primary key)
- question_id (unique string)
- text
- category
- created_at

### answers table
- id (primary key)
- question_id (foreign key)
- text
- next_question_id (nullable)
- conclusion (nullable)
- order
- created_at

## Troubleshooting

**App won't start?**
- Check that DATABASE_URL is set in Render environment variables
- Make sure you ran `init_db.py` to create tables

**"Question not found" error?**
- Make sure you have a question with ID "start"
- Check admin dashboard to see all questions

**Can't log into admin?**
- Check ADMIN_USERNAME and ADMIN_PASSWORD environment variables
- Default is admin/changeme

**Want to reset database?**
- Run `init_db.py` again - it will clear and reimport from YAML
- Or delete data directly in Supabase dashboard

**Changes not showing?**
- Clear browser cache (Ctrl+Shift+R)
- Check Render logs for errors

## Migration from YAML Version

If you were using the old YAML version:

1. Keep your `decision_tree.yaml` file
2. Deploy this new version
3. Run `init_db.py` - it will migrate your YAML data
4. After migration, you can delete `decision_tree.yaml` from your repo
5. All future changes happen through the admin interface

## Security Notes

**IMPORTANT:**
1. Change the default admin password immediately
2. Use a strong SECRET_KEY (long random string)
3. Don't commit environment variables to GitHub
4. Supabase connection string contains password - keep it secret

## Future Enhancements

Easy additions you could make:
- Photo uploads for specific issues
- User accounts with different permission levels
- Analytics on most common issues
- Export diagnostic reports as PDF
- Integration with work order systems
- Multiple equipment types in one app

## Support

Questions? Issues?
- Check Render logs for errors
- Check Supabase logs for database issues
- Test locally first before deploying

## License

Use this however you want for your company's internal tools!
