# tidal-curtain

This project translates real-time ocean tide data (sea level) from Woolloomooloo Bay into the physical movement of curtains in a studio space, using a Raspberry Pi Zero 2 W and SwitchBot Curtains.

The installation utilises live marine data from the Stormglass Global Tide API, where the ocean's true tide level inversely dictates the opening percentage of the curtain. 

The system employs **Dynamic Scaling**: every 24 hours, it fetches the ocean's specific high and low extremes for that day. As the water level recedes (Ebb) toward the daily minimum, the curtain draws closed to fill the void; as it rises (Flow) toward the daily peak, the curtain opens, allowing the physical space to breathe with the ocean's actual daily limits.

## Materials

- **Hardware:** Raspberry Pi Zero 2 W, SwitchBot Curtain 3 (Left & Right)
- **Data Source:** Stormglass Global Tide API (Free Tier, 50 requests/day)

## How to use

1. Install requirements:
  ```bash
   sudo apt update
   sudo apt install python3-pip -y
   pip3 install requests bleak pytz --break-system-packages
```
2. Update Settings in tidal_curtain.py:Update LEFT_CURTAIN and RIGHT_CURTAIN with your SwitchBot MAC addresses. Insert your free STORMGLASS_API_KEY into the script.
3. Deploy for 24/7 automation:  Copy tidal_curtain.service to /etc/systemd/system/ and run the following commands:
  ```bash
sudo systemctl daemon-reload
sudo systemctl enable tidal_curtain.service
sudo systemctl start tidal_curtain.service

