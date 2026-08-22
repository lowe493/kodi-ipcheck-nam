import urllib.request
import json
import time

TOKEN = "87e00bca0b8e3f"

try:
    import xbmc
    import xbmcgui
    KODI_AVAILABLE = True
except ImportError:
    xbmc = None
    xbmcgui = None
    KODI_AVAILABLE = False


# =========================
# FETCH IP INFO
# =========================
def fetch_ip_info():
    url = f"https://ipinfo.io/json?token={TOKEN}"
    with urllib.request.urlopen(url, timeout=5) as response:
        data = json.load(response)

    ip = data.get("ip", "Unknown IP")
    org = data.get("org", "Unknown ISP")

    if org.startswith("AS"):
        org = org.split(" ", 1)[-1]

    return org, ip


# =========================
# OUTPUT
# =========================
def show_notification(title, message, warning=False):
    if KODI_AVAILABLE:
        icon = xbmcgui.NOTIFICATION_ERROR if warning else xbmcgui.NOTIFICATION_INFO
        duration = 30000 if warning else 8000
        xbmcgui.Dialog().notification(
            heading=title,
            message=message,
            icon=icon,
            time=duration
        )
    else:
        print(f"{title}: {message}")


# =========================
# VPN RULE
# =========================
def is_unprotected_isp(isp):
    return isp.strip().lower() == "british"


# =========================
# CHECK FUNCTION
# =========================
def check_vpn_status(first_run=False):
    isp, ip = fetch_ip_info()
    message = f"{isp}: {ip}"
    title = "VPN NOT CONNECTED"
    detail = f"BT Detected - {message}"

    if is_unprotected_isp(isp):
        show_notification(
            title,
            detail,
            warning=True
        )
        xbmcgui.Dialog().ok(title, f"{detail}\nCheck that the VPN is connected IMMEDIATLY!")
        return False

    # VPN CONNECTED (startup only)
    if first_run:
        title = "VPN CONNECTED"
        detail = f"Protected - {message}"

        show_notification(
            title,
            detail,
            warning=False
        )

    return True


# =========================
# MAIN LOOP (KODI SAFE)
# =========================
def main():
    monitor = xbmc.Monitor() if KODI_AVAILABLE else None

    # Run once immediately
    check_vpn_status(first_run=True)

    # Then repeat every 10 minutes
    interval = 600  # 10 minutes in seconds

    while True:
        # Stop cleanly if Kodi exits
        if monitor and monitor.abortRequested():
            break

        # Wait in small chunks so Kodi can interrupt cleanly
        for _ in range(interval):
            if monitor and monitor.abortRequested():
                return
            time.sleep(1)

        # Only notify if VPN is NOT active
        check_vpn_status()


if __name__ == "__main__":
    main()