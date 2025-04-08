import subprocess
import time
from tg import telegram_sender

def restart_warp():
    try:
        """Restart the WARP VPN connection"""
        #print("Disconnecting WARP...")
        subprocess.run(["warp-cli", "disconnect"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        telegram_sender(message="restarting warp")
        #print("Connecting WARP...")
        subprocess.run(["warp-cli", "connect"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)   

        result = subprocess.run(["warp-cli", "status"], capture_output=True, text=True)
        output = result.stdout.strip()
        
        # Wait until Warp is connected
        while output != "Status update: Connected":
            result = subprocess.run(["warp-cli", "status"], capture_output=True, text=True)
            output = result.stdout.strip()
            time.sleep(1)
            telegram_sender("not yet")
            #print('not yet')

        #print("WARP restarted successfully.")
        telegram_sender("warp restarted")
        return 
    except Exception:
        return