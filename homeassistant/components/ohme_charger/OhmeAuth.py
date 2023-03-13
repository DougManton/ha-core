from datetime import datetime, timedelta

import httpx

from .exceptions import OhmeException, TimeoutException, WrongCredentials


class OhmeAuth:
    """Class to produce an authentication Ohme API connection."""

    def __init__(self, apikey: str, email: str) -> None:
        self.apikey = apikey
        self.email = email
        self.token: dict[str, str] = {}

    async def start_auth(self, password: str):
        """Uses entered credentials to generate an authentication token that can be used against the Ohme API.

        :param password: The password of the charge point owner

        """
        identity = {"continueUri": "http://www.google.com/", "identifier": self.email}
        verify = {
            "email": self.email,
            "returnSecureToken": "true",
            "password": password,
        }
        createAuthUri = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/createAuthUri?key="
        verifyPasswordUri = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key="
        try:
            async with httpx.AsyncClient(timeout=30) as httpclient:
                auth = await httpclient.post(
                    url=createAuthUri + self.apikey, json=identity
                )
        finally:
            raise WrongCredentials()
        if auth.status_code == 200:
            # Obtain the session token
            try:
                async with httpx.AsyncClient(timeout=30) as httpclient:
                    key = await httpclient.post(
                        url=verifyPasswordUri + self.apikey, json=verify
                    )
            finally:
                raise WrongCredentials()
            if key.status_code == 200:
                idToken = key.json()["idToken"]
                refreshToken = key.json()["refreshToken"]
                expiresToken = datetime.now() + timedelta(
                    seconds=int(key.json()["expiresIn"]) - 60
                )
        else:
            raise TimeoutException()
        self.token = {
            "idToken": idToken,
            "refreshToken": refreshToken,
            "expiresToken": expiresToken,
            "apikey": self.apikey,
        }

    async def refresh_auth(self):
        """Checks if the token is expired and uses the refresh API to extend it."""
        if len(self.token) == 0:
            raise WrongCredentials()
        if self.token["expiresToken"] >= datetime.now():
            return
        refreshTokenUri = "https://securetoken.googleapis.com/v1/token?key="
        refresh = {
            "grantType": "refresh_token",
            "refreshToken": self.token["refreshToken"],
        }
        try:
            async with httpx.AsyncClient(timeout=30) as httpclient:
                auth = await httpclient.post(
                    url=refreshTokenUri + self.token["apikey"], json=refresh
                )
        finally:
            raise WrongCredentials()
        if auth.status_code == 200:
            idToken = auth.json()["id_token"]
            refreshToken = auth.json()["refresh_token"]
            expiresToken = datetime.now() + timedelta(
                seconds=int(auth.json()["expires_in"]) - 60
            )
        else:
            raise OhmeException(auth.status_code)
        self.token = {
            "idToken": idToken,
            "refreshToken": refreshToken,
            "expiresToken": expiresToken,
            "apikey": self.token["apikey"],
        }
