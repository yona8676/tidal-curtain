# tidal-curtain

This project translates real-time ocean tide data (swell wave height) from Woolloomooloo Bay into the physical movement of curtains in a studio space, using a Raspberry Pi Zero 2 W and SwitchBot Curtains.

The system embraces **Dynamic Scaling**, calculating the ocean's actual daily high and low extremes to determine the 0% (fully open) and 100% (fully closed) positions of the curtains, allowing the physical space to breathe with the ocean's true daily limits.

## Materials

- **Hardware:** Raspberry Pi Zero 2 W, SwitchBot Curtain 3 (Left & Right)
- **Data Source:** Open-Meteo Marine API (Free, no token required)

## How to use

**1. Install requirements:**
```bash
sudo apt install python3-pip -y
pip3 install requests bleak pytz --break-system-packages
Find your SwitchBot Curtain MAC addresses via the SwitchBot App and update LEFT_CURTAIN and RIGHT_CURTAIN in tidal_curtain.py.
Deploy the tidal_curtain.service file to /etc/systemd/system/ for 24/7 automation.
