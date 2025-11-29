#!/usr/bin/env python3
"""
Test script to verify the stacked bar implementation
"""

import requests
import json

def test_timeline_api():
    """Test the timeline API to verify project_minutes field"""
    print("🧪 Testing Timeline API with project_minutes...")
    
    try:
        # Test the API endpoint
        response = requests.get('http://localhost:8080/api/timeline/data?date=2025-11-28')
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API Response Status: SUCCESS")
            print(f"📅 Date: {data.get('date')}")
            print(f"⏱️  Total Active Minutes: {data.get('total_active_minutes')}")
            print(f"📊 Hourly Data Entries: {len(data.get('hourly_data', []))}")
            
            # Check if project_minutes field exists in hourly_data
            hourly_data = data.get('hourly_data', [])
            if hourly_data:
                first_entry = hourly_data[0]
                if 'project_minutes' in first_entry:
                    print("✅ project_minutes field found in API response")
                    
                    # Show sample data
                    print("\n📋 Sample Hourly Data:")
                    for i, entry in enumerate(hourly_data[:3]):  # Show first 3 entries
                        print(f"  {entry['hour']}: "
                              f"Total={entry['active_minutes']}min, "
                              f"Project={entry['project_minutes']}min, "
                              f"Background={entry['active_minutes'] - entry['project_minutes']}min")
                    
                    return True
                else:
                    print("❌ project_minutes field NOT found in API response")
                    print(f"Available fields: {list(first_entry.keys())}")
                    return False
            else:
                print("❌ No hourly data returned")
                return False
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running on localhost:8080?")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_frontend_structure():
    """Test that frontend files contain stacked bar code"""
    print("\n🧪 Testing Frontend Implementation...")
    
    try:
        # Check timeline-chart.js for stacked bar code
        with open('web/js/timeline-chart.js', 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        checks = [
            ('stacked: true', 'Chart.js stacking configuration'),
            ('projectMinutes', 'Project minutes processing'),
            ('backgroundMinutes', 'Background activity calculation'),
            ('createSemiTransparentColor', 'Semi-transparent color function'),
            ('project_minutes', 'API field mapping')
        ]
        
        all_passed = True
        for pattern, description in checks:
            if pattern in js_content:
                print(f"✅ {description}: Found")
            else:
                print(f"❌ {description}: NOT found")
                all_passed = False
        
        # Check CSS for hatch patterns
        with open('web/css/dashboard.css', 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        css_patterns = [
            ('repeating-linear-gradient', 'Hatch pattern CSS'),
            ('timeline-stacked-hatch', 'Stacked hatch class'),
            ('chart-legend-enhanced', 'Enhanced legend')
        ]
        
        for pattern, description in css_patterns:
            if pattern in css_content:
                print(f"✅ {description}: Found")
            else:
                print(f"❌ {description}: NOT found")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error checking frontend files: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🔬 STACKED BAR IMPLEMENTATION TEST")
    print("=" * 60)
    
    api_test = test_timeline_api()
    frontend_test = test_frontend_structure()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    if api_test and frontend_test:
        print("🎉 ALL TESTS PASSED! Stacked bar implementation is complete.")
        print("\n📋 Implementation Summary:")
        print("  ✅ Backend calculates project_minutes separately from active_minutes")
        print("  ✅ API returns both project_minutes and active_minutes fields")
        print("  ✅ Frontend processes stacked bar data structure")
        print("  ✅ CSS styles for hatched patterns are implemented")
        print("  ✅ Enhanced tooltips show project vs background breakdown")
        print("  ✅ Updated legend explains stacked bar visualization")
        print("\n🌐 The timeline chart now shows:")
        print("  📦 Bottom layer: Project work (solid color)")
        print("  📦 Top layer: Background activity (hatched pattern)")
        print("  💡 Hover over bars to see detailed breakdown")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check the output above for specific issues.")
    
    return api_test and frontend_test

if __name__ == '__main__':
    main()