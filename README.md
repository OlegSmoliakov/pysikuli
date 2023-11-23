# pysikui
fast cross-platform python module for gui automation

for windows link use raw string r"C:\data\date"

For playsound:

+ Ubuntu/Debian: sudo apt install libgirepository1.0-dev libcairo2-dev
macOS/Homebrew: brew install cairo pkg-config
Arch Linux: sudo pacman -S cairo pkgconf
Fedora: sudo dnf install cairo-devel pkg-config python3-devel
penSUSE: sudo zypper install cairo-devel pkg-config python3-devel


For linux:
pygobject (for playsound) doesn't work with pyperclip
+ (evdev): sudo apt-get install python3-dev or python3.x, where x is version of your python