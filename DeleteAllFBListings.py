import tkinter as tk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tkinter import messagebox  
import time

class FacebookAutoDeleter:
    def __init__(self, root):
        self.root = root
        self.setup_gui()

    def setup_gui(self):
        self.root.title("Facebook Auto Deleter")
        
        # Set the size of the window
        window_width = 600  # Define the width
        window_height = 200  # Define the height
        
        # Get the screen dimension
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Find the center position
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        
        # Set the position of the window to the center of the screen
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Setup labels and entries for email and password
        tk.Label(self.root, text="Email:").pack()
        self.email_entry = tk.Entry(self.root)
        self.email_entry.pack()

        tk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        # Begin button setup
        self.begin_button = tk.Button(self.root, text="Begin", command=self.start_process)
        self.begin_button.pack()
        self.begin_button.config(state=tk.DISABLED)

        self.email_entry.bind("<KeyRelease>", self.check_input)
        self.password_entry.bind("<KeyRelease>", self.check_input)


    def check_input(self, event):
        if self.email_entry.get() and self.password_entry.get():
            self.begin_button.config(state=tk.NORMAL)
        else:
            self.begin_button.config(state=tk.DISABLED)

    def start_process(self):
        self.begin_button.config(state=tk.DISABLED)
        email = self.email_entry.get()
        password = self.password_entry.get()

        options = Options()
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument("--disable-notifications")

        driver = webdriver.Chrome(options=options)
        driver.get("https://www.facebook.com/")

        try:
            try:
                email_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='email']"))
                )
            except TimeoutException:
                print("Email input field not found.")
                return

            try:
                password_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='pass']"))
                )
            except TimeoutException:
                print("Password input field not found.")
                return

            try:
                login_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "login"))
                )
            except TimeoutException:
                print("Login button not found.")
                return

            email_input.send_keys(email)
            password_input.send_keys(password)
            login_button.click()

            # Assuming redirection to a new page is handled here
            time.sleep(5)  # Explicit wait to simulate page load, consider using WebDriverWait here as well
            driver.get("https://www.facebook.com/marketplace/you/selling")
            
            retry_count = 0
            while retry_count < 5:
                try:
                    time.sleep(5)            

                    print("Checking for items to delete...")
                    try:
                        items_collection = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Collection of your marketplace items']")))
                        print("Found items collection.")
                    except TimeoutException:
                        print("Didn't found items collection.")
                        return
                    try:

                        more_button = items_collection.find_element(By.XPATH, ".//div[@aria-label='More']")
                        print("Found 'More' button.")
                    except NoSuchElementException:
                        print("Didn't found 'More' button.")
                        return
                    time.sleep(2)
                    more_button.click()
                    print("Clicked 'More' for an item.")
                    time.sleep(5)

                    try:
                        delete_option = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Delete Listing')]")))                        
                        print("Found 'Delete listing' option.")
                        
                    except NoSuchElementException:
                        print("Didn't found 'Delete listing' option.")
                        return
                    time.sleep(2)
                    delete_option.click()
                    print("Delete option clicked.")
                    time.sleep(5)
        
                    try:
                        delete_confirm = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Delete'][@role='button' and not(@aria-disabled='true')]")))
                        print("Found 'Delete' button.")
                    except NoSuchElementException:
                        print("Didn't found 'Delete' button.")
                        return
                    time.sleep(2)
                    delete_confirm.click()
                    print("Confirmed deletion.")
                    time.sleep(5)

                    # Handle the sold item dialog if it appears
                    try:
                        if WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Did you sell this item?')]"))):
                            print("Handling 'Did you sell this item?' dialog...")
                            no_sold_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), \"No, haven't sold\")]"))
                            )
                            no_sold_button.click()
                            print("Clicked 'No, haven't sold'.")

                            time.sleep(5)
                            next_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Next']"))
                            )
                            next_button.click()
                            print("Clicked 'Next'.")
                            time.sleep(5)

                    except:
                        print("There's no 'Did you sell this item?' dialog...")

                    retry_count = 0
                    print("Waiting for page to stabilize after actions...")
                    driver.refresh()

                except TimeoutException:
                    retry_count += 1
                    driver.refresh()
                    print(f"Attempt {retry_count}: Retrying after Timeout...")
                except NoSuchElementException as e:
                    print(f"Element not found: {e}")
                    break

            if retry_count == 5:
                print("Final attempt failed due to timeout.")

        except Exception as e:
            tk.messagebox.showerror("Error", f"Unhandled exception: {str(e)}")
        finally:
            driver.quit()
            self.begin_button.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    app = FacebookAutoDeleter(root)
    root.mainloop()
