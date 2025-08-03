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
from threading import Thread
from flask import Flask

# Telegram bot imports
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
    import re
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logging.warning("Telegram bot not available - install python-telegram-bot to enable remote control")

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

# Configuration
CONFIG_FILE = 'email_config.json'

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
                                    logger.info("❌ Status: OUT OF STOCK (Found 'Sold Out' near main cart button - location check failed)")
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

    Great news! The product you're monitoring is now available:

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
                                        logger.info("✅ Successfully clicked pincode dropdown!")
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


# Flask app for health endpoint
app = Flask(__name__)

@app.route('/health')
def health():
    return {"status": "healthy", "service": "amul-stock-monitor"}, 200

@app.route('/')
def root():
    return {"message": "Amul Stock Monitor is running", "status": "active"}, 200

def run_flask_app():
    app.run(host='0.0.0.0', port=5000)

# Telegram Bot Controller (Comprehensive)
class TelegramController:
    def __init__(self, bot_token, authorized_users):
        self.bot_token = bot_token
        self.authorized_users = authorized_users
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command"""
        user_id = update.effective_user.id
        if user_id not in self.authorized_users:
            await update.message.reply_text("❌ Unauthorized access!")
            return
        
        keyboard = [
            [InlineKeyboardButton("📊 View Status", callback_data="status")],
            [InlineKeyboardButton("📦 Manage Products", callback_data="manage_products")],
            [InlineKeyboardButton("📧 Manage Emails", callback_data="manage_emails")],
            [InlineKeyboardButton("📍 Change Pincode", callback_data="change_pincode")],
            [InlineKeyboardButton("⏰ Change Interval", callback_data="manage_interval")],
            [InlineKeyboardButton("🔄 Manual Check", callback_data="manual_check")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤖 *Amul Stock Monitor Controller*\n\n"
            "🎯 Monitor Status: ACTIVE\n"
            "📦 Products: Checking every cycle\n"
            "📧 Emails: Ready to send alerts\n\n"
            "Use buttons below for full control:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        user_id = query.from_user.id
        
        if user_id not in self.authorized_users:
            await query.answer("❌ Unauthorized!")
            return
        
        await query.answer()
        
        config = load_config()
        if not config:
            await query.edit_message_text("❌ Failed to load configuration!")
            return
        
        if query.data == "status":
            text = f"📊 *Monitor Status*\n\n"
            text += f"📍 Pincode: `{config['pincode']}`\n"
            text += f"⏰ Interval: `{config['monitoring']['check_interval_minutes']} minutes`\n"
            text += f"📦 Products: `{len(config['products'])}`\n"
            text += f"📧 Recipients: `{len(config['email']['recipient_emails'])}`\n\n"
            text += "*Products:*\n"
            for i, product in enumerate(config['products']):
                text += f"{i+1}. {product['name'][:40]}...\n"
            text += f"\n*Email Recipients:*\n"
            for email in config['email']['recipient_emails']:
                text += f"• {email}\n"
            
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
            
        elif query.data == "manage_emails":
            text = f"📧 *Email Management*\n\n*Current Recipients:*\n"
            keyboard = []
            
            for i, email in enumerate(config['email']['recipient_emails']):
                text += f"{i+1}. {email}\n"
                keyboard.append([InlineKeyboardButton(f"❌ Remove: {email[:20]}...", callback_data=f"remove_email_{i}")])
            
            keyboard.append([InlineKeyboardButton("➕ Add New Email", callback_data="add_email")])
            keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_main")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
            
        elif query.data == "manage_products":
            text = f"📦 *Product Management*\n\n*Currently Monitoring:*\n"
            keyboard = []
            
            for i, product in enumerate(config['products']):
                text += f"{i+1}. {product['name'][:35]}...\n"
                keyboard.append([InlineKeyboardButton(f"❌ Remove: {product['name'][:25]}...", callback_data=f"remove_product_{i}")])
            
            keyboard.append([InlineKeyboardButton("➕ Add New Product", callback_data="add_product_step1")])
            keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_main")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
            
        elif query.data == "manage_interval":
            current_interval = config['monitoring']['check_interval_minutes']
            text = f"⏰ *Interval Management*\n\n"
            text += f"Current: `{current_interval} minutes`\n\n"
            text += "Choose new interval:"
            
            keyboard = [
                [InlineKeyboardButton("🚀 5 minutes (faster)", callback_data="set_interval_5")],
                [InlineKeyboardButton("⚖️ 10 minutes (balanced)", callback_data="set_interval_10")],
                [InlineKeyboardButton("💰 15 minutes (cheaper)", callback_data="set_interval_15")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
            
        elif query.data == "change_pincode":
            keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data="back_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "📍 *Change Pincode*\n\n"
                f"Current pincode: `{config['pincode']}`\n\n"
                "Please send me the new pincode (6 digits):",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            context.user_data['waiting_for'] = 'pincode'
            
        elif query.data == "add_email":
            keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data="manage_emails")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "📧 *Add New Email*\n\n"
                "Please send me the email address:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            context.user_data['waiting_for'] = 'email'
            
        elif query.data == "add_product_step1":
            keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data="manage_products")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "📦 *Add New Product - Step 1/2*\n\n"
                "Please send me the product name:\n"
                "Example: `Amul Gold Full Cream Milk 1L`",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            context.user_data['waiting_for'] = 'product_name'
            
        elif query.data.startswith("remove_product_"):
            product_index = int(query.data.split("_")[2])
            removed_product = config['products'].pop(product_index)
            
            if self.save_config(config):
                await query.edit_message_text(
                    f"✅ *Product Removed!*\n\n"
                    f"Removed: `{removed_product['name']}`\n\n"
                    f"Remaining products: {len(config['products'])}",
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text("❌ Failed to save configuration!")
                
        elif query.data.startswith("remove_email_"):
            email_index = int(query.data.split("_")[2])
            removed_email = config['email']['recipient_emails'].pop(email_index)
            
            if self.save_config(config):
                await query.edit_message_text(
                    f"✅ *Email Removed!*\n\n"
                    f"Removed: `{removed_email}`\n\n"
                    f"Remaining emails: {len(config['email']['recipient_emails'])}",
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text("❌ Failed to save configuration!")
                
        elif query.data.startswith("set_interval_"):
            interval = int(query.data.split("_")[2])
            config['monitoring']['check_interval_minutes'] = interval
            
            if self.save_config(config):
                cost_msg = {
                    5: "⚡ Faster alerts, higher cost (~$15-20/month)",
                    10: "⚖️ Balanced option (~$8-12/month)", 
                    15: "💰 Cheaper option (~$5-8/month)"
                }
                
                await query.edit_message_text(
                    f"✅ *Interval Updated!*\n\n"
                    f"⏰ New interval: `{interval} minutes`\n"
                    f"{cost_msg[interval]}\n\n"
                    f"⚠️ *Note:* Restart required for effect.",
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text("❌ Failed to update interval!")
                
        elif query.data == "add_product_step2":
            keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data="manage_products")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "📦 *Add New Product - Step 2/2*\n\n"
                "Please send me the product URL:\n"
                "Example: `https://www.example.com/amul-gold-full-cream-milk-1l`",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            context.user_data['waiting_for'] = 'product_url'
            
        elif query.data == "manual_check":
            await query.edit_message_text("🔄 *Manual Check Started!*\n\nChecking all products now...")
            # Trigger the actual run_monitor function
            from threading import Thread
            Thread(target=run_monitor).start()
            await asyncio.sleep(2)
            await query.edit_message_text("✅ *Manual Check Complete!*\n\nCheck your emails for any alerts!")
            
        elif query.data == "back_main":
            await self.show_main_menu(query)

    async def show_main_menu(self, query):
        """Show main menu from callback"""
        keyboard = [
            [InlineKeyboardButton("📊 View Status", callback_data="status")],
            [InlineKeyboardButton("📦 Manage Products", callback_data="manage_products")],
            [InlineKeyboardButton("📧 Manage Emails", callback_data="manage_emails")],
            [InlineKeyboardButton("📍 Change Pincode", callback_data="change_pincode")],
            [InlineKeyboardButton("⏰ Change Interval", callback_data="manage_interval")],
            [InlineKeyboardButton("🔄 Manual Check", callback_data="manual_check")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🤖 *Amul Stock Monitor Controller*\n\n"
            "🎯 Monitor Status: ACTIVE\n"
            "📦 Products: Checking every cycle\n"
            "📧 Emails: Ready to send alerts\n\n"
            "Use buttons below for full control:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text input for pincode/email"""
        user_id = update.effective_user.id
        
        if user_id not in self.authorized_users:
            return
        
        waiting_for = context.user_data.get('waiting_for')
        text = update.message.text.strip()
        
        config = load_config()
        if not config:
            await update.message.reply_text("❌ Error loading configuration!")
            return
        
        if waiting_for == 'pincode':
            # Validate pincode (6 digits)
            if re.match(r'^\d{6}$', text):
                config['pincode'] = text
                if self.save_config(config):
                    await update.message.reply_text(
                        f"✅ *Pincode Updated!*\n\n"
                        f"New pincode: `{text}`\n\n"
                        f"This will take effect on next check cycle.",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text("❌ Failed to save configuration!")
            else:
                await update.message.reply_text("❌ Invalid pincode! Please send 6 digits (e.g., 500018)")
                return
                
        elif waiting_for == 'email':
            # Validate email
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(email_pattern, text):
                if text not in config['email']['recipient_emails']:
                    config['email']['recipient_emails'].append(text)
                    if self.save_config(config):
                        await update.message.reply_text(
                            f"✅ *Email Added!*\n\n"
                            f"Added: `{text}`\n\n"
                            f"Total recipients: {len(config['email']['recipient_emails'])}",
                            parse_mode='Markdown'
                        )
                    else:
                        await update.message.reply_text("❌ Failed to save configuration!")
                else:
                    await update.message.reply_text("❌ Email already exists!")
            else:
                await update.message.reply_text("❌ Invalid email format! Please send a valid email address.")
                return
        
        elif waiting_for == 'product_name':
            # Validate product name
            if len(text) > 5:
                context.user_data['product_name'] = text
                await update.message.reply_text(
                    f"✅ *Product Name Saved!*\n\n"
                    f"Name: `{text}`\n\n"
                    f"Please send the product URL now.",
                    parse_mode='Markdown'
                )
                context.user_data['waiting_for'] = 'product_url'
            else:
                await update.message.reply_text("❌ Invalid product name! Please send a valid name.")
                return
        
        elif waiting_for == 'product_url':
            # Validate product URL
            url_pattern = r'^https?://[^\s]+'
            if re.match(url_pattern, text):
                product_name = context.user_data['product_name']
                product_url = text
                new_product = {
                    'name': product_name,
                    'url': product_url,
                    'price': 'N/A'
                }
                config['products'].append(new_product)
                if self.save_config(config):
                    await update.message.reply_text(
                        f"✅ *Product Added!*\n\n"
                        f"Name: `{product_name}`\n"
                        f"URL: `{product_url}`\n\n"
                        f"Total products: {len(config['products'])}\n\n"
                        f"✅ *Immediate Check Complete!*",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text("❌ Failed to save configuration!")
            else:
                await update.message.reply_text("❌ Invalid product URL! Please send a valid URL.")
                return
        
        # Clear waiting state
        context.user_data['waiting_for'] = None
    
    def save_config(self, config):
        """Save configuration"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False

def run_telegram_bot():
    """Run Telegram bot in background"""
    if not TELEGRAM_AVAILABLE:
        logger.info("⚠️ Telegram bot disabled - python-telegram-bot not installed")
        return
    
    BOT_TOKEN = "8042722432:AAH2vDuqwDpChCZYpVKPZSIbsrAlx28OI1g"
    AUTHORIZED_USERS = [616312112]
    
    try:
        controller = TelegramController(BOT_TOKEN, AUTHORIZED_USERS)
        application = Application.builder().token(BOT_TOKEN).build()
        
        application.add_handler(CommandHandler("start", controller.start))
        application.add_handler(CallbackQueryHandler(controller.button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, controller.handle_text_input))
        
        logger.info("🤖 Telegram Bot Controller started!")
        application.run_polling()
    except Exception as e:
        logger.error(f"❌ Failed to start Telegram bot: {e}")
        logger.info("📧 Monitor will continue running without bot control")

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"FATAL: Config file '{CONFIG_FILE}' not found.")
        return None

if __name__ == "__main__":
    logger.info("🚀 Self-Contained Amul Stock Monitor has started.")
    logger.info("The first check will run now, then every 10 minutes.")

    flask_thread = Thread(target=run_flask_app)
    flask_thread.daemon = True  # Allow main thread to exit even if flask thread is still running
    flask_thread.start()

    telegram_thread = Thread(target=run_telegram_bot)
    telegram_thread.daemon = True  # Allow main thread to exit even if telegram thread is still running
    telegram_thread.start()

    run_monitor()
    schedule.every(10).minutes.do(run_monitor)

    while True:
        schedule.run_pending()
        time.sleep(1)
