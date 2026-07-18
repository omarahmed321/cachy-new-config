# CachyOS & Hyprland Complete System Replicator & Control Panel

This repository provides a unified script to replicate your entire CachyOS desktop shell, along with a custom GUI Control Panel to configure monitor resolution, refresh rate, scaling (zoom), mouse/touchpad settings, night light, and dual-monitor cursor transition alignments.

---

## 🚀 One-Line Installation (For a Fresh System)

To restore or install this entire customized setup on any fresh CachyOS installation, open a terminal and run the following single-line command:

```bash
curl -sSL https://raw.githubusercontent.com/omarahmed321/cachy-new-config/main/restore_my_setup.sh | bash
```

*This script will automatically download the custom leaves wallpaper, configure the Arabic keyboard layout, compile drivers, set up sddm, build the custom Waybar layout, set up credentials keyring, and install the Settings GUI panel.*

---

## 🛠️ Features Included

### 1. Unified Setup Restorer (`restore_my_setup.sh`)
* **Package Management**: Installs all required desktop packages, utilities, and fonts.
* **GPU Switcher**: Automatically downloads and configures **EnvyControl** in your local path (`~/.local/bin/envycontrol`) to easily switch between your AMD and Nvidia GPUs.
* **XKB Keyboard Layout**: Sets up a local override in `~/.config/xkb/symbols/ara` to map the `ذ` key to the backslash key (`thal_bksl`) without requiring root access or breaking layout files.
* **Authentication Keyring**: Configures `gnome-keyring` and sets the `PASSWORD_STORE=gnome-libsecret` environment variable so that Chromium and Electron-based apps (like Chrome and VS Code) securely remember your login sessions.
* **Wallpaper Fallback**: Automatically downloads your custom leaves wallpaper (`background_for_me.jpg`) from GitHub if the local folder is not found.
* **Waybar Split Pill Layout**: Generates a gorgeous, glassy green Waybar styling dynamically generated from the leaves wallpaper with custom paddings, showing active window icons and laptop modules (Wifi, Bluetooth, Battery).

### 2. Desktop Settings GUI (`settings_gui.py`)
This is a custom-built, dark-themed control panel to adjust system settings live:
* **Display Control**: Change monitor resolution, refresh rate (Hz), and zoom/scale (e.g., `1.67`).
* **Mouse & Touchpad**: Adjust mouse sensitivity and toggle Natural Scrolling (reverse scrolling direction for touchpads).
* **Night Light**: Toggle the night light overlay and adjust color temperature (Kelvin) live using a slider.
* **Dual-Monitor Alignment (Offset Y)**: Custom Offset Y coordinate inputs to align monitors of different sizes physically, so your cursor moves across them in a straight line.
* **Hyprland Keyboard Shortcut**: You can launch this control panel at any time by pressing:
  `Super + Alt + G`

---

## 📂 Project Structure

* **`restore_my_setup.sh`**: The automated installer script.
* **`settings_gui.py`**: The Python Tkinter desktop control panel.
* **`README.md`**: Repository documentation and installation guide.
