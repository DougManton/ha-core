from datetime import datetime
import json

import httpx

from .OhmeAuth import OhmeAuth


class OhmeCharger:
    """Instantiate the class by passing-in an authentication token."""

    def __init__(self, auth: OhmeAuth) -> None:
        self.auth = auth
        self.disconnect = False
        self.session = {
            "sessionId": "null",
            "mode": "DISCONNECTED",
        }
        self.account = {
            "user": {
                "id": "",
            },
            "cars": [{"id": ""}],
            "chargeDevices": [{"id": "null"}],
        }
        self.chargeStart = datetime.now()
        self.chargeEnd = datetime.now()
        self.id = ""
        self.charge_status = ""
        self.model = ""

    def __str__(self) -> str:
        return self.account["chargeDevices"][0]["id"]

    # Defines the available solar cars (limited) and the Kona (max rate) which can be used as inputs to force specific charge rates
    cars = {
        6: '{"manufacturerId":"no_car_api_JVbisjT6fisJ04MSqZo0","model":{"modelDetailName":"Solar_6A_1.4kW","make":"SOLAR","id":"SOLAR_DEMO 6A","energyCapacityWh":50000,"averageWhPerKm":191,"imageUrl":"","powerLimits":{"maxDemandW":1400},"specifiedRangeKm":262,"modelName":"6A_1.4kW (2022)","providesBatterySoc":false,"modelYear":2022},"vehicleStatus":{}}',
        10: '{"manufacturerId":"no_car_api_0T2Qh9THS24jRrxFUEIz","model":{"modelDetailName":"Solar_10A_2kW","make":"SOLAR","id":"SOLAR_DEMO","energyCapacityWh":50000,"averageWhPerKm":191,"imageUrl":"","powerLimits":{"maxDemandW":2400},"specifiedRangeKm":262,"modelName":"10A_2kW (2022)","providesBatterySoc":false,"modelYear":2022},"vehicleStatus":{}}',
        15: '{"manufacturerId":"no_car_api_OP68mL2p6NKjjixjSzfy","model":{"modelDetailName":"Solar_13A_3kW","make":"SOLAR","id":"SOLAR_DEMO 13A","energyCapacityWh":50000,"averageWhPerKm":190,"imageUrl":"","powerLimits":{"maxDemandW":3600},"specifiedRangeKm":262,"modelName":"13A_3kW (2023)","providesBatterySoc":false,"modelYear":2023},"vehicleStatus":{}}',
        21: '{"manufacturerId":"no_car_api_fzYQpg9rCVrLvKkcq3DT","model":{"modelDetailName":"Solar_5kW","make":"SOLAR","id":"SOLAR_DEMO 21A/5kW","energyCapacityWh":60000,"averageWhPerKm":191,"imageUrl":"","powerLimits":{"maxDemandW":5000},"specifiedRangeKm":262,"modelName":"21A_5kW (2023)","providesBatterySoc":false,"modelYear":2023},"vehicleStatus":{}}',
        32: '{"manufacturerId":"no_car_api_KBUqSYtcGG0pOHupY1I1","model":{"modelDetailName":"Electric 64 kWh","make":"HYUNDAI","id":"HYUNDAI 2018 Kona Electric 64 kWh","energyCapacityWh":67500,"averageWhPerKm":165,"imageUrl":"https:\\/\\/s3.eu-west-2.amazonaws.com\\/ohme-images-public\\/cars\\/evdb\\/BEV\\/1126\\/enhanced.png","powerLimits":{"maxDemandW":7680},"specifiedRangeKm":449,"modelName":"Kona (2018)","providesBatterySoc":false,"modelYear":2018},"vehicleStatus":{}}',
        48: '{"id":"8e49d106-0b9b-4687-af84-7b37c11ac7db","manufacturerId":"no_car_api_0jjeoFzwvPXzVOZQ1ILL","manufacturerUserId":null,"vin":null,"name":null,"model":{"id":"TESLA 2022 Model Y Long Range Dual Motor","make":"TESLA","modelName":"Model Y (2022)","modelYear":2022,"modelDetailName":"Long Range Dual Motor","imageUrl":"https://s3.eu-west-2.amazonaws.com/ohme-images-public/cars/evdb/BEV/1182/enhanced.png","powerLimits":{"maxDemandW":11520,"minDemandW":null,"maxSupplyW":null,"minSupplyW":null},"averageWhPerKm":168,"energyCapacityWh":75000,"specifiedRangeKm":507,"providesBatterySoc":false,"rangeKm":507.0},"ownerUserId":"8DVnXXVS3ZajKT5hXoeguo3IWnt1","batterySoc":null,"licensePlateId":null,"startChargeSupported":null,"vehicleStatus":{"odometerReadingKm":null,"maxSoc":null,"rangeDisplaySelection":null,"soc":null,"climate":null,"chargingStatus":null,"availableChargingPowerW":null,"chargingSpeedKmh":null,"timestamp":null},"userNotes":null,"userDefined":false}',
    }

    async def start_charge(self) -> bool:
        """Uses the global token to call the Ohme API to start charging."""
        await self.auth.refresh_auth()
        chargeSessionsUri = (
            "https://api.ohme.io/v1/chargeSessions/"
            + self.session["chargeDevice"]["id"]
            + "/rule/?enableMaxPrice=false&preconditionLengthMins=30&maxCharge=true"
        )
        headers = {"Authorization": "Firebase " + self.auth.token["idToken"]}
        async with httpx.AsyncClient(timeout=30) as httpclient:
            charge = await httpclient.put(url=chargeSessionsUri, headers=headers)
        if charge.status_code == 200:
            self.chargeStart = datetime.now()
            self.chargeEnd = datetime.now()
            return True
        return False

    async def stop_charge(self) -> bool:
        """Uses the global token to call the Ohme API to stop charging."""
        await self.auth.refresh_auth()
        chargeSessionsUri = (
            "https://api.ohme.io/v1/chargeSessions/"
            + self.session["chargeDevice"]["id"]
            + "/stop"
        )
        headers = {"Authorization": "Firebase " + self.auth.token["idToken"]}
        async with httpx.AsyncClient(timeout=30) as httpclient:
            charge = await httpclient.put(url=chargeSessionsUri, headers=headers)
        if charge.status_code == 200:
            return True
        return False

    async def resume_charge(self) -> bool:
        """Uses the global token to call the Ohme API to resume charging."""
        await self.auth.refresh_auth()
        chargeSessionsUri = (
            "https://api.ohme.io/v1/chargeSessions/"
            + self.session["chargeDevice"]["id"]
            + "/resume"
        )
        headers = {"Authorization": "Firebase " + self.auth.token["idToken"]}
        async with httpx.AsyncClient(timeout=30) as httpclient:
            charge = await httpclient.put(url=chargeSessionsUri, headers=headers)
        if charge.status_code == 200:
            return True
        return False

    async def switch_amps(self, amperage: int) -> bool:
        """Uses the global token to call the Ohme API to set the car to one with the desired amperage.

        :param amperage: the requested amperage for charging

        """
        await self.auth.refresh_auth()
        # Find the highest supported amperage equal or lower to the one requested
        lower = []
        for i in self.cars:
            if i <= amperage:
                lower.append(i)
        if len(lower) > 0:
            amps = max(lower)
            carSwitchUri = "https://api.ohme.io/v1/cars"
            headers = {"Authorization": "Firebase " + self.auth.token["idToken"]}
            async with httpx.AsyncClient(timeout=30) as httpclient:
                car = await httpclient.post(
                    url=carSwitchUri, headers=headers, json=json.loads(self.cars[amps])
                )
            await self.refresh()
            if car.status_code == 200:
                return True
            return False
        return False

    def get_charge_times(self) -> list:
        """The API doesn't return the scheduled time for the next charge but it does return
        the points to render a graph.  The final point before the first increase corresponds
        to when the charge starts, the final point to show an increase corresponds to when
        the charge ends.
        """
        times = []
        start = 0
        started = 0
        startTime = 0
        endTime = 0
        endCharge = 0
        for point in self.session["chargeGraph"]["points"]:
            if point["y"] > start and started == 0:
                times.append(round(self.session["startTime"] / 1000) + round(startTime))
                started = 1
            elif point["y"] == endCharge and started == 1:
                times.append(round(self.session["startTime"] / 1000) + round(endTime))
                started = 0
            startTime = point["x"]
            start = point["y"]
            endCharge = point["y"]
            endTime = point["x"]
        return times

    async def get_charge_sessions(self) -> str:
        """Uses the global token to call the Ohme API to get current session details.  Refreshes the token if it's expired."""
        await self.auth.refresh_auth()
        chargeSessionsUri = "https://api.ohme.io/v1/chargeSessions"
        headers = {"Authorization": "Firebase " + self.auth.token["idToken"]}
        async with httpx.AsyncClient(timeout=30) as httpclient:
            sessions = await httpclient.get(url=chargeSessionsUri, headers=headers)
        return sessions.json()[0]

    async def get_account_info(self) -> str:
        """Uses the global token to call the Ohme API to get current account details.  Refreshes the token if it's expired."""
        await self.auth.refresh_auth()
        accountInfoUri = (
            "https://api.ohme.io/v1/users/me/account?timeZone=Europe%252FLondon"
        )
        headers = {"Authorization": "Firebase " + self.auth.token["idToken"]}
        async with httpx.AsyncClient(timeout=30) as httpclient:
            account = await httpclient.get(url=accountInfoUri, headers=headers)
        return account.json()

    async def refresh(self) -> dict:
        self.session = await self.get_charge_sessions()
        self.charge_status = self.session["mode"]
        self.account = await self.get_account_info()
        if self.session["mode"] == "DISCONNECTED":
            self.disconnect = True
        else:
            self.disconnect = False
        return {"charger_id": self.id, "charge_status": self.charge_status}

    async def setup(self):
        self.session = await self.get_charge_sessions()
        self.id = self.account["chargeDevices"][0]["id"]
        self.charge_status = self.session["mode"]
        self.model = self.account["chargeDevices"][0]["modelTypeDisplayName"]
        return {self.id: self}

    @property
    def max_amps(self) -> int:
        """Returns the number of amps the charger is configured to supply"""
        return round(
            self.account["cars"][0]["model"]["powerLimits"]["maxDemandW"] / 240,
            0,
        )

    @property
    def current_amps(self) -> int:
        """Returns the number of amps the charger is currently supplying"""
        if self.session["power"] is not None:
            return self.session["power"]["amp"]
        return 0

    @property
    def current_power(self) -> int:
        """Returns the number of watts the charger is currently supplying"""
        if self.session["power"] is not None:
            return self.session["power"]["watt"]
        return 0

    @property
    def current_voltage(self) -> int:
        """Returns the number of volts the charger is currently supplying"""
        if self.session["power"] is not None:
            return self.session["power"]["volt"]
        return 0
