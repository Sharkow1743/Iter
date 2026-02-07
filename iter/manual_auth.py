import os
import zipfile
import platform
import requests
import logging
import stat
from pathlib import Path
from DrissionPage import ChromiumPage, ChromiumOptions

logger = logging.getLogger(__name__)

class BrowserManager:
    def __init__(self, folder_name="browser"):
        package_dir = Path(__file__).resolve().parent
        self.base_dir = package_dir / folder_name
        
        self.system = platform.system()
        self.machine = platform.machine().lower()
        self._set_platform_configs()

    def _set_platform_configs(self):
        """Maps system architecture to Chrome for Testing API keys and paths."""
        if self.system == "Windows":
            self.platform_key = "win64"
            self.exec_name = "chrome.exe"
            self.relative_path = Path("chrome-win64") / self.exec_name
        elif self.system == "Linux":
            self.platform_key = "linux64"
            self.exec_name = "chrome"
            self.relative_path = Path("chrome-linux64") / self.exec_name
        elif self.system == "Darwin":
            self.platform_key = "mac-arm64" if "arm" in self.machine or "apple" in self.machine else "mac-x64"
            self.exec_name = "Google Chrome for Testing"
            folder_name = f"chrome-{self.platform_key}"
            self.relative_path = Path(folder_name) / "Google Chrome for Testing.app" / "Contents" / "MacOS" / "Google Chrome for Testing"
        else:
            raise OSError(f"Unsupported operating system: {self.system}")

        self.chrome_exe = self.base_dir / self.relative_path

    def get_chrome_path(self):
        """Returns the path to the executable, downloading it if necessary."""
        if not self.chrome_exe.exists():
            logger.info(f"Chrome not found for {self.system}. Starting download...")
            self._download_chrome()
            
            # On Linux/Mac, we must ensure the binary is executable
            if self.system != "Windows":
                self._ensure_executable(self.chrome_exe)
                
        return str(self.chrome_exe.absolute())

    def _ensure_executable(self, path):
        """Sets chmod +x on the binary."""
        st = os.stat(path)
        os.chmod(path, st.st_mode | stat.S_IEXEC)

    def _download_chrome(self):
        # 1. Get latest stable download URL
        api_url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
        try:
            resp = requests.get(api_url).json()
            downloads = resp['channels']['Stable']['downloads']['chrome']
            
            download_url = next(item['url'] for item in downloads if item['platform'] == self.platform_key)
        except Exception as e:
            raise RuntimeError(f"Failed to fetch download URL from Google API: {e}")

        self.base_dir.mkdir(parents=True, exist_ok=True)
        zip_path = self.base_dir / "chrome_temp.zip"

        # 2. Download with progress bar
        logger.info(f"Downloading Chrome ({self.platform_key}) from: {download_url}")
        r = requests.get(download_url, stream=True)
        
        with open(zip_path, 'wb') as f:
            for data in r.iter_content(chunk_size=1024):
                f.write(data)

        # 3. Extract
        logger.info("Extracting browser...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.base_dir)
            
        # 4. Cleanup
        if zip_path.exists():
            os.remove(zip_path)
        logger.info(f"Browser successfully installed to {self.chrome_exe}")

def auth(email = None, password = None):
    auth_data = None
    page = None
    try:
        bm = BrowserManager()
        chrome_path = bm.get_chrome_path()
        
        co = ChromiumOptions()
        co.set_browser_path(chrome_path)
    
        target_url = 'https://xn--d1ah4a.com/login'
        co.set_argument(f'--app={target_url}')

        co.incognito()
        
        width, height = 450, 700
        co.set_argument(f'--window-size={width},{height}')
        co.set_argument('--window-position=500,200')

        page = ChromiumPage(co)
        
        page.listen.start('auth/sign-in') 
        page.get(target_url)

        logger.info(f"Attempting to autofill login for: {email}")

        if email:
            email_field = page.ele('#login-email')
            email_field.input(email)

        if password:
            pass_field = page.ele('#login-password')
            pass_field.input(password)

        logger.info("Waiting for authentication response")
        
        res = None
        try:
            res = page.listen.wait() 
        except Exception: pass
        if res:
            target_data = res.response.body
            if isinstance(target_data, dict) and 'accessToken' in target_data:
                token = target_data['accessToken']
                all_raw_cookies = page.run_cdp('Network.getAllCookies')['cookies']
                auth_data = {"token": token, "cookies": all_raw_cookies}
                logger.info("Successfully authenticated!")
            else:
                logger.error("Login failed or response structure changed.")

    except Exception as e:
        logger.exception(f"Error during auth: {e}")
    finally:
        if page:
            page.quit()
            
    return auth_data