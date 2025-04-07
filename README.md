# MealPrepPlanner
Python script to make a meal prep plan that is sent to email

Before Running:
-pip install selenium beautifulsoup4
-Download ChromeDriver (matching your Chrome version):
  👉 https://sites.google.com/chromium.org/driver/
  
  Place the downloaded chromedriver in the same folder as your Python app
- 🔐 Generate a Gmail App Password:
Go to your Google Account Security page.

Under "Signing in to Google", enable 2-Step Verification if you haven’t already.

After that, a new option will appear: App passwords.

Click App passwords.

Choose:

App: "Mail"

Device: "Other" → Name it something like "MealPrepApp"

Google will generate a 16-character password. Copy it.

🔁 Use that password in your app:
Go back to your Meal Prep Scheduler:

Open Settings

Paste the App Password (not your normal Gmail password) when it asks for the Gmail password
- create a file gmail_credentials.txt
      format like:
        your_email@gmail.com
        your_app_password
  ![image](https://github.com/user-attachments/assets/c4b03fc4-cef2-4dca-96f9-9bcd1a5f8335)
