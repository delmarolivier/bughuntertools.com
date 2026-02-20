#!/home/delmar/.openclaw/workspace/projects/altclaw/analytics/venv/bin/python3
"""
Generate daily analytics report and send to Telegram.

Reads analytics data and formats it for human consumption.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional


class ReportGenerator:
    """Generate analytics reports."""
    
    def __init__(self, analytics_dir: Path):
        self.analytics_dir = analytics_dir
        self.history_dir = analytics_dir / "history"
    
    def load_data(self, date: str) -> Optional[Dict[str, Any]]:
        """Load analytics data for a specific date."""
        file_path = self.history_dir / f"{date}.json"
        if not file_path.exists():
            return None
        
        with open(file_path) as f:
            return json.load(f)
    
    def calculate_comparison(self, today_data: Dict, yesterday_data: Optional[Dict]) -> Dict[str, float]:
        """Calculate day-over-day percentage changes."""
        if not yesterday_data:
            return {}
        
        comparisons = {}
        metrics = ["total_users", "total_pageviews", "total_sessions"]
        
        for metric in metrics:
            today_val = today_data.get(metric, 0)
            yesterday_val = yesterday_data.get(metric, 0)
            
            if yesterday_val == 0:
                comparisons[metric] = 0.0
            else:
                change = ((today_val - yesterday_val) / yesterday_val) * 100
                comparisons[metric] = round(change, 1)
        
        return comparisons
    
    def format_duration(self, seconds: float) -> str:
        """Format seconds as human-readable duration."""
        if seconds < 60:
            return f"{int(seconds)}s"
        else:
            mins = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{mins}m {secs}s"
    
    def generate_telegram_report(self, date: str) -> str:
        """Generate formatted report for Telegram."""
        data = self.load_data(date)
        if not data:
            return f"❌ No analytics data found for {date}"
        
        # Load yesterday for comparison
        yesterday = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        yesterday_data = self.load_data(yesterday)
        comparison = self.calculate_comparison(data, yesterday_data)
        
        # Build report
        lines = [
            f"📊 **AltClaw Daily Analytics - {date}**",
            "",
            "👥 **Traffic:**",
        ]
        
        # Users with comparison
        users_change = comparison.get("total_users", 0)
        change_emoji = "📈" if users_change > 0 else "📉" if users_change < 0 else "➡️"
        lines.append(f"  • {data['total_users']} users ({change_emoji} {users_change:+.1f}% vs yesterday)")
        
        # Other metrics
        lines.extend([
            f"  • {data['total_sessions']} sessions",
            f"  • {data['total_pageviews']} pageviews",
            f"  • {self.format_duration(data['avg_session_duration'])} avg session",
            "",
            "🔝 **Top Articles:**",
        ])
        
        # Top pages (limit to top 5, highlight articles)
        for i, page in enumerate(data["top_pages"][:5], 1):
            page_path = page["page"]
            views = page["views"]
            
            # Simplify path for display
            if "/articles/" in page_path:
                title = page_path.split("/articles/")[1].replace(".html", "").replace("-", " ").title()
                emoji = "🔥" if i == 1 else ""
                lines.append(f"  {i}. {title} ({views} views) {emoji}")
            elif page_path == "/":
                lines.append(f"  {i}. Homepage ({views} views)")
            else:
                lines.append(f"  {i}. {page_path} ({views} views)")
        
        lines.extend([
            "",
            "📍 **Traffic Sources:**",
        ])
        
        # Traffic sources with percentages
        total_traffic = sum(data["traffic_sources"].values())
        for source, count in sorted(data["traffic_sources"].items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                pct = (count / total_traffic * 100) if total_traffic > 0 else 0
                source_display = source.capitalize()
                lines.append(f"  • {source_display}: {count} ({pct:.0f}%)")
        
        lines.extend([
            "",
            "🌍 **Top Countries:**",
        ])
        
        # Top 3 countries
        for country in data["countries"][:3]:
            name = country["country"]
            users = country["users"]
            pct = (users / data["total_users"] * 100) if data["total_users"] > 0 else 0
            lines.append(f"  • {name}: {users} ({pct:.0f}%)")
        
        # Bounce rate
        lines.extend([
            "",
            f"📉 **Bounce Rate:** {data['bounce_rate']:.1f}%",
        ])
        
        # Insights
        lines.extend([
            "",
            "✅ **What's Working:**",
        ])
        
        # Dynamic insights based on data
        if data["traffic_sources"].get("organic", 0) > data["total_users"] * 0.5:
            lines.append("  - Strong organic search performance")
        
        if data["top_pages"] and data["top_pages"][0]["views"] > 50:
            top_article = data["top_pages"][0]["page"]
            if "/articles/" in top_article:
                lines.append("  - Breaking news articles driving traffic")
        
        if data["bounce_rate"] < 55:
            lines.append("  - Good engagement (low bounce rate)")
        
        lines.extend([
            "",
            "⚠️ **What Needs Work:**",
        ])
        
        # Areas for improvement
        if data["bounce_rate"] > 60:
            lines.append(f"  - High bounce rate ({data['bounce_rate']:.0f}% - target <50%)")
        
        if data["traffic_sources"].get("referral", 0) < data["total_users"] * 0.1:
            lines.append("  - Low referral traffic (build backlinks)")
        
        if data["traffic_sources"].get("social", 0) < 5:
            lines.append("  - Minimal social media traffic")
        
        if data["total_users"] < 100:
            lines.append("  - Growing audience (needs more content)")
        
        return "\n".join(lines)


def main():
    """Generate report for yesterday and print to stdout."""
    workspace = Path("/home/delmar/.openclaw/workspace")
    analytics_dir = workspace / "projects/altclaw/analytics"
    
    generator = ReportGenerator(analytics_dir)
    
    # Generate report for yesterday
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    report = generator.generate_telegram_report(yesterday)
    
    print(report)
    
    return report


if __name__ == "__main__":
    main()
