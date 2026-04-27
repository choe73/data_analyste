"""Specialized collector implementations for different data sources."""

import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.base_collector import BaseCollector


class WorldBankCollector(BaseCollector):
    """
    Collector for World Bank Open Data API.
    
    Demonstrates:
    - Inheritance: Extends BaseCollector
    - Polymorphism: Implements fetch_data() and transform_data()
    - Robustness: Handles API errors gracefully
    """

    BASE_URL = "https://api.worldbank.org/v2"

    # Key indicators for Cameroon
    INDICATORS = {
        "SP.POP.TOTL": "Population totale",
        "SP.POP.GROW": "Croissance démographique",
        "NY.GDP.MKTP.CD": "PIB (USD)",
        "NY.GDP.PCAP.CD": "PIB par habitant",
        "AG.LND.FRST.ZS": "Forêt (% terres)",
        "SE.PRM.ENRR": "Scolarisation primaire",
        "SE.SEC.ENRR": "Scolarisation secondaire",
        "SH.DYN.MORT": "Mortalité infantile",
        "SH.STA.BASS.ZS": "Accès assainissement",
        "SH.H2O.BASW.ZS": "Accès eau potable",
        "EG.ELC.ACCS.ZS": "Accès électricité",
        "IS.ROD.DNST.K2": "Densité routière",
        "AG.PRD.FOOD.XD": "Production alimentaire",
        "FP.CPI.TOTL.ZG": "Inflation",
        "SL.UEM.TOTL.ZS": "Chômage",
    }

    async def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch data from World Bank API.
        
        Args:
            country_code: Country code (default: CMR for Cameroon)
            indicator: Indicator code
            start_year: Start year
            end_year: End year
            
        Returns:
            List of data points
        """
        country_code = kwargs.get("country_code", "CMR")
        indicator = kwargs.get("indicator", "SP.POP.TOTL")
        start_year = kwargs.get("start_year", 2000)
        end_year = kwargs.get("end_year", 2023)

        try:
            url = f"{self.BASE_URL}/country/{country_code}/indicator/{indicator}"
            params = {
                "format": "json",
                "per_page": 100,
                "date": f"{start_year}:{end_year}",
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            if len(data) > 1 and data[1]:
                return data[1]
            return []

        except httpx.HTTPError as e:
            raise Exception(f"World Bank API error: {str(e)}")

    async def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform World Bank data into standardized format.
        
        Args:
            raw_data: Raw data from API
            
        Returns:
            Transformed data
        """
        transformed = []
        for item in raw_data:
            if item.get("value") is not None:
                transformed.append({
                    "year": item.get("date"),
                    "value": float(item.get("value")),
                    "country": item.get("countryiso3code"),
                    "indicator": item.get("indicator", {}).get("id"),
                })
        return transformed

    async def collect_all_indicators(
        self,
        country_code: str = "CMR",
        start_year: int = 2000,
        end_year: int = 2023,
    ) -> Dict[str, Any]:
        """
        Collect all World Bank indicators for a country.
        
        Args:
            country_code: Country code
            start_year: Start year
            end_year: End year
            
        Returns:
            Collection summary
        """
        results = {
            "source": "world_bank",
            "country": country_code,
            "records_collected": 0,
            "indicators_processed": 0,
            "errors": [],
        }

        for indicator_code, indicator_name in self.INDICATORS.items():
            try:
                # Fetch data
                raw_data = await self.fetch_data(
                    country_code=country_code,
                    indicator=indicator_code,
                    start_year=start_year,
                    end_year=end_year,
                )

                if not raw_data:
                    continue

                # Save raw data
                await self.save_raw_data(
                    source_name="world_bank",
                    dataset_name=f"wb_{indicator_code}",
                    data={
                        "indicator": indicator_code,
                        "indicator_name": indicator_name,
                        "country": country_code,
                        "data": raw_data,
                    },
                )

                # Transform and save processed data
                transformed = await self.transform_data(raw_data)

                for item in transformed:
                    domain = self._get_domain(indicator_code)
                    await self.save_processed_data(
                        domain=domain,
                        region=country_code,
                        indicator=indicator_name,
                        value=item["value"],
                        unit="varies",
                        date=datetime(int(item["year"]), 1, 1),
                        metadata={"indicator_code": indicator_code},
                    )

                results["records_collected"] += len(transformed)
                results["indicators_processed"] += 1

            except Exception as e:
                results["errors"].append({
                    "indicator": indicator_code,
                    "error": str(e),
                })

        return results

    @staticmethod
    def _get_domain(indicator_code: str) -> str:
        """Determine domain based on indicator code."""
        if "GDP" in indicator_code or "FP.CPI" in indicator_code:
            return "economy"
        elif "SH." in indicator_code:
            return "health"
        elif "SE." in indicator_code:
            return "education"
        elif "AG.LND" in indicator_code or "EG." in indicator_code:
            return "environment"
        else:
            return "demography"


class NASAPowerCollector(BaseCollector):
    """
    Collector for NASA POWER meteorological data.
    
    Demonstrates:
    - Inheritance: Extends BaseCollector
    - Polymorphism: Different API structure than WorldBank
    """

    BASE_URL = "https://power.larc.nasa.gov/api/v1/aggregate"

    async def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch meteorological data from NASA POWER API.
        
        Args:
            latitude: Latitude
            longitude: Longitude
            start_year: Start year
            end_year: End year
            
        Returns:
            Meteorological data
        """
        latitude = kwargs.get("latitude", 3.8667)  # Cameroon center
        longitude = kwargs.get("longitude", 11.5167)
        start_year = kwargs.get("start_year", 2020)
        end_year = kwargs.get("end_year", 2023)

        try:
            params = {
                "parameters": "T2M,PRECTOTCORR,WS10M",
                "community": "RE",
                "longitude": longitude,
                "latitude": latitude,
                "start": f"{start_year}0101",
                "end": f"{end_year}1231",
                "format": "JSON",
            }

            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()

            data = response.json()
            if "properties" in data and "parameter" in data["properties"]:
                return [data["properties"]["parameter"]]
            return []

        except httpx.HTTPError as e:
            raise Exception(f"NASA POWER API error: {str(e)}")

    async def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform NASA POWER data into standardized format."""
        transformed = []
        for param_dict in raw_data:
            for param_name, values in param_dict.items():
                for date_str, value in values.items():
                    if value is not None:
                        transformed.append({
                            "parameter": param_name,
                            "date": date_str,
                            "value": float(value),
                        })
        return transformed

    async def collect_meteo_data(
        self,
        latitude: float = 3.8667,
        longitude: float = 11.5167,
        start_year: int = 2020,
        end_year: int = 2023,
    ) -> Dict[str, Any]:
        """Collect meteorological data for a region."""
        results = {
            "source": "nasa_power",
            "latitude": latitude,
            "longitude": longitude,
            "records_collected": 0,
            "errors": [],
        }

        try:
            raw_data = await self.fetch_data(
                latitude=latitude,
                longitude=longitude,
                start_year=start_year,
                end_year=end_year,
            )

            if raw_data:
                await self.save_raw_data(
                    source_name="nasa_power",
                    dataset_name="nasa_meteo",
                    data=raw_data[0] if raw_data else {},
                )

                transformed = await self.transform_data(raw_data)
                for item in transformed:
                    await self.save_processed_data(
                        domain="environment",
                        region=f"lat_{latitude}_lon_{longitude}",
                        indicator=item["parameter"],
                        value=item["value"],
                        unit="varies",
                        date=datetime.strptime(item["date"], "%Y%m%d"),
                    )

                results["records_collected"] = len(transformed)

        except Exception as e:
            results["errors"].append(str(e))

        return results


class FAOCollector(BaseCollector):
    """
    Collector for FAO (Food and Agriculture Organization) data.
    
    Demonstrates:
    - Inheritance: Extends BaseCollector
    - Polymorphism: Uses POST requests instead of GET
    """

    BASE_URL = "https://fenixservices.fao.org/faostat/api/v1/en/data"

    async def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch FAO data.
        
        Args:
            domain: FAO domain code (e.g., QCL for crops)
            area: Area code (e.g., 45 for Cameroon)
            years: List of years
            
        Returns:
            FAO data
        """
        domain = kwargs.get("domain", "QCL")
        area = kwargs.get("area", "45")  # Cameroon
        years = kwargs.get("years", ["2020", "2021", "2022", "2023"])

        try:
            url = f"{self.BASE_URL}/{domain}"
            payload = {
                "area": [area],
                "years": years,
            }

            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            if "data" in data:
                return data["data"]
            return []

        except httpx.HTTPError as e:
            raise Exception(f"FAO API error: {str(e)}")

    async def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform FAO data into standardized format."""
        transformed = []
        for item in raw_data:
            if item.get("Value") is not None:
                transformed.append({
                    "year": item.get("Year"),
                    "value": float(item.get("Value")),
                    "item": item.get("Item"),
                    "element": item.get("Element"),
                })
        return transformed

    async def collect_agricultural_data(
        self,
        domain: str = "QCL",
        area: str = "45",
        start_year: int = 2020,
        end_year: int = 2023,
    ) -> Dict[str, Any]:
        """Collect agricultural data."""
        results = {
            "source": "fao",
            "domain": domain,
            "area": area,
            "records_collected": 0,
            "errors": [],
        }

        try:
            years = [str(y) for y in range(start_year, end_year + 1)]
            raw_data = await self.fetch_data(
                domain=domain,
                area=area,
                years=years,
            )

            if raw_data:
                await self.save_raw_data(
                    source_name="fao",
                    dataset_name=f"fao_{domain}",
                    data={"domain": domain, "data": raw_data},
                )

                transformed = await self.transform_data(raw_data)
                for item in transformed:
                    await self.save_processed_data(
                        domain="agriculture",
                        region=area,
                        indicator=f"{item['item']} - {item['element']}",
                        value=item["value"],
                        unit="varies",
                        date=datetime(int(item["year"]), 1, 1),
                    )

                results["records_collected"] = len(transformed)

        except Exception as e:
            results["errors"].append(str(e))

        return results
