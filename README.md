# tidal-curtain

This project translates real-time ocean tide data (swell wave height) from Woolloomooloo Bay into the physical movement of curtains in a studio space, using a Raspberry Pi Zero 2 W and SwitchBot Curtains.

## Materials

**Hardware:** Raspberry Pi Zero 2 W, SwitchBot Curtain 3 (Left & Right)  
**Data Source:** Open-Meteo Marine API (Free, no token required)

## How to use

1. **Install requirements:**  
   `sudo apt install python3-pip -y`  
   `pip3 install requests bleak --break-system-packages`

2. **Update MAC Addresses:**  
   Find your SwitchBot Curtain MAC addresses via the SwitchBot App and update `LEFT_CURTAIN` and `RIGHT_CURTAIN` in `tidal_curtain.py`.

3. **Deploy automation:**  
   Deploy the `tidal_curtain.service` file to `/etc/systemd/system/` for 24/7 automation.
