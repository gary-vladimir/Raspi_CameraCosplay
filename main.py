import subprocess, sys
import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def _quiet(cmd):
    return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode

def wake_camera(retries = 3, pause = 1.0):
    for _ in range(retries):
        if _quiet(["gphoto2", "--summary"]) == 0:
            return True
        _quiet(["gphoto2", "--reset"])
        sleep(pause)
        
    if _quiet(["gphoto2", "--get-config", "eosremoterelease"]) == 0:
        _quiet(["gphoto2", "--set-config", "eosremoterelease=1"])
        sleep(0.3)
        _quiet(["gphoto2", "--set-config", "eosremoterelease=4"])
        return _quiet(["gphoto2", "--summary"]) == 0
    return False

def take_photo(filename):
    if not wake_camera():
        print("camera is turned off or not connected")
        sys.exit(1)
    print("Fotooo! :D")
    subprocess.run(["gphoto2", "--set-config", "capturetarget=1"], check=True)
    subprocess.run([
        "gphoto2",
        "--capture-image-and-download",
        "--filename", filename,
        "--force-overwrite"
    ], check=True)
    
if __name__ == "__main__":
    subprocess.run(["pkill", "-f", "gvfs-gphoto2-volume-monitor"], stderr=subprocess.DEVNULL)
    subprocess.run(["pkill", "-f", "gvfsd-gphoto2"], stderr=subprocess.DEVNULL)
    while True:
        if GPIO.input(4) == GPIO.LOW:
            take_photo("5K_RobotGenio.jpg")
            sleep(1)
        sleep(0.1)