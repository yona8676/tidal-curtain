import asyncio
import requests
from datetime import datetime
import pytz
from bleak import BleakClient

# ==========================================
# 🌊 Tidal Curtain Settings
# ==========================================
LEFT_CURTAIN  = "XX:XX:XX:XX:XX:XX"   # Replace with your LEFT SwitchBot MAC address
RIGHT_CURTAIN = "XX:XX:XX:XX:XX:XX"   # Replace with your RIGHT SwitchBot MAC address
WRITE_UUID    = "cba20002-224d-11e6-9fb8-0002a5d5c51b"

STORMGLASS_API_KEY = "YOUR_STORMGLASS_API_KEY"  # https://stormglass.io

# Woolloomooloo Bay, Sydney
LAT = "-33.865"
LON = "151.222"
# ==========================================


def get_live_tide_data():
    """
    Fetch today's real-time sea level data from the Stormglass Global Tide API.
    Returns (current_height, daily_min, daily_max) in metres.
    Falls back to (None, None, None) on any error.
    """
    sydney_tz   = pytz.timezone("Australia/Sydney")
    now_sydney  = datetime.now(sydney_tz)

    start_utc = (
        now_sydney
        .replace(hour=0, minute=0, second=0, microsecond=0)
        .astimezone(pytz.utc)
        .strftime("%Y-%m-%dT%H:%M:%S+00:00")
    )
    end_utc = (
        now_sydney
        .replace(hour=23, minute=59, second=59, microsecond=0)
        .astimezone(pytz.utc)
        .strftime("%Y-%m-%dT%H:%M:%S+00:00")
    )

    url     = "https://api.stormglass.io/v2/tide/sea-level/point"
    params  = {"lat": LAT, "lng": LON, "start": start_utc, "end": end_utc}
    headers = {"Authorization": STORMGLASS_API_KEY}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()["data"]

            # Dynamic Scaling: today's actual tidal range
            heights   = [item["sg"] for item in data]
            daily_min = min(heights)
            daily_max = max(heights)

            # Find the closest data point to right now
            now_utc      = datetime.now(pytz.utc)
            closest      = min(
                data,
                key=lambda x: abs(
                    datetime.fromisoformat(x["time"].replace("+00:00", "+0000"))
                    - now_utc
                )
            )
            current_height = closest["sg"]

            return current_height, daily_min, daily_max

        else:
            print(f"API Error {response.status_code}: {response.text}")

    except Exception as e:
        print(f"Network/API Error: {e}")

    return None, None, None


async def send_command(address, position, name):
    """Send a position command to a single SwitchBot Curtain via BLE (3 retries)."""
    print(f"👉 Moving {name} curtain → {position}% closed...")
    for attempt in range(3):
        try:
            async with BleakClient(address, timeout=15.0) as client:
                command = bytearray([0x57, 0x0F, 0x45, 0x01, 0x05, 0xFF, position])
                await client.write_gatt_char(WRITE_UUID, command)
                print(f"✅ {name} curtain OK")
                return
        except Exception as e:
            print(f"⚠️  {name} attempt {attempt + 1}/3 failed: {e}")
            await asyncio.sleep(2)
    print(f"❌ {name} curtain unreachable — skipping this cycle.")


async def move_both_curtains(position):
    """Send the same position to both curtains sequentially."""
    await send_command(LEFT_CURTAIN,  position, "Left")
    await asyncio.sleep(0.5)
    await send_command(RIGHT_CURTAIN, position, "Right")
    print("\n🌊 Both curtains synchronised.\n")


async def main():
    print("=" * 42)
    print("  🌊  Tidal Curtain  ·  Stormglass Live  🌊")
    print("=" * 42 + "\n")

    while True:
        current_height, daily_min, daily_max = get_live_tide_data()

        if current_height is not None:
            sydney_tz = pytz.timezone("Australia/Sydney")
            now_str   = datetime.now(sydney_tz).strftime("%H:%M:%S  %d %b %Y  (AEDT)")

            print(f"[{now_str}]")
            print(f"🌊 Today's tidal range : {daily_min:.3f} m  →  {daily_max:.3f} m")
            print(f"💧 Current sea level   : {current_height:.3f} m")

            if daily_max == daily_min:
                percent = 50
            else:
                percent = int(
                    ((current_height - daily_min) / (daily_max - daily_min)) * 100
                )

            percent = max(0, min(100, percent))

            # Artistic inversion:
            # High Tide  →  curtain fully open   (0% closed)
            # Low Tide   →  curtain fully closed  (100% closed)
            final_percent = 100 - percent
            print(f"🎭 Curtain position    : {final_percent}% closed")

            await move_both_curtains(final_percent)

        else:
            print("⚠️  Could not retrieve live tide data — retrying in 30 minutes.")

        # 30-minute interval → 48 calls/day (within Stormglass free tier: 50 calls/day)
        await asyncio.sleep(1800)


if __name__ == "__main__":
    asyncio.run(main())

