# pysikui
Fast cross-platform python module for gui automation

For windows paths use raw string, for example: r"C:\data\date"

For macos:
+ playsound dependencies
+ + macOS/Homebrew: brew install cairo pkg-config


For linux:
+ playsound dependencies
+ + Ubuntu/Debian: sudo apt install libgirepository1.0-dev libcairo2-dev
+ + Arch Linux: sudo pacman -S cairo pkgconf
+ + Fedora: sudo dnf install cairo-devel pkg-config python3-devel
+ + penSUSE: sudo zypper install cairo-devel pkg-config python3-devel
+ + pygobject doesn't work with pyperclip
+ (evdev): sudo apt-get install python3-dev or python3.x, where x is version of your python