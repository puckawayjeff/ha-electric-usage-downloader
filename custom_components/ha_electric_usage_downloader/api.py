import aiohttp
from bs4 import BeautifulSoup
import logging

_LOGGER = logging.getLogger(__name__)

class ElectricUsageAPI:
    """Handles communication with the ACEC SmartHub portal."""

    def __init__(self, session: aiohttp.ClientSession, username: str, password: str, login_url: str, usage_url: str):
        """Initialize the API client."""
        self.session = session
        self.username = username
        self.password = password
        self.login_url = login_url
        self.usage_url = usage_url
        self.cookies = None

    async def login(self):
        """Log in to the ACEC SmartHub and retrieve session cookies."""
        payload = {
            "UserName": self.username,
            "Password": self.password
        }
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        try:
            async with self.session.post(self.login_url, data=payload, headers=headers) as response:
                if response.status == 200:
                    _LOGGER.debug("Successfully logged in to ACEC SmartHub")
                    self.cookies = response.cookies
                else:
                    _LOGGER.error(f"Failed to log in to ACEC SmartHub: {response.status}")
                    raise Exception("Login failed")
        except Exception as e:
            _LOGGER.error(f"Error during login: {e}")
            raise

    async def get_usage_data(self):
        """Fetch electric usage data by scraping the ACEC SmartHub portal."""
        if not self.cookies:
            await self.login()

        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        try:
            async with self.session.get(self.usage_url, cookies=self.cookies, headers=headers) as response:
                if response.status != 200:
                    _LOGGER.error(f"Failed to fetch usage data: {response.status}")
                    return None

                html_content = await response.text()
                soup = BeautifulSoup(html_content, "html.parser")

                # Parse the usage data
                usage_data = self._parse_usage_data(soup)
                return usage_data
        except Exception as e:
            _LOGGER.error(f"Error fetching usage data: {e}")
            return None

    def _parse_usage_data(self, soup):
        """Parse the electric usage data from the HTML soup."""
        try:
            usage_value = soup.find("td", class_="highcharts-tooltip").get_text()
            return {"usage": float(usage_value)}
        except Exception as e:
            _LOGGER.error(f"Error parsing usage data: {e}")
            return None
