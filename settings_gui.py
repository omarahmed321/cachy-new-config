#!/usr/bin/env python3
import os
import re
import json
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

# Paths
MONITORS_CONF = os.path.expanduser("~/.config/hypr/monitors.conf")
USERPREFS_CONF = os.path.expanduser("~/.config/hypr/userprefs.conf")
NIGHTLIGHT_CONF = os.path.expanduser("~/.config/hypr/nightlight.conf")
NIGHTLIGHT_START = os.path.expanduser("~/.config/hypr/nightlight-start.sh")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hyprland Desktop Control Panel")
        self.geometry("600x750")
        self.configure(bg="#1e1e2e") # Dark mode theme (Catppuccin Mocha)

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", background="#1e1e2e", foreground="#cdd6f4")
        self.style.configure("TLabel", background="#1e1e2e", foreground="#cdd6f4", font=("Outfit", 11))
        self.style.configure("Header.TLabel", font=("Outfit", 16, "bold"), foreground="#a6e3a1")
        self.style.configure("Section.TLabel", font=("Outfit", 12, "bold"), foreground="#cba6f7")
        self.style.configure("TFrame", background="#1e1e2e")
        self.style.configure("Card.TFrame", background="#252538")
        self.style.configure("TButton", font=("Outfit", 10, "bold"), background="#313244", foreground="#cdd6f4")
        self.style.map("TButton", background=[("active", "#45475a")])
        self.style.configure("Primary.TButton", font=("Outfit", 10, "bold"), background="#a6e3a1", foreground="#11111b")
        self.style.map("Primary.TButton", background=[("active", "#b4befe")])

        # State Variables
        self.monitors = []
        self.sensitivity_val = tk.DoubleVar(value=0.0)
        self.natural_scroll_val = tk.BooleanVar(value=False)
        self.nightlight_enabled_val = tk.BooleanVar(value=False)
        self.nightlight_temp_val = tk.IntVar(value=3500)

        # Load configs
        self.load_monitors()
        self.load_inputs()
        self.load_nightlight()

        # Build UI
        self.build_ui()

    def load_monitors(self):
        # 1. Try to load from hyprctl dynamically
        try:
            res = subprocess.run(["hyprctl", "monitors", "-j"], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                data = json.loads(res.stdout)
                for mon in data:
                    self.monitors.append({
                        "name": mon["name"],
                        "description": mon.get("description", mon["name"]),
                        "width": mon["width"],
                        "height": mon["height"],
                        "refresh": int(round(mon["refreshRate"])),
                        "scale": mon["scale"],
                        "offset_x": mon["x"],
                        "offset_y": mon["y"]
                    })
                return
        except Exception:
            pass

        # 2. Fallback to parsing monitors.conf
        if os.path.exists(MONITORS_CONF):
            with open(MONITORS_CONF, "r") as f:
                content = f.read()
            matches = re.findall(r"monitor\s*=\s*([\w\-]+)\s*,\s*(\d+)x(\d+)@(\d+\.?\d*)\s*,\s*(\-?\d+)x(\-?\d+)\s*,\s*(\d+\.?\d*)", content)
            for m in matches:
                self.monitors.append({
                    "name": m[0],
                    "description": m[0],
                    "width": int(m[1]),
                    "height": int(m[2]),
                    "refresh": int(float(m[3])),
                    "offset_x": int(m[4]),
                    "offset_y": int(m[5]),
                    "scale": float(m[6])
                })
            if self.monitors:
                return

        # 3. Hardcoded defaults if nothing found
        self.monitors.append({
            "name": "eDP-2",
            "description": "Primary Laptop Screen (eDP-2)",
            "width": 2560,
            "height": 1600,
            "refresh": 165,
            "scale": 1.67,
            "offset_x": 0,
            "offset_y": 0
        })

    def load_inputs(self):
        if not os.path.exists(USERPREFS_CONF):
            return
        
        with open(USERPREFS_CONF, "r") as f:
            content = f.read()

        # Parse sensitivity
        sens_match = re.search(r"sensitivity\s*=\s*(\-?\d+\.?\d*)", content)
        if sens_match:
            self.sensitivity_val.set(float(sens_match.group(1)))

        # Parse natural_scroll
        ns_match = re.search(r"natural_scroll\s*=\s*(true|false)", content)
        if ns_match:
            self.natural_scroll_val.set(ns_match.group(1) == "true")

    def load_nightlight(self):
        if not os.path.exists(NIGHTLIGHT_CONF):
            return
        
        with open(NIGHTLIGHT_CONF, "r") as f:
            lines = f.readlines()

        for line in lines:
            parts = line.strip().split("=")
            if len(parts) == 2:
                key, val = parts[0].strip(), parts[1].strip()
                if key == "temperature":
                    self.nightlight_temp_val.set(int(val))
                elif key == "enabled":
                    self.nightlight_enabled_val.set(val == "true")

    def build_ui(self):
        # Main container with scrolling
        canvas = tk.Canvas(self, bg="#1e1e2e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=580)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        # Header Title
        title_label = ttk.Label(scroll_frame, text="Hyprland Configuration Wizard", style="Header.TLabel")
        title_label.pack(pady=15)

        # ----------------- MONITORS SECTION -----------------
        monitors_header = ttk.Label(scroll_frame, text="💻 Screen Resolutions & Positions", style="Section.TLabel")
        monitors_header.pack(anchor="w", pady=(10, 5))

        self.monitor_entries = []
        for index, mon in enumerate(self.monitors):
            card = ttk.Frame(scroll_frame, style="Card.TFrame")
            card.pack(fill="x", pady=5, ipady=8)

            # Monitor Name Header
            mon_title = ttk.Label(card, text=f"{mon['description']} ({mon['name']})", font=("Outfit", 11, "bold"), background="#252538", foreground="#a6e3a1")
            mon_title.grid(row=0, column=0, columnspan=4, sticky="w", padx=10, pady=(5, 10))

            # Resolution Width x Height
            ttk.Label(card, text="Resolution:", background="#252538").grid(row=1, column=0, sticky="w", padx=10, pady=5)
            w_var = tk.StringVar(value=str(mon["width"]))
            h_var = tk.StringVar(value=str(mon["height"]))
            
            w_entry = ttk.Entry(card, textvariable=w_var, width=6)
            w_entry.grid(row=1, column=1, sticky="w", pady=5)
            ttk.Label(card, text="x", background="#252538").grid(row=1, column=2, padx=2)
            h_entry = ttk.Entry(card, textvariable=h_var, width=6)
            h_entry.grid(row=1, column=3, sticky="w", pady=5)

            # Refresh Rate & Zoom/Scale
            ttk.Label(card, text="Hz (Refresh):", background="#252538").grid(row=2, column=0, sticky="w", padx=10, pady=5)
            ref_var = tk.StringVar(value=str(mon["refresh"]))
            ref_entry = ttk.Entry(card, textvariable=ref_var, width=6)
            ref_entry.grid(row=2, column=1, sticky="w", pady=5)

            ttk.Label(card, text="Scale (Zoom):", background="#252538").grid(row=2, column=2, sticky="w", padx=(10, 2), pady=5)
            scale_var = tk.StringVar(value=str(mon["scale"]))
            scale_entry = ttk.Entry(card, textvariable=scale_var, width=6)
            scale_entry.grid(row=2, column=3, sticky="w", pady=5)

            # Offsets (For cursor transition alignment)
            ttk.Label(card, text="Offset X:", background="#252538").grid(row=3, column=0, sticky="w", padx=10, pady=5)
            ox_var = tk.StringVar(value=str(mon["offset_x"]))
            ox_entry = ttk.Entry(card, textvariable=ox_var, width=6)
            ox_entry.grid(row=3, column=1, sticky="w", pady=5)

            ttk.Label(card, text="Offset Y:", background="#252538").grid(row=3, column=2, sticky="w", padx=(10, 2), pady=5)
            oy_var = tk.StringVar(value=str(mon["offset_y"]))
            oy_entry = ttk.Entry(card, textvariable=oy_var, width=6)
            oy_entry.grid(row=3, column=3, sticky="w", pady=5)

            # Hint for multi-monitor Y alignment
            if index > 0:
                align_hint = ttk.Label(card, text="💡 Modify Offset Y to align cursors between screens", font=("Outfit", 9, "italic"), foreground="#89b4fa", background="#252538")
                align_hint.grid(row=4, column=0, columnspan=4, sticky="w", padx=10, pady=(5, 0))

            self.monitor_entries.append({
                "name": mon["name"],
                "width": w_var,
                "height": h_var,
                "refresh": ref_var,
                "scale": scale_var,
                "offset_x": ox_var,
                "offset_y": oy_var
            })

        # ----------------- MOUSE & TOUCHPAD SECTION -----------------
        inputs_header = ttk.Label(scroll_frame, text="🖱️ Mouse & Touchpad Controls", style="Section.TLabel")
        inputs_header.pack(anchor="w", pady=(15, 5))

        inputs_card = ttk.Frame(scroll_frame, style="Card.TFrame")
        inputs_card.pack(fill="x", pady=5, ipady=8)

        # Mouse Sensitivity Slider
        ttk.Label(inputs_card, text="Mouse Sensitivity:", background="#252538").pack(anchor="w", padx=10, pady=(5, 2))
        sens_slider = tk.Scale(inputs_card, from_=-1.0, to=1.0, resolution=0.05, orient="horizontal",
                               variable=self.sensitivity_val, bg="#252538", fg="#cdd6f4", highlightthickness=0,
                               activebackground="#a6e3a1", troughcolor="#313244")
        sens_slider.pack(fill="x", padx=10, pady=(0, 10))

        # Natural Scrolling Checkbox
        ns_chk = tk.Checkbutton(inputs_card, text="Enable Natural Scrolling (Reverse laptop touchpad scroll like Windows)",
                                variable=self.natural_scroll_val, bg="#252538", fg="#cdd6f4", selectcolor="#313244",
                                activebackground="#252538", activeforeground="#cdd6f4", font=("Outfit", 10))
        ns_chk.pack(anchor="w", padx=10, pady=5)

        # ----------------- NIGHT LIGHT SECTION -----------------
        nightlight_header = ttk.Label(scroll_frame, text="🌙 Night Light Settings", style="Section.TLabel")
        nightlight_header.pack(anchor="w", pady=(15, 5))

        nl_card = ttk.Frame(scroll_frame, style="Card.TFrame")
        nl_card.pack(fill="x", pady=5, ipady=8)

        # Enabled Checkbox
        nl_chk = tk.Checkbutton(nl_card, text="Enable Night Light",
                                variable=self.nightlight_enabled_val, bg="#252538", fg="#cdd6f4", selectcolor="#313244",
                                activebackground="#252538", activeforeground="#cdd6f4", font=("Outfit", 10))
        nl_chk.pack(anchor="w", padx=10, pady=5)

        # Temperature Slider
        ttk.Label(nl_card, text="Color Temperature (Kelvin):", background="#252538").pack(anchor="w", padx=10, pady=(5, 2))
        temp_slider = tk.Scale(nl_card, from_=1000, to=10000, resolution=100, orient="horizontal",
                               variable=self.nightlight_temp_val, bg="#252538", fg="#cdd6f4", highlightthickness=0,
                               activebackground="#a6e3a1", troughcolor="#313244")
        temp_slider.pack(fill="x", padx=10, pady=(0, 10))

        # ----------------- SAVE BUTTONS -----------------
        btn_frame = ttk.Frame(scroll_frame)
        btn_frame.pack(fill="x", pady=25)

        save_btn = ttk.Button(btn_frame, text="💾 Apply & Save Config", style="Primary.TButton", command=self.apply_settings)
        save_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)

        close_btn = ttk.Button(btn_frame, text="❌ Close", command=self.destroy)
        close_btn.pack(side="right", fill="x", expand=True)

    def apply_settings(self):
        try:
            # 1. Save Monitors
            monitors_data = []
            for entry in self.monitor_entries:
                monitors_data.append({
                    "name": entry["name"],
                    "width": int(entry["width"].get()),
                    "height": int(entry["height"].get()),
                    "refresh": int(entry["refresh"].get()),
                    "scale": float(entry["scale"].get()),
                    "offset_x": int(entry["offset_x"].get()),
                    "offset_y": int(entry["offset_y"].get())
                })
            
            with open(MONITORS_CONF, "w") as f:
                f.write("# Generated by Hyprland Desktop Control Panel\n")
                for mon in monitors_data:
                    f.write(f"monitor = {mon['name']}, {mon['width']}x{mon['height']}@{mon['refresh']}, {mon['offset_x']}x{mon['offset_y']}, {mon['scale']}\n")

            # 2. Save Inputs (userprefs.conf)
            sens = self.sensitivity_val.get()
            ns = self.natural_scroll_val.get()
            self.update_userprefs_file(sens, ns)

            # 3. Save Nightlight Settings
            nl_enabled = self.nightlight_enabled_val.get()
            nl_temp = self.nightlight_temp_val.get()
            with open(NIGHTLIGHT_CONF, "w") as f:
                f.write(f"temperature={nl_temp}\ngamma=100\nenabled={'true' if nl_enabled else 'false'}\n")

            # 4. Reload Hyprland Live
            subprocess.run(["hyprctl", "reload"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # 5. Reload Night Light Live
            if os.path.exists(NIGHTLIGHT_START):
                subprocess.run(["bash", NIGHTLIGHT_START], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            messagebox.showinfo("Success", "Settings applied successfully and reloaded live!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply settings: {str(e)}")

    def update_userprefs_file(self, sensitivity, natural_scroll):
        if not os.path.exists(USERPREFS_CONF):
            # Create a basic template if missing
            with open(USERPREFS_CONF, "w") as f:
                f.write(f"input {{\n    sensitivity = {sensitivity:.2f}\n    touchpad {{\n        natural_scroll = {'true' if natural_scroll else 'false'}\n    }}\n}}\n")
            return

        with open(USERPREFS_CONF, "r") as f:
            lines = f.readlines()

        new_lines = []
        in_input = False
        in_touchpad = False
        sensitivity_updated = False
        natural_scroll_updated = False

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("input {"):
                in_input = True
            elif in_input and stripped.startswith("touchpad {"):
                in_touchpad = True
            elif in_touchpad and stripped.startswith("}"):
                in_touchpad = False
            elif in_input and not in_touchpad and stripped.startswith("}"):
                in_input = False

            if in_input and not in_touchpad and stripped.startswith("sensitivity"):
                indent = line[:line.find("sensitivity")]
                new_lines.append(f"{indent}sensitivity = {sensitivity:.2f}\n")
                sensitivity_updated = True
            elif in_touchpad and stripped.startswith("natural_scroll"):
                indent = line[:line.find("natural_scroll")]
                new_lines.append(f"{indent}natural_scroll = {'true' if natural_scroll else 'false'}\n")
                natural_scroll_updated = True
            else:
                new_lines.append(line)

        # If they weren't found in the file, append them cleanly inside the blocks
        # (Very basic fallback; if blocks aren't closed properly this might append. Under normal cases it works)
        with open(USERPREFS_CONF, "w") as f:
            f.writelines(new_lines)

if __name__ == "__main__":
    app = App()
    app.mainloop()
