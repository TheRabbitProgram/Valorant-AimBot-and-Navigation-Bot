# Valorant-Aim-and-Navigation-Bot

**FOR EDUCATIONAL PURPOSES ONLY**

**For educational purposes in image processing, serial communication, and other**

**Obvious errors and slowdowns have been purposefully introduced therefore solving the errors may be a learning experience.**

Please use within reason: practice range, user hosted testing enviorments.  I am not responsible for your ban.  Also valorant has not patched this method since the Beta till the date of the projects inital posting **(I haven't played val after posting this, there I cannot verify if it still works)**.  This method can be mitigated through intelligent enviorment coloring, character and ability coloring (character outlines), or through VANGUARD.  This is a low maintenance cheat, if you really wanted a reliable cheat, why would you even use this method look elsewhere.

![Gif](ReadMeFiles/Valorant.gif)

## How it works?

* Aimbot
  * This is a color based aimbot made in python that works in fullscreen mode optimized for the Phantom and Vandal.  It has multiple color filterings that will automatically adjust itself when a target is detected.  Target detection occurs when the right color is seen by the first filter on a large fov detection range.  The second filter applies once the conditions for the first is met resulting in detection range reduction and color filtering becomes more lenient.  Because the head of enemy characters are usually the highest point, we scan from top left to bottom right and the first instance of purple pixel found, filtering switches to a more accurate mode and smaller fov resulting in quicker detection on the second pass when looping through the pixel array.  The size of the fov is determined if `Shift` is held down or not, auto recoil compenstation is implemented.  The vertical size of the target detemines the perceived distance, the close the target is, the quicker the gun will fire.  The futher the target is, the keyboard will attempt to counter strafe to stop the character movement before firing the weapon.  Aim offset from first pixel is also determined by the distance of the target as to attempt to get headshots on pony tail characters.
  * Mouse movements will be locked when firing.  Mouse commands are sent via lan, therefore firewalls must have their ports exposed.  Once the mouse movement command is sent from PC 1 to PC 2, PC 2 forwards it to the ardunio via serial.

* Navigation
  * Incomplete, generates a map data based off of where red dots are placed to help guide the bot.
  ![Pic](ReadMeFiles/map%20demo.png?raw=true "Demo")

## Limitations

This demonstration requires 2 seperate computers and 2 seperate arduino units.  Computing speed depends on PC, but is relatively and optimized for speed.  Works only with 1080p screen size on Valorant PC.  Scales poorly with resolution size.  Harder to hit moving targets.  Developers of valorant could opt to create similar colored surroundings or make abilites of similar color to make this method obsolete.

## Setup

Python PIP Installs
```
pip3 install -r requirements.txt
```

The follow found in **mouseHost.py** should be scaled to your monitor's resolution.  (Not PC running Valorant's resolution)
```python
mon_width = 3840
mon_height = 2160
```

**valkset.json**
```json
{"host-ip": "IP of Mouse Host", "host-port": "6767", 
"client-ip": "IP of PC Running Valorant", "client-port": "6767"}
```

Flash the respective arduino files per arduino, afterwards COM ports may need to altered accordingly.
* Arduino Library needed https://github.com/NicoHood/HID

valkyrie.py
```python
serMouse = serial.Serial('COM3', baudrate=2000000, writeTimeout=0)
serKeyboard = serial.Serial('COM4', baudrate=2000000, writeTimeout=0)
```

How files and arduinos should be arranged
```
PC 1
├── mouseHost.py
└── valkset.json
```

```
PC 2 (Running Valorant)
├── valkyrie.py
├── valkset.json
├── Arduino For Mouse Emulation
└── Arduino For Keyboard Emulation
```

Use PC 1's mouse and PC 2's keyboard

Valorant settings should be as follows
* Set Game to 0.5 sense
* Set Game to 0.84 or 0.85 zoom sense, 0.9 to tracking moving targets (Weapon Dependent)
* Set Game to 1920 x 1080
* Set Game to Show Purple
* Set Game to Hide Corpses
* Set Game to Transparent Cursor
* Set Game FPS to MAX
* Set Walk to P (secondary)
* Set Zoom to O (secondary)
* Set Move Up to Up Arrow
* Set Move Down to Down Arrow
* Set Move Left to Left Arrow
* Set Move Right to Right Arrow
* (Optional) Set AA to MSAA 4x for long range precision

## Usage (Startup)

Verified to work with Windows.

Run on machine running Valorant
```
./valkyrie.py
```


Run on machine hosting mouse inputs
```
./hostHouse.py
```

## Usage (Mouse Host PC)

* Press ``` - ``` Key to exit
* Press ``` ` ``` Key to pause mouse lock/ grabber
* Press ``` ESC ``` Key to unpause

## Usage (Valorant PC)

* Modes
  * Press ``` ` ``` Key to pause and go into mode selector
  * Press ``` ESC ``` Key to engage Mode 1: Automatic Auto Aim
  * Press ``` F1 ``` Key to engage Mode 2: Auto Aim when shoot button is triggered, slowly moves camera towards target
  * Press ``` F2 ``` Key to engage Mode 3: Auto Aim when shoot button is triggered, snaps to target and snaps back immediately, resulting effect should be (mostly) unoticable.
* Other
  * Hold ``` [ ``` or ``` ] ``` Key to temporily pause detection and auto aim when in Mode 1
  * Hold ``` Middle Mouse Button ``` Key When in Mode 1 to Engage Spin bot, spin bot slightly varies when moving vs not moving
  * Hold ``` Shift ``` Key Single Shot
  * Release ``` Shift ``` Key Spray and Pray
  * Press ``` = ``` Key to terminate program
* Settings
  * Look in terminal for guidence
  
## Thanks

Thanks to all those who made this possible with simple to use python packages.  If I missed any license or credits, please let me know and I'll add them here.
