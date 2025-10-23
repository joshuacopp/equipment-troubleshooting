# Equipment Troubleshooting Tool

A Flask-based web application for creating interactive decision trees to troubleshoot mechanical equipment.

## What You've Got

- **app.py** - Main Flask application
- **decision_tree.yaml** - Your troubleshooting logic (edit this to customize)
- **templates/** - HTML templates for the web interface
- **requirements.txt** - Python dependencies

## Quick Start (Local Testing)

### 1. Install Python
Make sure you have Python 3.8+ installed. Check with:
```bash
python --version
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
python app.py
```

Open your browser to: `http://localhost:5000`

## Customizing Your Decision Tree

Edit `decision_tree.yaml` to add your own troubleshooting logic. The structure is:

```yaml
questions:
  question_id:
    text: "Your question here?"
    answers:
      - text: "Answer option 1"
        next: next_question_id
      - text: "Answer option 2"
        conclusion: "Final diagnosis/solution"
```

### Key Rules:
- Each question needs a unique ID (like `start`, `motor_check`, etc.)
- Answers can either:
  - Lead to another question: `next: question_id`
  - End with a conclusion: `conclusion: "Your solution here"`
- Always start from the question with ID `start`

### Example Addition:
```yaml
  check_oil_level:
    text: "Is the oil level within normal range?"
    answers:
      - text: "Yes, oil level is normal"
        next: check_filter
      - text: "No, oil level is low"
        conclusion: "Add oil to proper level. Check for leaks if oil consumption is excessive."
```

## Deploying to Cloud (Render - Free)

### Option 1: Deploy to Render (Recommended)

1. **Create a GitHub account** (if you don't have one)
   - Go to github.com and sign up

2. **Create a new repository**
   - Click "New repository"
   - Name it something like "equipment-troubleshooting"
   - Make it private if you want
   - Don't initialize with README (you already have files)

3. **Upload your files to GitHub**
   
   If you have git installed:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```
   
   Or use GitHub's web interface to upload files directly.

4. **Deploy to Render**
   - Go to render.com and sign up (free)
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select your repository
   - Configure:
     - **Name**: equipment-troubleshooting (or whatever you want)
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
   - Click "Create Web Service"

5. **Add Gunicorn** (required for production)
   Add this line to your `requirements.txt`:
   ```
   gunicorn==21.2.0
   ```
   Commit and push the change.

6. **Access your app**
   - Render will give you a URL like: `https://equipment-troubleshooting.onrender.com`
   - Share this with your team!

### Important Notes for Production:

1. **Change the secret key** in `app.py`:
   ```python
   app.secret_key = 'your-secret-key-change-this-in-production'
   ```
   Generate a random string for this.

2. **Free tier limitations**:
   - App sleeps after 15 minutes of inactivity
   - First request after sleep takes ~30 seconds
   - 750 hours/month free (plenty for internal tools)

3. **To avoid sleep** (paid tier ~$7/month):
   - Upgrade to paid instance in Render dashboard

## Alternative Deployment Options

### Option 2: PythonAnywhere
1. Sign up at pythonanywhere.com (free tier available)
2. Upload your files
3. Configure a web app pointing to `app.py`
4. Access at: `your-username.pythonanywhere.com`

### Option 3: Railway
1. Sign up at railway.app
2. Deploy from GitHub
3. Similar to Render but different interface

## Troubleshooting

**App won't start locally?**
- Make sure Flask and PyYAML are installed: `pip install -r requirements.txt`
- Check that `decision_tree.yaml` exists in the same folder as `app.py`

**Changes to YAML not showing up?**
- Restart the Flask app (Ctrl+C, then `python app.py` again)
- On cloud platforms, push changes to GitHub and Render will auto-deploy

**Getting deployment errors?**
- Make sure `requirements.txt` includes all dependencies
- Check that `gunicorn` is in `requirements.txt` for production
- Verify your `decision_tree.yaml` syntax is valid (use a YAML validator online)

## Adding More Features

Want to add:
- **User authentication?** Add Flask-Login
- **Save diagnostic history?** Add a database (SQLite for simple, PostgreSQL for production)
- **Email reports?** Add Flask-Mail
- **Multiple equipment types?** Create multiple YAML files and add a selection screen

## File Structure
```
your-project/
├── app.py                 # Main Flask application
├── decision_tree.yaml     # Your troubleshooting logic
├── requirements.txt       # Python dependencies
├── templates/
│   ├── index.html        # Landing page
│   ├── question.html     # Question display
│   └── conclusion.html   # Results page
└── README.md             # This file
```

## Support

Questions? Issues? 
- Check Flask documentation: flask.palletsprojects.com
- Check Render documentation: render.com/docs
- YAML syntax: yaml.org

## License

Use this however you want for your company's internal tools!
