import subprocess
import time


def restart_warp():
    try:
        """Restart the WARP VPN connection"""
        #print("Disconnecting WARP...")
        subprocess.run(["warp-cli", "disconnect"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
     
        #print("Connecting WARP...")
        subprocess.run(["warp-cli", "connect"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)   

        result = subprocess.run(["warp-cli", "status"], capture_output=True, text=True)
        output = result.stdout.strip()
        
        # Wait until Warp is connected
        while output != "Status update: Connected":
            result = subprocess.run(["warp-cli", "status"], capture_output=True, text=True)
            output = result.stdout.strip()
            time.sleep(1)
           
            #print('not yet')

        #print("WARP restarted successfully.")
      
        return 
    except Exception:
        return