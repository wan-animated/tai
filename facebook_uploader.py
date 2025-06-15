#!/usr/bin/env python3
"""
Facebook Uploader untuk Status dan Reels menggunakan Selenium
Mendukung cookies JSON untuk auto-login dan upload berbagai jenis konten
"""

import os
import sys
import json
import time
import random
from pathlib import Path
from typing import Optional, Dict, Any

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    WebDriverException,
    ElementNotInteractableException,
    StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager
from colorama import init, Fore, Style
import argparse

# Initialize colorama
init(autoreset=True)

class FacebookUploader:
    def __init__(self, headless: bool = False, debug: bool = False):
        """
        Initialize Facebook Uploader
        
        Args:
            headless: Run browser in headless mode
            debug: Enable debug logging
        """
        self.headless = headless
        self.debug = debug
        self.driver = None
        self.wait = None
        
        # Setup paths
        self.base_dir = Path(__file__).parent
        self.cookies_dir = self.base_dir / "cookies"
        self.cookies_dir.mkdir(exist_ok=True)
        self.cookies_path = self.cookies_dir / "facebook_cookies.json"
        self.screenshots_dir = self.base_dir / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # Facebook URLs
        self.home_url = "https://www.facebook.com"
        self.reels_url = "https://www.facebook.com/reel/create"
        self.login_url = "https://www.facebook.com/login"
        
        # Selectors for Facebook
        self.selectors = {
            'status_input': [
                "div[data-testid='status-attachment-mentions-input']",
                "div[role='textbox'][data-testid='status-attachment-mentions-input']",
                "div[contenteditable='true'][data-testid='status-attachment-mentions-input']",
                "div[aria-label*='What\\'s on your mind']",
                "div[aria-label*='Apa yang Anda pikirkan']"
            ],
            'photo_video_button': [
                "div[aria-label='Photo/video']",
                "div[aria-label='Foto/video']",
                "div[data-testid='photo-video-button']",
                "input[accept*='image']",
                "input[accept*='video']"
            ],
            'file_input': [
                "input[type='file']",
                "input[accept*='video']",
                "input[accept*='image']"
            ],
            'post_button': [
                "div[aria-label='Post']",
                "div[aria-label='Posting']",
                "div[data-testid='react-composer-post-button']",
                "div[role='button'][tabindex='0']"
            ],
            'reels_upload_button': [
                "div[aria-label='Select video']",
                "div[aria-label='Pilih video']",
                "input[accept*='video']"
            ],
            'reels_next_button': [
                "div[aria-label='Next']",
                "div[aria-label='Berikutnya']",
                "div[role='button']"
            ],
            'reels_share_button': [
                "div[aria-label='Share to Feed']",
                "div[aria-label='Bagikan ke Feed']",
                "div[aria-label='Share']",
                "div[aria-label='Bagikan']"
            ]
        }

    def _log(self, message: str, level: str = "INFO"):
        """Enhanced logging with colors"""
        colors = {
            "INFO": Fore.CYAN,
            "SUCCESS": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED,
            "DEBUG": Fore.MAGENTA
        }
        
        if level == "DEBUG" and not self.debug:
            return
            
        color = colors.get(level, Fore.WHITE)
        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "DEBUG": "🔍"
        }
        
        icon = icons.get(level, "📝")
        print(f"{color}{icon} {message}{Style.RESET_ALL}")

    def _setup_driver(self):
        """Setup Chrome WebDriver with optimal configuration"""
        self._log("Setting up browser for Facebook...")
        
        chrome_options = Options()
        
        # Basic options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--window-size=1280,800")
        
        if self.headless:
            chrome_options.add_argument('--headless=new')
        
        # Additional options for Facebook
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Suppress logs
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--silent")
        chrome_options.add_argument("--disable-logging")
        
        # Anti-detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            service = Service(
                ChromeDriverManager().install(),
                log_path=os.devnull,
                service_args=['--silent']
            )
            
            os.environ['WDM_LOG_LEVEL'] = '0'
            os.environ['WDM_PRINT_FIRST_LINE'] = 'False'
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Anti-detection scripts
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 30)
            
            self._log("Browser ready for Facebook", "SUCCESS")
            
        except Exception as e:
            self._log(f"Failed to setup browser: {str(e)}", "ERROR")
            raise

    def _find_element_by_selectors(self, selectors: list, timeout: int = 10, visible: bool = True) -> Optional[Any]:
        """Find element using multiple selectors"""
        for i, selector in enumerate(selectors):
            try:
                if visible:
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                else:
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                
                if i == 0:
                    self._log("Element found", "SUCCESS")
                else:
                    self._log(f"Element found (alternative {i+1})", "SUCCESS")
                return element
                
            except TimeoutException:
                continue
                
        return None

    def load_cookies(self) -> bool:
        """Load cookies from JSON file"""
        if not self.cookies_path.exists():
            self._log("Facebook cookies file not found", "WARNING")
            return False
            
        try:
            with open(self.cookies_path, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            if isinstance(cookies_data, dict):
                cookies = cookies_data.get('cookies', [])
            else:
                cookies = cookies_data
            
            if not cookies:
                self._log("Cookies file is empty", "WARNING")
                return False
            
            # Navigate to Facebook first
            self.driver.get(self.home_url)
            time.sleep(3)
            
            # Add cookies
            cookies_added = 0
            for cookie in cookies:
                try:
                    if 'name' in cookie and 'value' in cookie:
                        clean_cookie = {
                            'name': cookie['name'],
                            'value': cookie['value'],
                            'domain': cookie.get('domain', '.facebook.com'),
                            'path': cookie.get('path', '/'),
                        }
                        
                        if 'expiry' in cookie:
                            clean_cookie['expiry'] = int(cookie['expiry'])
                        elif 'expires' in cookie:
                            clean_cookie['expiry'] = int(cookie['expires'])
                        
                        if 'secure' in cookie:
                            clean_cookie['secure'] = cookie['secure']
                        if 'httpOnly' in cookie:
                            clean_cookie['httpOnly'] = cookie['httpOnly']
                        
                        self.driver.add_cookie(clean_cookie)
                        cookies_added += 1
                        
                except Exception as e:
                    if self.debug:
                        self._log(f"Failed to add cookie {cookie.get('name', 'unknown')}: {e}", "DEBUG")
            
            self._log(f"Cookies loaded: {cookies_added}/{len(cookies)}", "SUCCESS")
            return cookies_added > 0
            
        except Exception as e:
            self._log(f"Failed to load cookies: {str(e)}", "ERROR")
            return False

    def save_cookies(self):
        """Save cookies to JSON file"""
        try:
            cookies = self.driver.get_cookies()
            
            cookies_data = {
                "timestamp": int(time.time()),
                "cookies": cookies
            }
            
            with open(self.cookies_path, 'w', encoding='utf-8') as f:
                json.dump(cookies_data, f, indent=2, ensure_ascii=False)
            
            self._log(f"Cookies saved: {len(cookies)} items", "SUCCESS")
            
        except Exception as e:
            self._log(f"Failed to save cookies: {str(e)}", "ERROR")

    def clear_cookies(self):
        """Clear cookies file"""
        try:
            if self.cookies_path.exists():
                self.cookies_path.unlink()
                self._log("Facebook cookies cleared", "SUCCESS")
            else:
                self._log("No Facebook cookies to clear", "WARNING")
        except Exception as e:
            self._log(f"Failed to clear cookies: {str(e)}", "ERROR")

    def check_login_required(self) -> bool:
        """Check if login is required"""
        current_url = self.driver.current_url
        return "login" in current_url or "checkpoint" in current_url

    def wait_for_login(self, timeout: int = 180):
        """Wait for user to login manually"""
        self._log("Please login manually in the browser...", "WARNING")
        self._log(f"Waiting for login completion (timeout {timeout} seconds)...", "INFO")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            current_url = self.driver.current_url
            
            # Check if no longer on login page
            if not ("login" in current_url or "checkpoint" in current_url):
                if "facebook.com" in current_url:
                    self._log("Login successful!", "SUCCESS")
                    self.save_cookies()
                    return True
            
            time.sleep(2)
        
        raise TimeoutException("Timeout waiting for login")

    def upload_status(self, status_text: str = "", media_path: str = "") -> Dict[str, Any]:
        """
        Upload status to Facebook with optional media
        
        Args:
            status_text: Text content for status
            media_path: Path to media file (image/video)
            
        Returns:
            Dict with upload status
        """
        try:
            # Setup driver
            self._setup_driver()
            
            # Load cookies
            cookies_loaded = self.load_cookies()
            
            # Navigate to Facebook
            self._log("Navigating to Facebook...")
            self.driver.get(self.home_url)
            time.sleep(3)
            
            # Check if login required
            if self.check_login_required():
                if cookies_loaded:
                    self._log("Cookies loaded but still need login, refreshing...", "WARNING")
                    self.driver.refresh()
                    time.sleep(3)
                
                if self.check_login_required():
                    self.wait_for_login()
                    self.driver.get(self.home_url)
                    time.sleep(3)
            
            # Find status input
            self._log("Looking for status input...")
            status_input = self._find_element_by_selectors(self.selectors['status_input'])
            
            if not status_input:
                raise NoSuchElementException("Status input not found")
            
            # Click status input to activate
            status_input.click()
            time.sleep(2)
            
            # Add media if provided
            if media_path and os.path.exists(media_path):
                self._log("Adding media to status...")
                
                # Look for photo/video button
                photo_video_btn = self._find_element_by_selectors(self.selectors['photo_video_button'], timeout=5)
                
                if photo_video_btn:
                    photo_video_btn.click()
                    time.sleep(2)
                
                # Find file input
                file_input = self._find_element_by_selectors(self.selectors['file_input'], timeout=10, visible=False)
                
                if file_input:
                    abs_path = os.path.abspath(media_path)
                    file_input.send_keys(abs_path)
                    self._log("Media uploaded successfully", "SUCCESS")
                    time.sleep(5)  # Wait for upload
                else:
                    self._log("File input not found", "WARNING")
            
            # Add status text if provided
            if status_text.strip():
                self._log("Adding status text...")
                
                # Find the active text input (might have changed after media upload)
                text_inputs = self.driver.find_elements(By.CSS_SELECTOR, "div[contenteditable='true']")
                
                for text_input in text_inputs:
                    if text_input.is_displayed():
                        try:
                            text_input.click()
                            time.sleep(1)
                            text_input.send_keys(status_text)
                            self._log("Status text added", "SUCCESS")
                            break
                        except:
                            continue
            
            # Find and click post button
            self._log("Looking for post button...")
            post_button = self._find_element_by_selectors(self.selectors['post_button'])
            
            if not post_button:
                # Fallback: look for button with "Post" text
                buttons = self.driver.find_elements(By.TAG_NAME, "div")
                for button in buttons:
                    if button.text.lower() in ['post', 'posting', 'share', 'bagikan']:
                        if button.is_enabled() and button.is_displayed():
                            post_button = button
                            break
            
            if not post_button:
                raise NoSuchElementException("Post button not found")
            
            # Click post button
            self.driver.execute_script("arguments[0].click();", post_button)
            self._log("Post button clicked", "SUCCESS")
            time.sleep(5)
            
            # Check for success
            self._log("Facebook status posted successfully!", "SUCCESS")
            
            return {
                "success": True,
                "message": "Status posted successfully",
                "status_text": status_text,
                "media_path": media_path
            }
            
        except Exception as e:
            error_msg = f"Facebook status upload failed: {str(e)}"
            self._log(error_msg, "ERROR")
            
            # Take screenshot for debugging
            self.take_screenshot(f"facebook_status_error_{int(time.time())}.png")
            
            return {
                "success": False,
                "message": error_msg,
                "status_text": status_text,
                "media_path": media_path
            }
        
        finally:
            if self.driver:
                self._log("Closing browser...")
                self.driver.quit()

    def upload_reels(self, video_path: str, description: str = "") -> Dict[str, Any]:
        """
        Upload reels to Facebook
        
        Args:
            video_path: Path to video file
            description: Description for the reel
            
        Returns:
            Dict with upload status
        """
        try:
            # Setup driver
            self._setup_driver()
            
            # Load cookies
            cookies_loaded = self.load_cookies()
            
            # Navigate to Facebook Reels creation
            self._log("Navigating to Facebook Reels...")
            self.driver.get(self.reels_url)
            time.sleep(5)
            
            # Check if login required
            if self.check_login_required():
                if cookies_loaded:
                    self._log("Cookies loaded but still need login, refreshing...", "WARNING")
                    self.driver.refresh()
                    time.sleep(5)
                
                if self.check_login_required():
                    self.wait_for_login()
                    self.driver.get(self.reels_url)
                    time.sleep(5)
            
            # Upload video file
            self._log("Uploading video file...")
            
            # Find upload button or file input
            upload_element = self._find_element_by_selectors(self.selectors['reels_upload_button'], timeout=15, visible=False)
            
            if not upload_element:
                # Fallback: look for any file input
                file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                for file_input in file_inputs:
                    accept_attr = file_input.get_attribute('accept') or ''
                    if 'video' in accept_attr:
                        upload_element = file_input
                        break
            
            if not upload_element:
                raise NoSuchElementException("Video upload element not found")
            
            # Upload video
            abs_path = os.path.abspath(video_path)
            upload_element.send_keys(abs_path)
            self._log("Video file uploaded", "SUCCESS")
            
            # Wait for video processing
            self._log("Waiting for video processing...")
            time.sleep(15)
            
            # Add description if provided
            if description.strip():
                self._log("Adding description...")
                
                # Look for description input
                description_inputs = self.driver.find_elements(By.CSS_SELECTOR, "div[contenteditable='true']")
                
                for desc_input in description_inputs:
                    if desc_input.is_displayed():
                        try:
                            desc_input.click()
                            time.sleep(1)
                            desc_input.send_keys(description)
                            self._log("Description added", "SUCCESS")
                            break
                        except:
                            continue
            
            # Look for Next button (if exists)
            next_button = self._find_element_by_selectors(self.selectors['reels_next_button'], timeout=5)
            if next_button:
                next_button.click()
                self._log("Next button clicked", "SUCCESS")
                time.sleep(3)
            
            # Find and click share button
            self._log("Looking for share button...")
            share_button = self._find_element_by_selectors(self.selectors['reels_share_button'], timeout=15)
            
            if not share_button:
                # Fallback: look for button with share-related text
                buttons = self.driver.find_elements(By.TAG_NAME, "div")
                for button in buttons:
                    button_text = button.text.lower()
                    if any(word in button_text for word in ['share', 'bagikan', 'post', 'publish']):
                        if button.is_enabled() and button.is_displayed():
                            share_button = button
                            break
            
            if not share_button:
                raise NoSuchElementException("Share button not found")
            
            # Click share button
            self.driver.execute_script("arguments[0].click();", share_button)
            self._log("Share button clicked", "SUCCESS")
            time.sleep(10)
            
            # Check for success
            self._log("Facebook Reels uploaded successfully!", "SUCCESS")
            
            return {
                "success": True,
                "message": "Reels uploaded successfully",
                "video_path": video_path,
                "description": description
            }
            
        except Exception as e:
            error_msg = f"Facebook Reels upload failed: {str(e)}"
            self._log(error_msg, "ERROR")
            
            # Take screenshot for debugging
            self.take_screenshot(f"facebook_reels_error_{int(time.time())}.png")
            
            return {
                "success": False,
                "message": error_msg,
                "video_path": video_path,
                "description": description
            }
        
        finally:
            if self.driver:
                self._log("Closing browser...")
                self.driver.quit()

    def take_screenshot(self, filename: str = None):
        """Take screenshot for debugging"""
        if not filename:
            filename = f"facebook_screenshot_{int(time.time())}.png"
        
        screenshot_path = self.screenshots_dir / filename
        
        try:
            self.driver.save_screenshot(str(screenshot_path))
            self._log(f"Screenshot saved: {screenshot_path.name}", "INFO")
            return str(screenshot_path)
        except Exception as e:
            self._log(f"Failed to save screenshot: {str(e)}", "WARNING")
            return None

    def check_cookies_status(self):
        """Check Facebook cookies status"""
        if not self.cookies_path.exists():
            self._log("Facebook cookies file not found", "WARNING")
            return {"exists": False, "count": 0}
        
        try:
            with open(self.cookies_path, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            if isinstance(cookies_data, dict):
                cookies = cookies_data.get('cookies', [])
                timestamp = cookies_data.get('timestamp', 0)
            else:
                cookies = cookies_data if isinstance(cookies_data, list) else []
                timestamp = 0
            
            # Check expired cookies
            current_time = time.time()
            valid_cookies = []
            expired_cookies = []
            
            for cookie in cookies:
                if 'expiry' in cookie:
                    if cookie['expiry'] > current_time:
                        valid_cookies.append(cookie)
                    else:
                        expired_cookies.append(cookie)
                elif 'expires' in cookie:
                    if cookie['expires'] > current_time:
                        valid_cookies.append(cookie)
                    else:
                        expired_cookies.append(cookie)
                else:
                    valid_cookies.append(cookie)
            
            self._log(f"Total Facebook cookies: {len(cookies)}", "INFO")
            self._log(f"Valid cookies: {len(valid_cookies)}", "SUCCESS")
            
            if expired_cookies:
                self._log(f"Expired cookies: {len(expired_cookies)}", "WARNING")
            
            if timestamp:
                import datetime
                saved_time = datetime.datetime.fromtimestamp(timestamp)
                self._log(f"Cookies saved: {saved_time.strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
            
            return {
                "exists": True,
                "total": len(cookies),
                "valid": len(valid_cookies),
                "expired": len(expired_cookies),
                "timestamp": timestamp
            }
            
        except Exception as e:
            self._log(f"Error reading Facebook cookies: {str(e)}", "ERROR")
            return {"exists": True, "error": str(e)}


def main():
    """Main function for CLI"""
    parser = argparse.ArgumentParser(description="Facebook Uploader")
    parser.add_argument("--type", choices=['status', 'reels'], help="Upload type")
    parser.add_argument("--video", "-v", help="Path to video file (for reels)")
    parser.add_argument("--status", "-s", help="Status text")
    parser.add_argument("--media", "-m", help="Path to media file (for status)")
    parser.add_argument("--description", "-d", default="", help="Description for reels")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--clear-cookies", action="store_true", help="Clear cookies")
    parser.add_argument("--check-cookies", action="store_true", help="Check cookies status")
    
    args = parser.parse_args()
    
    uploader = FacebookUploader(headless=args.headless, debug=args.debug)
    
    # Handle different actions
    if args.clear_cookies:
        uploader.clear_cookies()
        return
    
    if args.check_cookies:
        uploader.check_cookies_status()
        return
    
    if args.type == 'status':
        if not args.status and not args.media:
            print(f"{Fore.RED}❌ Status text or media required for status upload")
            sys.exit(1)
        
        if args.media and not os.path.exists(args.media):
            print(f"{Fore.RED}❌ Media file not found: {args.media}")
            sys.exit(1)
        
        result = uploader.upload_status(args.status or "", args.media or "")
        
        if result["success"]:
            print(f"{Fore.GREEN}🎉 Facebook status uploaded successfully!")
        else:
            print(f"{Fore.RED}❌ Facebook status upload failed: {result['message']}")
            sys.exit(1)
    
    elif args.type == 'reels':
        if not args.video:
            print(f"{Fore.RED}❌ Video path required for reels upload")
            sys.exit(1)
        
        if not os.path.exists(args.video):
            print(f"{Fore.RED}❌ Video file not found: {args.video}")
            sys.exit(1)
        
        result = uploader.upload_reels(args.video, args.description)
        
        if result["success"]:
            print(f"{Fore.GREEN}🎉 Facebook Reels uploaded successfully!")
        else:
            print(f"{Fore.RED}❌ Facebook Reels upload failed: {result['message']}")
            sys.exit(1)
    
    else:
        # Interactive mode
        print(f"{Fore.BLUE}📘 Facebook Uploader")
        print("=" * 40)
        
        while True:
            print(f"\n{Fore.YELLOW}Choose action:")
            print("1. 📝 Upload Status (Text)")
            print("2. 🖼️ Upload Status (with Media)")
            print("3. 🎬 Upload Reels")
            print("4. 🍪 Check cookies status")
            print("5. 🗑️ Clear cookies")
            print("6. ❌ Exit")
            
            choice = input(f"\n{Fore.WHITE}Choice (1-6): ").strip()
            
            if choice == "1":
                status_text = input(f"{Fore.CYAN}Status text: ").strip()
                if not status_text:
                    print(f"{Fore.RED}❌ Status text cannot be empty!")
                    continue
                
                result = uploader.upload_status(status_text)
                
                if result["success"]:
                    print(f"{Fore.GREEN}🎉 Facebook status uploaded successfully!")
                else:
                    print(f"{Fore.RED}❌ Facebook status upload failed: {result['message']}")
            
            elif choice == "2":
                media_path = input(f"{Fore.CYAN}Media file path: ").strip()
                if not os.path.exists(media_path):
                    print(f"{Fore.RED}❌ Media file not found!")
                    continue
                
                status_text = input(f"{Fore.CYAN}Status text (optional): ").strip()
                
                result = uploader.upload_status(status_text, media_path)
                
                if result["success"]:
                    print(f"{Fore.GREEN}🎉 Facebook status with media uploaded successfully!")
                else:
                    print(f"{Fore.RED}❌ Facebook status upload failed: {result['message']}")
            
            elif choice == "3":
                video_path = input(f"{Fore.CYAN}Video file path: ").strip()
                if not os.path.exists(video_path):
                    print(f"{Fore.RED}❌ Video file not found!")
                    continue
                
                description = input(f"{Fore.CYAN}Description (optional): ").strip()
                
                result = uploader.upload_reels(video_path, description)
                
                if result["success"]:
                    print(f"{Fore.GREEN}🎉 Facebook Reels uploaded successfully!")
                else:
                    print(f"{Fore.RED}❌ Facebook Reels upload failed: {result['message']}")
            
            elif choice == "4":
                uploader.check_cookies_status()
            
            elif choice == "5":
                confirm = input(f"{Fore.YELLOW}Clear Facebook cookies? (y/N): ").strip().lower()
                if confirm == 'y':
                    uploader.clear_cookies()
            
            elif choice == "6":
                print(f"{Fore.YELLOW}👋 Goodbye!")
                break
            
            else:
                print(f"{Fore.RED}❌ Invalid choice!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Program stopped by user")
    except Exception as e:
        print(f"{Fore.RED}💥 Fatal error: {str(e)}")
        sys.exit(1)