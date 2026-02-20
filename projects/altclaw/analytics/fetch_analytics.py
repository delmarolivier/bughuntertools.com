#!/home/delmar/.openclaw/workspace/projects/altclaw/analytics/venv/bin/python3
"""
Fetch analytics data from Google Analytics 4 API.

Uses GA4 Data API v1 to pull daily metrics for bughuntertools.com.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Dimension,
    Metric,
)
from google.oauth2 import service_account


class GA4Fetcher:
    """Fetch analytics data from GA4."""
    
    def __init__(self, config_path: Path):
        """Initialize with config file."""
        with open(config_path) as f:
            self.config = json.load(f)
        
        # Authenticate
        credentials = service_account.Credentials.from_service_account_file(
            self.config["service_account_key_path"]
        )
        self.client = BetaAnalyticsDataClient(credentials=credentials)
        self.property_id = self.config["ga4_property_id"]
    
    def fetch_daily_report(self, date: str = None) -> Dict[str, Any]:
        """
        Fetch analytics for a specific date (default: yesterday).
        
        Args:
            date: YYYY-MM-DD format, defaults to yesterday
        
        Returns:
            Dict with analytics data
        """
        if date is None:
            date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Fetch multiple reports
        overview = self._fetch_overview(date)
        top_pages = self._fetch_top_pages(date)
        traffic_sources = self._fetch_traffic_sources(date)
        countries = self._fetch_countries(date)
        
        return {
            "date": date,
            "fetched_at": datetime.now().isoformat(),
            **overview,
            "top_pages": top_pages,
            "traffic_sources": traffic_sources,
            "countries": countries,
        }
    
    def _fetch_overview(self, date: str) -> Dict[str, Any]:
        """Fetch overview metrics."""
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            date_ranges=[DateRange(start_date=date, end_date=date)],
            metrics=[
                Metric(name="activeUsers"),
                Metric(name="sessions"),
                Metric(name="screenPageViews"),
                Metric(name="averageSessionDuration"),
                Metric(name="bounceRate"),
            ],
        )
        
        response = self.client.run_report(request)
        
        if not response.rows:
            return {
                "total_users": 0,
                "total_sessions": 0,
                "total_pageviews": 0,
                "avg_session_duration": 0.0,
                "bounce_rate": 0.0,
            }
        
        row = response.rows[0]
        return {
            "total_users": int(row.metric_values[0].value),
            "total_sessions": int(row.metric_values[1].value),
            "total_pageviews": int(row.metric_values[2].value),
            "avg_session_duration": float(row.metric_values[3].value),
            "bounce_rate": float(row.metric_values[4].value) * 100,  # Convert to percentage
        }
    
    def _fetch_top_pages(self, date: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch top pages by views."""
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            date_ranges=[DateRange(start_date=date, end_date=date)],
            dimensions=[Dimension(name="pagePath")],
            metrics=[Metric(name="screenPageViews")],
            order_bys=[{"metric": {"metric_name": "screenPageViews"}, "desc": True}],
            limit=limit,
        )
        
        response = self.client.run_report(request)
        
        return [
            {
                "page": row.dimension_values[0].value,
                "views": int(row.metric_values[0].value),
            }
            for row in response.rows
        ]
    
    def _fetch_traffic_sources(self, date: str) -> Dict[str, int]:
        """Fetch traffic by source/medium."""
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            date_ranges=[DateRange(start_date=date, end_date=date)],
            dimensions=[Dimension(name="sessionDefaultChannelGroup")],
            metrics=[Metric(name="activeUsers")],
        )
        
        response = self.client.run_report(request)
        
        # Map GA4 channel groups to simplified categories
        channel_map = {
            "Organic Search": "organic",
            "Direct": "direct",
            "Referral": "referral",
            "Organic Social": "social",
            "Paid Search": "paid",
            "Email": "email",
        }
        
        sources = {"organic": 0, "direct": 0, "referral": 0, "social": 0, "other": 0}
        
        for row in response.rows:
            channel = row.dimension_values[0].value
            users = int(row.metric_values[0].value)
            
            mapped = channel_map.get(channel, "other")
            sources[mapped] += users
        
        return sources
    
    def _fetch_countries(self, date: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch top countries by users."""
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            date_ranges=[DateRange(start_date=date, end_date=date)],
            dimensions=[Dimension(name="country")],
            metrics=[Metric(name="activeUsers")],
            order_bys=[{"metric": {"metric_name": "activeUsers"}, "desc": True}],
            limit=limit,
        )
        
        response = self.client.run_report(request)
        
        return [
            {
                "country": row.dimension_values[0].value,
                "users": int(row.metric_values[0].value),
            }
            for row in response.rows
        ]


def main():
    """Fetch and save daily analytics."""
    workspace = Path("/home/delmar/.openclaw/workspace")
    config_path = workspace / "projects/altclaw/analytics/config.json"
    history_dir = workspace / "projects/altclaw/analytics/history"
    
    fetcher = GA4Fetcher(config_path)
    
    # Fetch yesterday's data
    data = fetcher.fetch_daily_report()
    
    # Save to history
    date = data["date"]
    output_file = history_dir / f"{date}.json"
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ Analytics fetched for {date}")
    print(f"  Saved to: {output_file}")
    print(f"  Users: {data['total_users']}")
    print(f"  Pageviews: {data['total_pageviews']}")
    
    return data


if __name__ == "__main__":
    main()
