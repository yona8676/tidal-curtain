import asyncio
import requests
from datetime import datetime
import pytz
from bleak import BleakClient

# ==========================================
# 🌊 Tidal Curtain Settings (Sydney Local Time)
# ==========================================
LEFT_CURTAIN = "YOUR_LEFT_MAC_HERE"   # e.g., "DF:9E:2B:BD:3B:7B"
RIGHT_CURTAIN = "YOUR_RIGHT_MAC_HERE" # e.g., "DE:31:2E:85:FA:C2"
WRITE_UUID = "cba20002-224d-11e6-9fb8-0002a5d5c51b"

LAT = "-33.865"
LON = "151.222"
# ==========================================

def get_water_level_and_daily_range():
    url = f"https://marine-api.open-meteo.com/v1/marine?latitude={LAT}&longitude={LON}&hourly=swell_wave_height&timezone=Australia%2FSydney&forecast_days=1"
    try:
        response = requests.get(url).json()
        sydney_tz = pytz.timezone('Australia/Sydney')
        current_time = datetime.now(sydney_tz).strftime("%Y-%m-%dT%H:00")
        
        times = response['hourly']['time']
        heights = response['hourly']['swell_wave_height']
        
        valid_heights = [h for h in heights if h is not None]
        daily_min = min(valid_heights)
        daily_max = max(valid_heights)
        
        if current_time in times:
            idx = times.index(current_time)
            current_height = heights[idx]
            return current_height, daily_min, daily_max

    except Exception as e:
        print(f"API Error: {e}")
    return None, None, None

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
    print(" 🌊 Dynamic Tidal Curtain (Sydney Time) 🌊 ")
    print("====================================\n")
    
    while True:
        current_height, daily_min, daily_max = get_water_level_and_daily_range()
        
        if current_height is not None:
            sydney_tz = pytz.timezone('Australia/Sydney')
            print(f"[{datetime.now(sydney_tz).strftime('%H:%M:%S')}]")
            print(f"🌊 Today's Ocean Limit: Min {daily_min}m ~ Max {daily_max}m")
            print(f"💧 Current Water Level: {current_height}m")
            
            if daily_max == daily_min:
                percent = 50 
            else:
                percent = int(((current_height - daily_min) / (daily_max - daily_min)) * 100)
                
            percent = max(0, min(100, percent))
            final_percent = 100 - percent 
            print(f"🎭 Artistic Translation: {final_percent}% Closed")
            
            await move_both_curtains(final_percent)
        
        await asyncio.sleep(1800)

if __name__ == "__main__":
    asyncio.run(main())

