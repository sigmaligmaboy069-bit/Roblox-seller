import requests
import json
import time
import os
import hashlib
import uuid
import platform
import sys
from datetime import datetime

# Pre-generated license keys (30 keys)
VALID_LICENSES = [
    "RBX-A1B2C3D4E5F6G7H8",
    "RBX-I9J0K1L2M3N4O5P6",
    "RBX-Q7R8S9T0U1V2W3X4",
    "RBX-Y5Z6A7B8C9D0E1F2",
    "RBX-G3H4I5J6K7L8M9N0",
    "RBX-O1P2Q3R4S5T6U7V8",
    "RBX-W9X0Y1Z2A3B4C5D6",
    "RBX-E7F8G9H0I1J2K3L4",
    "RBX-M5N6O7P8Q9R0S1T2",
    "RBX-U3V4W5X6Y7Z8A9B0",
    "RBX-C1D2E3F4G5H6I7J8",
    "RBX-K9L0M1N2O3P4Q5R6",
    "RBX-S7T8U9V0W1X2Y3Z4",
    "RBX-A5B6C7D8E9F0G1H2",
    "RBX-I3J4K5L6M7N8O9P0",
    "RBX-Q1R2S3T4U5V6W7X8",
    "RBX-Y9Z0A1B2C3D4E5F6",
    "RBX-G7H8I9J0K1L2M3N4",
    "RBX-O5P6Q7R8S9T0U1V2",
    "RBX-W3X4Y5Z6A7B8C9D0",
    "RBX-E1F2G3H4I5J6K7L8",
    "RBX-M9N0O1P2Q3R4S5T6",
    "RBX-U7V8W9X0Y1Z2A3B4",
    "RBX-C5D6E7F8G9H0I1J2",
    "RBX-K3L4M5N6O7P8Q9R0",
    "RBX-S1T2U3V4W5X6Y7Z8",
    "RBX-A9B0C1D2E3F4G5H6",
    "RBX-I7J8K9L0M1N2O3P4",
    "RBX-Q5R6S7T8U9V0W1X2",
    "RBX-Y3Z4A5B6C7D8E9F0"
]

LICENSE_DB_FILE = "license_database.json"

class LicenseManager:
    def __init__(self):
        self.license_file = "license.key"
        self.hwid_file = ".hwid"
        self.db = self.load_database()
        
    def load_database(self):
        """Load the license database (tracks which licenses are used)"""
        if os.path.exists(LICENSE_DB_FILE):
            with open(LICENSE_DB_FILE, 'r') as f:
                return json.load(f)
        # Initialize with all licenses as unused
        return {key: None for key in VALID_LICENSES}
    
    def save_database(self):
        """Save the license database"""
        with open(LICENSE_DB_FILE, 'w') as f:
            json.dump(self.db, f, indent=4)
    
    def get_hwid(self):
        """Get hardware ID (works on Windows and Mac)"""
        if platform.system() == "Windows":
            import subprocess
            try:
                output = subprocess.check_output("wmic csproduct get uuid", shell=True)
                hwid = str(output.decode().split('\n')[1].strip())
            except:
                hwid = str(uuid.getnode())
        else:
            hwid = str(uuid.getnode())
        return hashlib.sha256(hwid.encode()).hexdigest()
    
    def verify_license(self, license_key, hwid):
        """Verify and potentially bind a license"""
        # Check if license exists in valid licenses
        if license_key not in VALID_LICENSES:
            return False, "Invalid license key"
        
        # Load current database state
        self.db = self.load_database()
        
        # Check if license is already bound
        bound_hwid = self.db.get(license_key)
        
        if bound_hwid is None:
            # License not yet used - bind it to this HWID
            self.db[license_key] = hwid
            self.save_database()
            return True, "License activated successfully"
        
        if bound_hwid == hwid:
            # License already bound to this computer
            return True, "License verified"
        
        # License bound to different computer
        return False, "License already used on another machine"
    
    def activate(self):
        """Activate the software"""
        print("\n" + "=" * 60)
        print("   LICENSE ACTIVATION")
        print("=" * 60)
        
        hwid = self.get_hwid()
        print(f"\n🔑 Hardware ID: {hwid[:16]}...")
        print(f"🖥️  System: {platform.system()}")
        
        if os.path.exists(self.license_file):
            with open(self.license_file, 'r') as f:
                data = json.load(f)
                license_key = data.get("key", "")
                stored_hwid = data.get("hwid", "")
            
            if stored_hwid != hwid:
                print("\n⚠ WARNING: Hardware change detected!")
                print("Your license is tied to a different machine.")
                input("\nPress Enter to exit...")
                return False
            
            valid, msg = self.verify_license(license_key, hwid)
            if valid:
                print("✓ License verified successfully!")
                return True
            else:
                print(f"✗ License verification failed: {msg}")
                input("\nPress Enter to exit...")
                return False
        
        print("\n📝 Enter your license key:")
        license_key = input("License Key: ").strip()
        
        valid, msg = self.verify_license(license_key, hwid)
        
        if valid:
            with open(self.license_file, 'w') as f:
                json.dump({
                    "key": license_key,
                    "hwid": hwid,
                    "activated": datetime.now().isoformat(),
                    "system": platform.system()
                }, f, indent=4)
            
            print(f"\n✓ {msg}")
            print("=" * 60)
            return True
        else:
            print(f"\n✗ Activation failed: {msg}")
            input("\nPress Enter to exit...")
            return False

class RobloxLimitedSeller:
    def __init__(self):
        self.session = requests.Session()
        self.user_id = None
        self.csrf_token = None
        self.config = self.load_config()
        self.account_file = "account.json"
        
    def load_cookie(self):
        if not os.path.exists(self.account_file):
            return None
        with open(self.account_file, 'r') as f:
            data = json.load(f)
        return data.get("cookie", "")
    
    def save_cookie(self, cookie):
        data = {"cookie": cookie}
        with open(self.account_file, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"✓ Cookie saved to {self.account_file}")
    
    def load_config(self):
        default_config = {
            "pricing_strategy": "cheapest",
            "price_multiplier": 1.05,
            "blacklist": [],
            "item_type": "all"
        }
        
        if os.path.exists("config.json"):
            with open("config.json", 'r') as f:
                return {**default_config, **json.load(f)}
        return default_config
    
    def save_config(self):
        with open("config.json", 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def login(self, cookie):
        self.session.cookies.set(".ROBLOSECURITY", cookie, domain=".roblox.com")
        
        response = self.session.post("https://auth.roblox.com/v2/logout")
        if "x-csrf-token" in response.headers:
            self.csrf_token = response.headers["x-csrf-token"]
            self.session.headers.update({"x-csrf-token": self.csrf_token})
        
        user_response = self.session.get("https://users.roblox.com/v1/users/authenticated")
        if user_response.status_code == 200:
            user_data = user_response.json()
            self.user_id = user_data["id"]
            print(f"✓ Logged in as: {user_data['name']} (ID: {self.user_id})")
            return True
        else:
            print("✗ Authentication failed. Invalid cookie.")
            return False
    
    def get_user_limiteds(self):
        print("\n🔍 Fetching your limited items...")
        limiteds = []
        cursor = ""
        
        while True:
            url = f"https://inventory.roblox.com/v2/users/{self.user_id}/inventory/13"
            params = {"limit": 100, "sortOrder": "Asc"}
            if cursor:
                params["cursor"] = cursor
            
            response = self.session.get(url, params=params)
            if response.status_code != 200:
                break
            
            data = response.json()
            
            for item in data.get("data", []):
                asset_details = item.get("assetDetails", {})
                if asset_details:
                    is_limited = asset_details.get("isLimited", False)
                    is_limited_u = asset_details.get("isLimitedUnique", False)
                    
                    if is_limited or is_limited_u:
                        item_info = {
                            "id": item["assetId"],
                            "name": item["name"],
                            "type": "Roblox Limited" if is_limited else "UGC Limited",
                            "is_limited_u": is_limited_u
                        }
                        limiteds.append(item_info)
            
            cursor = data.get("nextPageCursor")
            if not cursor:
                break
        
        print(f"✓ Found {len(limiteds)} limited items")
        return limiteds
    
    def filter_limiteds(self, limiteds):
        filtered = []
        
        for item in limiteds:
            if item["id"] in self.config["blacklist"]:
                continue
            
            item_type = self.config["item_type"]
            if item_type == "ugc" and item["type"] != "UGC Limited":
                continue
            elif item_type == "roblox" and item["type"] != "Roblox Limited":
                continue
            
            filtered.append(item)
        
        return filtered
    
    def get_lowest_price(self, asset_id):
        url = f"https://economy.roblox.com/v2/assets/{asset_id}/resellers"
        params = {"limit": 10}
        
        response = self.session.get(url, params=params)
        if response.status_code != 200:
            return None
        
        data = response.json()
        resellers = data.get("data", [])
        
        if not resellers:
            return None
        
        return resellers[0]["price"]
    
    def calculate_price(self, lowest_price):
        if self.config["pricing_strategy"] == "cheapest":
            return lowest_price
        elif self.config["pricing_strategy"] == "above":
            return int(lowest_price * self.config["price_multiplier"])
        return lowest_price
    
    def list_item(self, asset_id, price):
        url = f"https://economy.roblox.com/v1/assets/{asset_id}/resellable-copies"
        
        response = self.session.get(url)
        if response.status_code != 200:
            return False, "Failed to get user asset"
        
        copies = response.json().get("data", [])
        if not copies:
            return False, "No resellable copies found"
        
        user_asset_id = copies[0]["userAssetId"]
        
        list_url = f"https://economy.roblox.com/v1/assets/{asset_id}/resellable-copies/{user_asset_id}"
        payload = {"price": price}
        
        response = self.session.patch(list_url, json=payload)
        
        if response.status_code == 200:
            return True, "Listed successfully"
        else:
            return False, f"Error: {response.status_code}"
    
    def sell_all_limiteds(self):
        limiteds = self.get_user_limiteds()
        filtered = self.filter_limiteds(limiteds)
        
        print(f"\n📊 Items to list: {len(filtered)}")
        print("=" * 60)
        
        listed_count = 0
        
        for item in filtered:
            print(f"\n📦 {item['name']} ({item['type']})")
            print(f"   ID: {item['id']}")
            
            lowest = self.get_lowest_price(item["id"])
            if not lowest:
                print("   ⚠ No market data available - skipping")
                continue
            
            sell_price = self.calculate_price(lowest)
            print(f"   💰 Lowest Price: {lowest:,} R$")
            print(f"   💵 Listing Price: {sell_price:,} R$")
            
            success, msg = self.list_item(item["id"], sell_price)
            if success:
                print(f"   ✓ {msg}")
                listed_count += 1
            else:
                print(f"   ✗ {msg}")
            
            time.sleep(1)
        
        print("\n" + "=" * 60)
        print(f"✓ Successfully listed {listed_count}/{len(filtered)} items")

def main():
    try:
        license_mgr = LicenseManager()
        if not license_mgr.activate():
            print("\n❌ Software not licensed. Exiting...")
            time.sleep(3)
            return
        
        print("\n" + "=" * 60)
        print("   ROBLOX LIMITED AUTO-SELLER")
        print("=" * 60)
        
        seller = RobloxLimitedSeller()
        
        cookie = seller.load_cookie()
        
        if not cookie:
            print("\n⚙ First time setup")
            cookie_input = input("Enter your .ROBLOSECURITY cookie: ").strip()
            seller.save_cookie(cookie_input)
            cookie = cookie_input
        
        print("\n🔐 Authenticating...")
        if not seller.login(cookie):
            input("\nPress Enter to exit...")
            return
        
        print("\n⚙ Configuration")
        print(f"1. Pricing Strategy: {seller.config['pricing_strategy']}")
        print(f"2. Price Multiplier: {seller.config['price_multiplier']}")
        print(f"3. Item Type: {seller.config['item_type']}")
        print(f"4. Blacklisted Items: {len(seller.config['blacklist'])}")
        
        configure = input("\nConfigure settings? (y/n): ").lower()
        
        if configure == 'y':
            print("\nPricing Strategy:")
            print("1. Cheapest (match lowest price)")
            print("2. Above (price above lowest)")
            choice = input("Select (1/2): ")
            
            if choice == "2":
                seller.config["pricing_strategy"] = "above"
                multiplier = input("Enter multiplier (e.g., 1.05 for 5% above): ")
                seller.config["price_multiplier"] = float(multiplier)
            else:
                seller.config["pricing_strategy"] = "cheapest"
            
            print("\nItem Type Filter:")
            print("1. All limiteds")
            print("2. UGC limiteds only")
            print("3. Roblox limiteds only")
            choice = input("Select (1/2/3): ")
            
            if choice == "2":
                seller.config["item_type"] = "ugc"
            elif choice == "3":
                seller.config["item_type"] = "roblox"
            else:
                seller.config["item_type"] = "all"
            
            blacklist_input = input("\nEnter asset IDs to blacklist (comma-separated, or press Enter to skip): ")
            if blacklist_input:
                seller.config["blacklist"] = [int(x.strip()) for x in blacklist_input.split(",")]
            
            seller.save_config()
            print("✓ Configuration saved")
        
        print("\n" + "=" * 60)
        confirm = input("Start listing limiteds? (y/n): ").lower()
        
        if confirm == 'y':
            seller.sell_all_limiteds()
        else:
            print("Cancelled.")
        
        input("\nPress Enter to exit...")
        
    except KeyboardInterrupt:
        print("\n\n✗ Operation cancelled by user")
        input("\nPress Enter to exit...")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
