#!/usr/bin/env python3
"""
快速测试API端点
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

import requests
import time

def test_api_endpoints():
    """测试API端点"""
    base_url = "http://localhost:8080"
    
    endpoints = [
        "/api/status",
        "/api/initial_data",
        "/api/simulation_data"
    ]
    
    print("🧪 Testing API endpoints...")
    
    for endpoint in endpoints:
        url = base_url + endpoint
        try:
            print(f"\n📡 Testing {url}")
            response = requests.get(url, timeout=5)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ Success")
                if endpoint == "/api/status":
                    data = response.json()
                    print(f"   Data: {data}")
            else:
                print(f"   ❌ Failed: {response.text}")
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Connection failed - server may not be running")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n🌐 You can also test manually:")
    print("   http://localhost:8080")
    print("   http://localhost:8080/api/status")

if __name__ == "__main__":
    test_api_endpoints() 