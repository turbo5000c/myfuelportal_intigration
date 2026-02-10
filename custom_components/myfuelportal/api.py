"""API Client for MyFuelPortal."""

from __future__ import annotations

import logging
import re
from typing import Any

import aiohttp
from bs4 import BeautifulSoup

_LOGGER = logging.getLogger(__name__)


class MyFuelPortalAPIError(Exception):
    """Base exception for MyFuelPortal API errors."""


class AuthenticationError(MyFuelPortalAPIError):
    """Authentication failed."""


class ConnectionError(MyFuelPortalAPIError):
    """Connection to MyFuelPortal failed."""


class ParsingError(MyFuelPortalAPIError):
    """Failed to parse data from HTML."""


class MyFuelPortalAPI:
    """API client for MyFuelPortal."""

    def __init__(
        self, email: str, password: str, base_url: str = "https://kbjohnson.myfuelportal.com"
    ) -> None:
        """Initialize the API client.

        Args:
            email: User's email address for authentication
            password: User's password
            base_url: Base URL for the MyFuelPortal instance

        """
        self.email = email
        self.password = password
        self.base_url = base_url.rstrip("/")
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def async_login(self) -> bool:
        """Authenticate with MyFuelPortal.

        Returns:
            True if authentication successful

        Raises:
            AuthenticationError: If credentials are invalid
            ConnectionError: If unable to connect to the service

        """
        try:
            session = await self._get_session()

            # Step 1: GET login page to extract CSRF token
            login_url = f"{self.base_url}/Account/Login"
            _LOGGER.debug("Fetching login page from %s", login_url)
            
            async with session.get(login_url) as response:
                if response.status != 200:
                    raise ConnectionError(
                        f"Failed to load login page: HTTP {response.status}"
                    )
                html = await response.text()

            # Parse HTML to extract CSRF token
            soup = BeautifulSoup(html, "html.parser")
            token_input = soup.find("input", {"name": "__RequestVerificationToken"})
            
            if not token_input or not token_input.get("value"):
                raise ParsingError("Could not find CSRF token in login page")

            csrf_token = token_input["value"]
            _LOGGER.debug("Extracted CSRF token")

            # Step 2: POST credentials with CSRF token
            login_post_url = f"{self.base_url}/Account/Login?ReturnUrl=%2FTank"
            form_data = {
                "EmailAddress": self.email,
                "Password": self.password,
                "__RequestVerificationToken": csrf_token,
                "RememberMe": "false",
            }

            _LOGGER.debug("Submitting login credentials")
            async with session.post(login_post_url, data=form_data) as response:
                # Check if login was successful
                # Successful login should redirect to /Tank page (302 or 200)
                if response.status in (200, 302):
                    # Check if we're actually logged in by looking at the response
                    # If redirected back to login page or login form present, auth failed
                    response_text = await response.text()
                    
                    # If we see the login form again, authentication failed
                    if "Account/Login" in str(response.url) or "id=\"EmailAddress\"" in response_text:
                        raise AuthenticationError("Invalid email or password")
                    
                    _LOGGER.info("Successfully authenticated to MyFuelPortal")
                    return True
                elif response.status == 401 or response.status == 403:
                    raise AuthenticationError("Invalid email or password")
                else:
                    raise ConnectionError(
                        f"Unexpected response during login: HTTP {response.status}"
                    )

        except aiohttp.ClientError as err:
            raise ConnectionError(f"Connection error: {err}") from err
        except AuthenticationError:
            raise
        except ParsingError:
            raise
        except Exception as err:
            _LOGGER.exception("Unexpected error during login")
            raise ConnectionError(f"Unexpected error: {err}") from err

    async def async_get_tank_data(self) -> dict[str, Any]:
        """Fetch tank data from MyFuelPortal.

        Returns:
            Dictionary with tank_level_percent and gallons_remaining

        Raises:
            AuthenticationError: If session expired
            ParsingError: If unable to parse tank data
            ConnectionError: If unable to connect

        """
        try:
            session = await self._get_session()

            # Fetch the Tank page
            tank_url = f"{self.base_url}/Tank"
            _LOGGER.debug("Fetching tank data from %s", tank_url)

            async with session.get(tank_url) as response:
                if response.status == 401 or response.status == 403:
                    raise AuthenticationError("Session expired, please re-authenticate")
                
                if response.status != 200:
                    raise ConnectionError(
                        f"Failed to fetch tank data: HTTP {response.status}"
                    )

                html = await response.text()

                # Check if we were redirected to login (session expired)
                if "Account/Login" in str(response.url):
                    raise AuthenticationError("Session expired, please re-authenticate")

            # Parse the HTML to extract tank data
            soup = BeautifulSoup(html, "html.parser")

            # Extract tank level percentage from progress bar
            progress_bar = soup.find("div", {"class": "progress-bar", "role": "progressbar"})
            if not progress_bar or not progress_bar.get("aria-valuenow"):
                raise ParsingError("Could not find tank level in page")

            try:
                tank_level_percent = float(progress_bar["aria-valuenow"])
            except (ValueError, TypeError) as err:
                raise ParsingError(f"Invalid tank level value: {err}") from err

            # Extract gallons remaining from text
            # Look for pattern like "Approximately 41 gallons in tank"
            gallons_remaining = None
            for div in soup.find_all("div"):
                text = div.get_text(strip=True)
                if "gallons in tank" in text.lower():
                    # Extract the number
                    match = re.search(r"(\d+\.?\d*)\s*gallons", text, re.IGNORECASE)
                    if match:
                        try:
                            gallons_remaining = float(match.group(1))
                            break
                        except ValueError:
                            pass

            if gallons_remaining is None:
                _LOGGER.warning("Could not find gallons remaining in page")
                gallons_remaining = 0.0

            _LOGGER.debug(
                "Parsed tank data: level=%s%%, gallons=%s",
                tank_level_percent,
                gallons_remaining,
            )

            return {
                "tank_level_percent": tank_level_percent,
                "gallons_remaining": gallons_remaining,
            }

        except aiohttp.ClientError as err:
            raise ConnectionError(f"Connection error: {err}") from err
        except (AuthenticationError, ParsingError):
            raise
        except Exception as err:
            _LOGGER.exception("Unexpected error fetching tank data")
            raise ParsingError(f"Unexpected error: {err}") from err

    async def async_close(self) -> None:
        """Close the API session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
