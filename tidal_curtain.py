import asyncio
import requests
from datetime import datetime, timezone
from bleak import BleakClient

# ==========================================
# 🌊 Tidal Curtain Settings (Woolloomooloo Bay)
# ==========================================
LEFT_CURTAIN = "YOUR_LEFT_MAC_HERE"   # e.g., "DF:9E:2B:BD:3B:7B"
RIGHT_CURTAIN = "YOUR_RIGHT_MAC_HERE" # e.g., "DE:31:2E:85:FA:C2"
WRITE_UUID = "cba20002-224d-11e6-9fb8-0002a5d5c51b"

# Coordinates for Woolloomooloo Bay
LAT = "-33.865"
LON = "151.222"

# 🎨 Artistic Canvas (Tidal Range Mapping)
MIN_HEIGHT = 0.0  # Low tide baseline (meters)
MAX_HEIGHT = 2.0  # High tide baseline (meters)
# ==========================================

def get_water_level():
    url = f"https://marine-api.open-meteo.com/v1/marine?latitude={LAT}&longitude={LON}&hourly=swell_wave_height"
    try:
        response = requests.get(url).json()
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:00")
        times = response['hourly']['time']
        heights = response['hourly']['swell_wave_height']
        
        if current_time in times:
            idx = times.index(current_time)
            return heights[idx]
    except Exception as e:
        print(f"API Error: {e}")
    return None

async def send_command(address, position, name):
    print(f"👉 Moving {name} curtain to {position}%...")
    for attempt in range(3):
        try:
            async with BleakClient(address, timeout=15.0) as client:
                command = bytearray([0x57, 0x0F, 0x45, 0x01, 0x05, 0xFF, position])
                await client.write_gatt_char(WRITE_UUID, command)
                print(f"✅ {name} curtain success!")
                return
        except Exception as e:
            print(f"⚠️ {name} retrying ({attempt+1}/3)...")
            await asyncio.sleep(2)
    print(f"❌ {name} control failed.")

async def move_both_curtains(position):
    await send_command(LEFT_CURTAIN, position, "Left")
    await asyncio.sleep(0.5)
    await send_command(RIGHT_CURTAIN, position, "Right")
    print("\n🌊 Both curtains synchronized!\n")

async def main():
    print("====================================")
    print(" 🌊 Tidal Curtain Automation 🌊 ")
    print("====================================\n")
    
    while True:
        height = get_water_level()
        
        if height is not None:
            print(f"Current water level: {height} m")
            
            percent = int(((height - MIN_HEIGHT) / (MAX_HEIGHT - MIN_HEIGHT)) * 100)
            percent = max(0, min(100, percent))
            
            # Artistic Choice: Inverse Mapping (Close on high tide)
            percent = 100 - percent 
            
            await move_both_curtains(percent)
        
        # Wait 30 minutes before next update
        await asyncio.sleep(1800)

if __name__ == "__main__":
    asyncio.run(main())
