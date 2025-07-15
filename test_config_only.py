#!/usr/bin/env python3
"""
Simple FootyStats Configuration Test

This script tests the basic configuration without making actual API calls.
It verifies that the configuration is loaded correctly and URLs are generated properly.
"""

import sys
from datetime import datetime

def test_configuration():
    """Test FootyStats configuration loading and URL generation."""
    
    print("🔍 FootyStats Configuration Test")
    print("=" * 50)
    
    try:
        # Import configuration
        from footystats_config import (
            FOOTYSTATS_API_KEY,
            FOOTYSTATS_LEAGUE_IDS,
            LEAGUE_BY_COUNTRY,
            FOOTYSTATS_BASE_URL,
            get_league_teams_url,
            get_league_season_url
        )
        print("✅ Configuration imported successfully")
        
    except ImportError as e:
        print(f"❌ Failed to import configuration: {e}")
        return False
    
    # Test basic configuration
    print(f"\n📋 Basic Configuration:")
    print(f"  🔑 API Key: {FOOTYSTATS_API_KEY[:20]}...")
    print(f"  🌐 Base URL: {FOOTYSTATS_BASE_URL}")
    print(f"  📊 Total leagues: {len(FOOTYSTATS_LEAGUE_IDS)}")
    print(f"  🌍 Countries: {len(LEAGUE_BY_COUNTRY)}")
    
    # Test URL generation for major leagues
    print(f"\n🔗 Testing URL Generation:")
    major_leagues = {
        "English Premier League": 13943,
        "Spanish La Liga": 13942,
        "German Bundesliga": 13951,
        "Italian Serie A": 13952,
        "French Ligue 1": 13947
    }
    
    for league_name, season_id in major_leagues.items():
        print(f"\n🏆 {league_name} (Season ID: {season_id}):")
        
        # Generate season URL
        season_url = get_league_season_url(season_id)
        print(f"  📈 Season URL: {season_url}")
        
        # Generate teams URL
        teams_url = get_league_teams_url(season_id, include_stats=True)
        print(f"  👥 Teams URL: {teams_url}")
        
        # Verify URL structure
        if f"season_id={season_id}" in season_url and f"season_id={season_id}" in teams_url:
            print(f"  ✅ URLs generated correctly")
        else:
            print(f"  ❌ URL generation error")
            return False
    
    # Test league organization by country
    print(f"\n🌍 League Organization by Country:")
    for country, leagues in list(LEAGUE_BY_COUNTRY.items())[:5]:  # Show first 5 countries
        print(f"  {country}: {len(leagues)} leagues")
        for league_name, season_id in leagues.items():
            print(f"    - {league_name}: {season_id}")
    
    # Test that all season IDs are numeric
    print(f"\n🔢 Season ID Validation:")
    invalid_ids = []
    for league_name, season_id in FOOTYSTATS_LEAGUE_IDS.items():
        if not isinstance(season_id, int) or season_id < 10000:
            invalid_ids.append((league_name, season_id))
    
    if invalid_ids:
        print(f"  ❌ Found {len(invalid_ids)} invalid season IDs:")
        for name, sid in invalid_ids:
            print(f"    - {name}: {sid}")
        return False
    else:
        print(f"  ✅ All {len(FOOTYSTATS_LEAGUE_IDS)} season IDs are valid")
    
    # Summary
    print(f"\n📊 Configuration Summary:")
    print(f"  ✅ Configuration loaded successfully")
    print(f"  ✅ {len(FOOTYSTATS_LEAGUE_IDS)} leagues configured")
    print(f"  ✅ {len(LEAGUE_BY_COUNTRY)} countries covered")
    print(f"  ✅ URL generation working correctly")
    print(f"  ✅ All season IDs are valid")
    
    print(f"\n🚀 Configuration Status: READY")
    print(f"📅 Test completed at: {datetime.now().isoformat()}")
    
    return True

def main():
    """Main function."""
    success = test_configuration()
    
    if success:
        print(f"\n🎉 All configuration tests passed!")
        print(f"💡 The FootyStats API integration is properly configured.")
        print(f"🔧 You can now use the updated API endpoints.")
    else:
        print(f"\n❌ Configuration tests failed!")
        print(f"🔧 Please check the configuration files.")
        sys.exit(1)

if __name__ == "__main__":
    main()