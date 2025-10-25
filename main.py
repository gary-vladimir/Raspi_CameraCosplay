import subprocess, sys, os
from gpiozero import Button, Servo
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory

factory = PiGPIOFactory()
button = Button(4, pull_up=True, bounce_time=0.3)
s1 = Servo(17, pin_factory=factory)

def set_servo_angle(angle):
    # Map angle (0 to 180) to servo value (-1 to 1)
    servo_value = (angle / 90.0) - 1.0
    s1.value = servo_value

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
    print("Fotooo! :D")
    subprocess.run(["gphoto2", "--set-config", "capturetarget=1"], check=True)
    subprocess.run([
        "gphoto2",
        "--capture-image-and-download",
        "--filename", filename,
        "--force-overwrite"
    ], check=True)

if __name__ == "__main__":
    set_servo_angle(90)

    subprocess.run(["pkill", "-f", "gvfs-gphoto2-volume-monitor"], stderr=subprocess.DEVNULL)
    subprocess.run(["pkill", "-f", "gvfsd-gphoto2"], stderr=subprocess.DEVNULL)

    if not wake_camera():
        print("camera is turned off or not connected")
        sys.exit(1)

    viewer = None
    try:
        while True:
            if button.is_pressed:
                try:
                    set_servo_angle(45)
                    take_photo("5K_RobotGenio.jpg")
                    set_servo_angle(90)
                    # Start viewer after first photo if not already running
                    if viewer is None:
                        print("Starting image viewer...")
                        env = os.environ.copy()
                        env["DISPLAY"] = ":0"
                        viewer = subprocess.Popen([
                            "feh",
                            "--fullscreen",
                            "--auto-zoom",
                            "--reload", "1",
                            "5K_RobotGenio.jpg"
                        ], env=env)
                        print(f"Viewer started with PID: {viewer.pid}")
                except Exception as e:
                    print(f"Error taking photo: {e}")
                button.wait_for_release()
            sleep(0.1)
    finally:
        if viewer:
            viewer.terminate()
        button.close()
