import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import os
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By  # Add this import
from time import sleep

# Configure WebDriver (make sure chromedriver is installed)
def scrape_ingredients(url):
    options = Options()
    options.headless = True  # Run headlessly (without a GUI)
    
    # Specify path to chromedriver using Service
    service = Service(executable_path='chromedriver.exe')  # Update this path with your chromedriver location
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get(url)
    sleep(2)  # Give time for the page to load

    ingredientTags = ['.custom .post .format_text ul li','.wprm-recipe-ingredients']

    try:
        for i in ingredientTags:
            # Use By.CSS_SELECTOR with the find_element method
            ingredients = driver.find_element(By.CSS_SELECTOR, i).text  # Update this with actual CSS selector
         
    except Exception as e:
        print(f"Error scraping ingredients: {e}")
        return None
    finally:
        driver.quit()
        
# Configure Days and Meals
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MEALS = ["Breakfast", "Lunch", "Dinner"]

class MealPrepApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weekly Meal Prep Scheduler")
        self.root.configure(bg="#f4f4f4")
        self.entries = {}
        self.urls = {}

        # Layout and design setup
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        title = tk.Label(root, text="🍽️ Meal Prep Scheduler", font=("Helvetica", 20, "bold"), bg="#f4f4f4", fg="#333")
        title.grid(row=0, column=0, pady=15)

        self.frame = tk.Frame(root, bg="#f4f4f4")
        self.frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        for col in range(3):
            self.frame.columnconfigure(col, weight=1)

        for i, day in enumerate(DAYS):
            row = i // 3
            col = i % 3
            day_frame = tk.LabelFrame(self.frame, text=day, padx=15, pady=10, bg="white", fg="#333", font=("Helvetica", 12, "bold"), bd=2, relief="groove")
            day_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            day_frame.columnconfigure(0, weight=1)
            self.entries[day] = {}
            self.urls[day] = {}

            for meal in MEALS:
                meal_label = tk.Label(day_frame, text=meal, bg="white", font=("Helvetica", 10, "bold"))
                meal_label.pack(anchor="w", pady=(5, 0))
                entry = ttk.Entry(day_frame)
                entry.pack(fill="x", pady=2)
                url_entry = ttk.Entry(day_frame)
                url_entry.pack(fill="x", pady=2)
                self.entries[day][meal] = entry
                self.urls[day][meal] = url_entry

        btn_frame = tk.Frame(root, bg="#f4f4f4")
        btn_frame.grid(row=2, column=0, pady=20)

        save_btn = tk.Button(btn_frame, text="💾 Save Meal Plan", command=self.save_meals, bg="#4CAF50", fg="white", padx=20, pady=10, font=("Helvetica", 12, "bold"))
        save_btn.pack(side="left", padx=10)

        load_btn = tk.Button(btn_frame, text="📂 Load Meal Plan", command=self.load_meals, bg="#2196F3", fg="white", padx=20, pady=10, font=("Helvetica", 12, "bold"))
        load_btn.pack(side="left", padx=10)

        email_btn = tk.Button(btn_frame, text="📧 Email Meal Plan", command=self.email_meal_plan, bg="#FF9800", fg="white", padx=20, pady=10, font=("Helvetica", 12, "bold"))
        email_btn.pack(side="left", padx=10)

    def save_meals(self):
        meal_plan = {day: {meal: self.entries[day][meal].get() for meal in MEALS} for day in DAYS}
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"Meal_Plan_{now}.txt"
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        filepath = os.path.join(desktop, filename)

        with open(filepath, "w") as f:
            f.write("Weekly Meal Plan\n\n")
            for day, meals in meal_plan.items():
                f.write(f"{day}:\n")
                for meal, dish in meals.items():
                    f.write(f"  {meal}: {dish}\n")
                    url = self.urls[day][meal].get()
                    if url:
                        f.write(f"  Recipe URL: {url}\n")
                f.write("\n")

        messagebox.showinfo("Meal Plan Saved", f"Meal plan saved to:\n{filepath}")
        print(f"Meal plan saved to: {filepath}")

    def load_meals(self):
        file_path = filedialog.askopenfilename(title="Open Meal Plan", filetypes=[("Text Files", "*.txt")])
        if not file_path:
            return

        try:
            with open(file_path, "r") as f:
                lines = f.readlines()

            current_day = None
            current_meal = None
            for line in lines:
                line = line.strip()
                if line.endswith(":") and line[:-1] in DAYS:
                    current_day = line[:-1]
                elif current_day and any(line.startswith(f"{meal}:") for meal in MEALS):
                    for meal in MEALS:
                        if line.startswith(f"{meal}:"):
                            value = line.split(":", 1)[1].strip()
                            self.entries[current_day][meal].delete(0, tk.END)
                            self.entries[current_day][meal].insert(0, value)
                elif "Recipe URL" in line:
                    url = line.split(":", 1)[1].strip()
                    self.urls[current_day][meal].delete(0, tk.END)
                    self.urls[current_day][meal].insert(0, url)

            messagebox.showinfo("Success", f"Meal plan loaded from:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load meal plan:\n{str(e)}")

    def email_meal_plan(self):
        meal_plan = {day: {meal: self.entries[day][meal].get() for meal in MEALS} for day in DAYS}
        email = self.get_email_credentials()
        if not email:
            return

        # Compose the HTML email content
        email_content = "<h1>Weekly Meal Plan</h1>"
        for day, meals in meal_plan.items():
            email_content += f"<h2>{day}</h2>"
            for meal, dish in meals.items():
                email_content += f"<p><b>{meal}</b>: {dish}</p>"
                url = self.urls[day][meal].get()
                if url:
                    email_content += f"<p>Recipe URL: <a href='{url}'>{url}</a></p>"
                    ingredients = scrape_ingredients(url)
                    if ingredients:
                        email_content += f"<p><b>Ingredients:</b><br>{ingredients}</p>"

        # Send the email
        self.send_email(email, email_content)

    def get_email_credentials(self):
        # Read the username and password from a text file
        try:
            with open("email_credentials.txt", "r") as f:
                username = f.readline().strip()
                password = f.readline().strip()
            return username, password
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load email credentials: {str(e)}")
            return None

    def send_email(self, email, email_content):
        username, password = email

        # Set up the server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        try:
            server.login(username, password)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to log in: {str(e)}")
            return

        # Compose the email
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = username
        msg['Subject'] = "Weekly Meal Plan"
        msg.attach(MIMEText(email_content, 'html'))

        # Send the email
        try:
            server.sendmail(username, username, msg.as_string())
            messagebox.showinfo("Email Sent", "Meal plan sent successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {str(e)}")
        finally:
            server.quit()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1000x750")
    app = MealPrepApp(root)
    root.mainloop()
