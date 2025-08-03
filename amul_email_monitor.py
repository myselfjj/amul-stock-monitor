#!/usr/bin/env python3
"""
🚀 Amul Stock Monitor - Headless Server Version
Monitors Amul product stock availability and sends email notifications.
Optimized for 24/7 server deployment with headless Chrome.
"""

import smtplib
import time
import json
import schedule
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import logging

# Configure logging for server deployment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('amul_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Configuration ---
CONFIG_FILE = "email_config.json"
NOTIFIED_PRODUCTS_CACHE = {}

# --- High-Accuracy Stock Checking Function ---
def check_stock(driver, product):
    """
    Checks if a product is in stock by looking for "Sold Out" text specific to the product name from config.
    Uses the exact product name from config file to target the right "Sold Out" text.
    """
    try:
        driver.get(product['url'])
        logger.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking: {product['url'].split('/')[-1]}")
        
        # Wait for page to fully load (pincode is already set site-wide)
        logger.info("Waiting for page to fully load...")
        time.sleep(3)
        
        # Primary check: Look for the main product's Add to Cart button area
        try:
            logger.info(f"Checking stock status for product: {product['name']}")
            
            # Step 1: Find the main "Add to Cart" button (there should be only one main one)
            main_cart_button = None
            cart_buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Add to Cart') or contains(text(), 'ADD TO CART')]")
            
            # Find the main cart button (usually the longest text and most prominent)
            main_button_candidates = []
            for btn in cart_buttons:
                if btn.is_displayed():
                    btn_text = btn.text.strip()
                    if btn_text and 'add to cart' in btn_text.lower():
                        main_button_candidates.append(btn)
            
            if main_button_candidates:
                # Take the first main cart button (usually the primary one)
                main_cart_button = main_button_candidates[0]
                logger.info(f"✅ Found main Add to Cart button: '{main_cart_button.text.strip()}'")
                
                # Step 2: Check the area around the main cart button for "Sold Out" indicators
                try:
                    # Get the parent container of the Add to Cart button
                    button_container = main_cart_button.find_element(By.XPATH, "./ancestor::div[position() <= 3]")  # Check up to 3 levels up
                    
                    # Look for "Sold Out" text in the same container as the main cart button
                    nearby_sold_out = button_container.find_elements(By.XPATH, ".//*[contains(text(), 'Sold Out') or contains(text(), 'SOLD OUT')]")
                    
                    if nearby_sold_out:
                        # Check if any sold out text is actually for this product
                        for sold_elem in nearby_sold_out:
                            if sold_elem.is_displayed():
                                sold_text = sold_elem.text.strip()
                                logger.info(f"Found 'Sold Out' near cart button: '{sold_text}'")
                                
                                # If sold out text is very close to the cart button, it's likely for this product
                                try:
                                    # Check if sold out element is within reasonable distance of cart button
                                    sold_location = sold_elem.location
                                    cart_location = main_cart_button.location
                                    
                                    # If they're vertically close (within 200px), likely same product
                                    if abs(sold_location['y'] - cart_location['y']) < 200:
                                        logger.info("❌ Status: OUT OF STOCK (Found 'Sold Out' near main cart button)")
                                        return False
                                except:
                                    # If we can't get location, be conservative and assume sold out
                                    logger.info("❌ Status: OUT OF STOCK (Found 'Sold Out' near cart button - location check failed)")
                                    return False
                    
                    logger.info("No 'Sold Out' found near main cart button")
                    
                except Exception as e:
                    logger.error(f"Error checking button container: {e}")
                
                # Step 3: Alternative check - see if the main cart button itself indicates stock status
                try:
                    button_disabled = main_cart_button.get_attribute('disabled')
                    button_class = main_cart_button.get_attribute('class') or ''
                    
                    logger.info(f"Cart button - Disabled: '{button_disabled}', Class: '{button_class}'")
                    
                    # If button is explicitly disabled and has sold-out related classes
                    if button_disabled == "true" and any(indicator in button_class.lower() for indicator in ['sold', 'out', 'unavailable', 'disabled']):
                        # Double-check by looking for sold out text specifically in the product title area
                        try:
                            product_name = product['name']
                            title_elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{product_name}')]")
                            
                            for title_elem in title_elements:
                                if title_elem.is_displayed() and len(title_elem.text.strip()) > 20:  # Likely the main title
                                    # Check for sold out in the title's parent area
                                    title_area = title_elem.find_element(By.XPATH, "./ancestor::div[position() <= 2]")
                                    title_sold_out = title_area.find_elements(By.XPATH, ".//*[contains(text(), 'Sold Out') or contains(text(), 'SOLD OUT')]")
                                    
                                    if title_sold_out:
                                        for sold in title_sold_out:
                                            if sold.is_displayed():
                                                logger.info(f"❌ Status: OUT OF STOCK (Found 'Sold Out' in title area: '{sold.text.strip()}')")
                                                return False
                                    break
                        except:
                            pass
                    
                    # If we reach here, no clear sold out indicators found
                    logger.info("✅ Status: IN STOCK (No clear sold out indicators found)")
                    return True
                    
                except Exception as e:
                    logger.error(f"Error checking button attributes: {e}")
            
            else:
                logger.info("❌ Could not find main Add to Cart button")
                # Fallback: if no cart button found, might be sold out
                return False
                
        except Exception as e:
            logger.error(f"Error in stock detection: {e}")
        
    except Exception as e:
        logger.error(f"An unexpected error occurred while checking stock: {e}")
        return False

# --- Email Notification Function (Modified to support multiple recipient email addresses) ---
def send_email(config, product):
    """Sends an email notification for a restocked product to multiple recipients."""
    sender_email = config['email']['sender_email']
    sender_password = config['email']['sender_password']
    recipient_emails = config['email']['recipient_emails']  # Now supports multiple emails
    
    subject = f"🎉 STOCK ALERT: {product['name']} is Back in Stock!"
    body = f"""
    Hello,

    Great news! The product you are monitoring is now available for purchase.

    📦 Product: {product['name']}
    💰 Price: {product['price']}
    📍 Pincode: {config['pincode']}
    
    🛒 Order now:
    {product['url']}

    ⚡ This is an automated alert from your Amul Stock Monitor.
    Act fast - items may go out of stock quickly!

    Happy Shopping! 🛍️
    - Your Amul Stock Monitor Bot 🤖
    """
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Send to all recipients
        successful_sends = 0
        failed_sends = 0
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:  # Use SMTP with starttls
            server.starttls()  # Enable encryption
            server.login(sender_email, sender_password)
            
            for recipient in recipient_emails:
                try:
                    msg['To'] = recipient  # Set individual recipient
                    server.send_message(msg)
                    logger.info(f"📧 ✅ Email sent successfully to: {recipient}")
                    successful_sends += 1
                    del msg['To']  # Remove for next iteration
                except Exception as e:
                    logger.error(f"📧 ❌ Failed to send email to {recipient}: {e}")
                    failed_sends += 1
        
        # Summary
        total_recipients = len(recipient_emails)
        logger.info(f"📧 📊 Email Summary: {successful_sends}/{total_recipients} sent successfully")
        if successful_sends > 0:
            logger.info(f"📧 🎉 Stock alert notification sent for {product['name']}")
        
        return successful_sends > 0  # Return True if at least one email was sent
        
    except Exception as e:
        logger.error(f"🚨 Failed to send emails. Error: {e}")
        return False

# --- Main Monitoring Job ---
def run_monitor():
    logger.info("\n--- Starting Amul Stock Monitor Cycle ---")
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.error(f"FATAL: Config file '{CONFIG_FILE}' not found.")
        return

    chrome_options = Options()
    # 🚀 HEADLESS MODE ENABLED for 24/7 server deployment
    chrome_options.add_argument("--headless=new")  # Enable new headless mode
    chrome_options.add_argument("--no-sandbox")  # Required for server environments
    chrome_options.add_argument("--disable-dev-shm-usage")  # Optimize shared memory usage
    chrome_options.add_argument("--disable-gpu")  # Disable GPU for headless
    chrome_options.add_argument("--disable-extensions")  # Disable extensions for performance
    chrome_options.add_argument("--disable-web-security")  # Bypass CORS for automation
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
    chrome_options.add_argument("--no-first-run")  # Skip first run experience
    chrome_options.add_argument("--disable-background-timer-throttling")  # Prevent throttling
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")  # Keep windows active
    chrome_options.add_argument("--disable-renderer-backgrounding")  # Keep renderer active
    chrome_options.add_argument("--window-size=1920,1080")  # Set consistent window size
    chrome_options.add_argument("--disable-default-apps")  # Disable default apps
    chrome_options.add_argument("--disable-sync")  # Disable Chrome sync
    chrome_options.add_argument("--disable-translate")  # Disable translation prompts
    chrome_options.add_argument("--disable-plugins")  # Disable plugins
    # chrome_options.add_argument("--disable-images")  # Disable images (may break layout)
    chrome_options.add_argument("--remote-debugging-port=0")  # Avoid port conflicts
    chrome_options.add_argument("--memory-pressure-off")  # Reduce memory pressure
    chrome_options.add_argument("--max_old_space_size=4096")  # Increase memory limit
    chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36")
    
    # Server-specific optimization - remove Chrome binary path for portability
    # chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    driver = None
    try:
        # Use webdriver-manager with proper architecture handling
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Set pincode for this session
        logger.info(f"Setting pincode {config['pincode']} for this session...")
        
        # Load the first product page to set pincode
        if config['products']:
            first_product_url = config['products'][0]['url']
            logger.info(f"Loading first product page to set pincode: {first_product_url.split('/')[-1]}")
            driver.get(first_product_url)
        
        time.sleep(3)  # Allow page to load
        
        try:
            # Try to find pincode input on this product page
            pincode_input = None
            possible_selectors = [
                "input[placeholder*='pincode' i]",
                "input[placeholder*='Pincode' i]",
                "input[placeholder*='PIN' i]", 
                "input[name*='pincode' i]",
                "input[id*='pincode' i]",
                ".pincode-input",
                "#pincode",
                "#pin-code",
                "#delivery-pincode"
            ]
            
            for selector in possible_selectors:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        logger.info(f"Found pincode input with selector: {selector}")
                        pincode_input = element
                        break
                except:
                    continue
            
            if pincode_input:
                pincode_input.clear()
                pincode_input.send_keys(config['pincode'])
                logger.info(f"Entered pincode: {config['pincode']}")
                
                # Wait for dropdown and click on pincode
                time.sleep(2)
                logger.info("Looking for pincode dropdown options...")
                
                dropdown_clicked = False
                # Try multiple approaches to click the dropdown item
                dropdown_approaches = [
                    # Approach 1: Look for list items containing the pincode
                    f"//li[contains(text(), '{config['pincode']}')]",
                    f"//li[contains(., '{config['pincode']}')]",
                    # Approach 2: Look for dropdown items with pincode
                    f"//div[contains(@class, 'dropdown-item') and contains(text(), '{config['pincode']}')]",
                    # Approach 3: Look for any clickable element with pincode text
                    f"//*[contains(text(), '{config['pincode']}') and (@role='option' or contains(@class, 'option') or contains(@class, 'item'))]",
                    # Approach 4: Generic search for any element containing the pincode
                    f"//*[contains(text(), '{config['pincode']}')]"
                ]
                
                for approach in dropdown_approaches:
                    if dropdown_clicked:
                        break
                    try:
                        logger.info(f"Trying dropdown approach: {approach}")
                        # Wait for dropdown items to be clickable
                        dropdown_elements = WebDriverWait(driver, 5).until(
                            EC.presence_of_all_elements_located((By.XPATH, approach))
                        )
                        
                        logger.info(f"Found {len(dropdown_elements)} dropdown elements")
                        for elem in dropdown_elements:
                            try:
                                if elem.is_displayed() and elem.is_enabled():
                                    elem_text = elem.text.strip()
                                    logger.info(f"Found dropdown option: '{elem_text}'")
                                    
                                    # Click on the element containing our pincode
                                    if config['pincode'] in elem_text:
                                        logger.info(f"Clicking on dropdown item: '{elem_text}'")
                                        driver.execute_script("arguments[0].click();", elem)  # Use JS click for reliability
                                        dropdown_clicked = True
                                        logger.info("Successfully clicked pincode dropdown!")
                                        break
                            except Exception as e:
                                logger.error(f"Error clicking dropdown element: {e}")
                                continue
                    except Exception as e:
                        logger.error(f"Approach failed: {e}")
                        continue
                
                if not dropdown_clicked:
                    logger.info("Could not click pincode dropdown, trying alternative approach...")
                    # Try clicking the "Get my location" button if dropdown doesn't work
                    try:
                        location_btn = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Get my location')]"))
                        )
                        location_btn.click()
                        logger.info("Clicked 'Get my location' button instead")
                        dropdown_clicked = True
                    except:
                        logger.info("Could not find location button either")
                
                time.sleep(3)  # Wait for page to update with pincode
                logger.info("✅ Pincode has been set for this session!")
            else:
                logger.info("⚠️ Could not find pincode input field")
        except Exception as e:
            logger.error(f"Pincode setup failed: {e}. Continuing anyway...")
        
        for product in config['products']:
            if check_stock(driver, product):
                if product['url'] not in NOTIFIED_PRODUCTS_CACHE:
                    send_email(config, product)
                    NOTIFIED_PRODUCTS_CACHE[product['url']] = time.time()
            else:
                if product['url'] in NOTIFIED_PRODUCTS_CACHE:
                    logger.info(f"'{product['name']}' is out of stock. Resetting notification status.")
                    del NOTIFIED_PRODUCTS_CACHE[product['url']]
            time.sleep(0.5)  # Reduced delay between product checks

    except Exception as e:
        logger.error(f"An error occurred during the monitoring job: {e}")
    finally:
        if driver:
            driver.quit()
    logger.info("--- Monitor Cycle Complete ---")


if __name__ == "__main__":
    logger.info("🚀 Self-Contained Amul Stock Monitor has started.")
    logger.info("The first check will run now, then every 10 minutes.")

    run_monitor()
    schedule.every(10).minutes.do(run_monitor)

    while True:
        schedule.run_pending()
        time.sleep(1)
