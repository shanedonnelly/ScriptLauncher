import os
import sys
import tkinter as tk
from tkinter import messagebox
import subprocess
from PIL import Image, ImageTk  # Ensure Pillow is installed: pip install Pillow
from ttkbootstrap import Style  # Ensure ttkbootstrap is installed: pip install ttkbootstrap

PRESETS_FOLDER = "presets"
ASSETS_FOLDER = os.path.join("assets", "app_icons")
MAX_COLUMNS = 6  # Updated to 6 columns

class ScriptLauncherApp:
    def __init__(self, root):
        print("Debug: Initializing ScriptLauncherApp...")
        
        # Initialize ttkbootstrap style
        # Available themes: 'superhero', 'flatly', 'darkly', 'cosmo', 'journal', 'litera',
        # 'minty', 'pulse', 'sandstone', 'simplex', 'yeti', 'materia', etc.
        self.style = Style(theme="pulse")
        # self.style = Style(theme="sandstone")
        # self.style = Style(theme="simplex")
        # self.style = Style(theme="yeti")


        self.root = root
        self.root.title("ScriptLauncher")
        self.root.configure(highlightthickness=0)
        self.next_position = 0

        root.protocol("WM_DELETE_WINDOW", self.exit_app)

        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        win_w = int(screen_w * 0.9)
        win_h = int(screen_h * 0.95)
        pos_x = (screen_w - win_w) // 2
        pos_y = (screen_h - win_h) // 2
        self.root.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")

        os.makedirs(PRESETS_FOLDER, exist_ok=True)
        os.makedirs(ASSETS_FOLDER, exist_ok=True)

        # Fixed width/height for buttons
        self.button_width = 20
        self.button_height = 5

        # Canvas and scrollbar for presets
        self.canvas = tk.Canvas(root, borderwidth=0, background="#ffffff")
        self.scrollbar = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.place(relx=1.0, rely=0.0, relheight=1.0, anchor="ne")
        self.canvas.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)

        self.presets_frame = tk.Frame(self.canvas, background="#ffffff")
        self.canvas.create_window((0, 0), window=self.presets_frame, anchor="nw")
        self.presets_frame.bind("<Configure>", self.on_frame_configure)

        self.plus_btn = tk.Button(
            self.presets_frame,
            text="➕",
            width=self.button_width,
            height=self.button_height,
            command=self.open_add_dialog,
            bg=self.style.colors.primary,
            fg="white",
            relief=tk.RAISED
        )

        self.icon_images = {}
        self.preset_widgets = {}  # Mapping for preset widgets
        self.load_icon_images()

        self.load_existing_presets()
        self.update_plus_position()

    def load_icon_images(self):
        print("Debug: Loading icons from assets/app_icons...")
        if not os.path.exists(ASSETS_FOLDER):
            os.makedirs(ASSETS_FOLDER)
        for file in sorted(os.listdir(ASSETS_FOLDER)):
            if file.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                path = os.path.join(ASSETS_FOLDER, file)
                try:
                    image = Image.open(path).resize((24, 24), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    self.icon_images[file] = photo
                except Exception as e:
                    print(f"Error loading image {file}: {e}")

    def exit_app(self, *args):
        print("Debug: Exiting application...")
        self.root.quit()

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_plus_position(self):
        row = self.next_position // MAX_COLUMNS
        col = self.next_position % MAX_COLUMNS
        self.plus_btn.grid(row=row, column=col, padx=5, pady=5)

    def add_preset_button(self, title, file_name, icon='none'):
        self.plus_btn.grid_forget()
        print(f"Debug: Adding preset button '{title}' at position {self.next_position}...")
        frame = tk.Frame(self.presets_frame, bd=2, relief=tk.RIDGE)
        row = self.next_position // MAX_COLUMNS
        col = self.next_position % MAX_COLUMNS
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Container for the main button
        button_frame = tk.Frame(frame)
        button_frame.pack(fill=tk.BOTH, expand=True)

        # Main script button
        btn = tk.Button(
            button_frame,
            text=title,
            width=self.button_width,
            height=self.button_height,
            font=("TkDefaultFont", 12),
            bg=self.style.colors.primary,
            fg="white",
            relief=tk.RAISED,
            command=lambda f=file_name: self.run_preset(f)
        )
        btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # If icon is provided, place top-left
        icon_label = None
        if icon != 'none' and icon in self.icon_images:
            icon_label = tk.Label(button_frame, image=self.icon_images[icon], bg=self.style.colors.primary)
            icon_label.place(x=5, y=5)

        # Edit/Delete stacked to the right
        buttons_right_frame = tk.Frame(button_frame, bg=self.style.colors.primary)
        buttons_right_frame.pack(side=tk.RIGHT, padx=2, pady=2)

        edit_btn = tk.Button(
            buttons_right_frame,
            text="✎",
            width=3,
            height=1,
            command=lambda f=file_name, t=title: self.edit_preset(f, t),
            bg=self.style.colors.secondary,
            fg="white",
            relief=tk.RAISED
        )
        edit_btn.pack(side=tk.TOP, padx=2, pady=2)

        del_btn = tk.Button(
            buttons_right_frame,
            text="🗑",
            width=3,
            height=1,
            command=lambda f=file_name: self.delete_preset(f, frame),
            bg=self.style.colors.danger,
            fg="white",
            relief=tk.RAISED
        )
        del_btn.pack(side=tk.TOP, padx=2, pady=2)

        # Store the button reference
        self.preset_widgets[file_name] = {
            'frame': frame,
            'button': btn,
            'icon_label': icon_label
        }

        self.next_position += 1
        self.update_plus_position()

    def delete_preset(self, file_name, frame):
        print(f"Debug: Deleting preset '{file_name}'...")
        preset_path = os.path.join(PRESETS_FOLDER, file_name)
        if os.path.exists(preset_path):
            os.remove(preset_path)
        frame.destroy()
        self.rearrange_presets()

    def load_existing_presets(self):
        print("Debug: Loading existing presets...")
        self.next_position = 0
        for file in sorted(os.listdir(PRESETS_FOLDER)):
            if file.endswith(".slaunch"):
                preset_path = os.path.join(PRESETS_FOLDER, file)
                with open(preset_path, "r") as f:
                    lines = f.readlines()
                if len(lines) >= 4:
                    title_line = lines[0].strip().replace("title=", "")
                    type_line = lines[1].strip().replace("type=", "")
                    icon_line = lines[2].strip().replace("icon=", "")
                    self.add_preset_button(title_line, file, icon_line)

    def save_preset(self, file_name, title, preset_type, content, icon='none'):
        print(f"Debug: Saving preset '{file_name}' (new format)...")
        preset_path = os.path.join(PRESETS_FOLDER, file_name)
        with open(preset_path, "w") as f:
            f.write(f"title={title}\n")
            f.write(f"type={preset_type}\n")
            f.write(f"icon={icon}\n")
            f.write("script=\n")
            f.write(content)

    def run_preset(self, file_name):
        print(f"Debug: Running preset '{file_name}'...")
        preset_path = os.path.join(PRESETS_FOLDER, file_name)
        if os.path.exists(preset_path):
            with open(preset_path, 'r') as f:
                lines = f.readlines()
            if len(lines) >= 4:
                script_content = "".join(lines[4:]).strip()
                temp_script = os.path.join(PRESETS_FOLDER, f"temp_{file_name}")
                with open(temp_script, 'w') as ftemp:
                    ftemp.write(script_content)
                subprocess.run(["chmod", "777", temp_script])
                subprocess.run(["gnome-terminal", "--", "bash", "-c", f"'{temp_script}'; exec bash"])
                os.remove(temp_script)
        else:
            messagebox.showerror("Error", "Preset not found!")

    def open_icon_gallery(self, parent_dialog, icon_var, selected_icon_label):
        print("Debug: Rebuilding icon gallery from scratch...")
        gallery_popup = tk.Toplevel(parent_dialog)
        gallery_popup.title("Select Icon")
        gallery_popup.geometry("289x280")
        gallery_popup.transient(parent_dialog)
        gallery_popup.configure(highlightthickness=0)

        canvas = tk.Canvas(gallery_popup, highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(gallery_popup, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)
        icons_frame = tk.Frame(canvas, bg="#ffffff")
        canvas.create_window((0, 0), window=icons_frame, anchor='nw')

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        icons_frame.bind("<Configure>", on_frame_configure)

        def select_icon(icon_name):
            print(f"Debug: Icon selected -> {icon_name}")
            selected_icon_label.config(text=icon_name if icon_name != "none" else "")
            icon_var.set(icon_name)
            gallery_popup.destroy()

        none_btn = tk.Button(
            icons_frame,
            text="",
            width=1,
            height=1,
            command=lambda: select_icon("none"),
            bg=self.style.colors.secondary,
            fg="white",
            relief=tk.RAISED
        )
        none_btn.grid(row=0, column=0, padx=5, pady=5)

        row_index = 0
        col_index = 1
        for icon_file, photo in sorted(self.icon_images.items()):
            btn = tk.Button(
                icons_frame,
                image=photo,
                command=lambda name=icon_file: select_icon(name),
                bg="#ffffff",
                borderwidth=1,
                relief=tk.RIDGE
            )
            btn.grid(row=row_index, column=col_index, padx=5, pady=5)
            col_index += 1
            if col_index >= MAX_COLUMNS:
                row_index += 1
                col_index = 0

    def show_preset_dialog(self, title="", content="", preset_type="standard",
                           file_name=None, icon="none"):
        print("Debug: Creating preset dialog...")
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Preset" if file_name else "Add Preset")
        dialog.geometry("900x800")
        dialog.transient(self.root)
        dialog.configure(highlightthickness=0)

        dialog_frame = tk.Frame(dialog, padx=10, pady=10)
        dialog_frame.pack(fill=tk.BOTH, expand=True)

        title_label = tk.Label(dialog_frame, text="Title:")
        title_label.pack(pady=5, anchor='w')
        title_entry = tk.Entry(dialog_frame, width=80)
        title_entry.insert(0, title)
        title_entry.pack(pady=5, fill=tk.X)

        type_label = tk.Label(dialog_frame, text="Type:")
        type_label.pack(pady=5, anchor='w')
        type_var = tk.StringVar(value=preset_type)

        type_frame = tk.Frame(dialog_frame)
        type_frame.pack(pady=5, anchor='w')

        def select_type(selected_type):
            type_var.set(selected_type)
            standard_btn.config(relief=tk.SUNKEN if selected_type == "standard" else tk.RAISED)
            pausable_btn.config(relief=tk.SUNKEN if selected_type == "pausable" else tk.RAISED)
            recorded_btn.config(relief=tk.SUNKEN if selected_type == "recorded" else tk.RAISED)

        standard_btn = tk.Button(type_frame, text="Standard", command=lambda: select_type("standard"))
        standard_btn.pack(side=tk.LEFT, padx=2)
        pausable_btn = tk.Button(type_frame, text="Pausable", command=lambda: select_type("pausable"))
        pausable_btn.pack(side=tk.LEFT, padx=2)
        recorded_btn = tk.Button(type_frame, text="Recorded", command=lambda: select_type("recorded"))
        recorded_btn.pack(side=tk.LEFT, padx=2)

        select_type(preset_type)

        icon_label = tk.Label(dialog_frame, text="Icon:")
        icon_label.pack(pady=5, anchor='w')

        icon_frame = tk.Frame(dialog_frame)
        icon_frame.pack(pady=5, anchor='w')

        icon_var = tk.StringVar(value=icon)
        selected_icon_label = tk.Label(icon_frame, text=(icon if icon != "none" else ""))
        selected_icon_label.pack(side=tk.LEFT, padx=5)

        icon_popup_btn = tk.Button(icon_frame, text="Choose Icon",
                                   command=lambda: self.open_icon_gallery(dialog, icon_var, selected_icon_label))
        icon_popup_btn.pack(side=tk.LEFT, padx=5)

        content_label = tk.Label(dialog_frame, text="Script Content:")
        content_label.pack(pady=5, anchor='w')
        content_text = tk.Text(dialog_frame, width=80, height=20)
        content_text.pack(pady=5, fill=tk.BOTH, expand=True)
        content_text.insert("1.0", content)

        def on_save():
            print("Debug: Save button clicked...")
            new_title = title_entry.get().strip()
            new_type = type_var.get().strip()
            new_icon = icon_var.get().strip()
            script_content = content_text.get("1.0", tk.END).strip()
            if not new_title or not script_content:
                messagebox.showerror("Error", "Please fill in all fields.")
                return
            if file_name:
                self.save_preset(file_name, new_title, new_type, script_content, new_icon)
                # Update the specific button
                widget = self.preset_widgets.get(file_name)
                if widget:
                    widget['button'].config(text=new_title)
                    # Update icon
                    if new_icon != "none" and new_icon in self.icon_images:
                        widget['icon_label'].config(image=self.icon_images[new_icon])
                        widget['icon_label'].image = self.icon_images[new_icon]  # Prevent GC
                    else:
                        if widget['icon_label']:
                            widget['icon_label'].destroy()
                            widget['icon_label'] = None
                dialog.destroy()
            else:
                existing = [f for f in os.listdir(PRESETS_FOLDER) if f.endswith(".slaunch")]
                next_index = len(existing) + 1
                new_file_name = f"preset{next_index}.slaunch"
                self.save_preset(new_file_name, new_title, new_type, script_content, new_icon)
                self.add_preset_button(new_title, new_file_name, new_icon)
                dialog.destroy()

        save_button = tk.Button(dialog_frame, text="Save", command=on_save, bg=self.style.colors.success, fg="white")
        save_button.pack(pady=10)

    def open_add_dialog(self):
        print("Debug: Opening Add Preset dialog...")
        self.show_preset_dialog()

    def edit_preset(self, file_name, old_title):
        print(f"Debug: Editing preset '{file_name}'...")
        preset_path = os.path.join(PRESETS_FOLDER, file_name)
        if os.path.exists(preset_path):
            with open(preset_path, 'r') as f:
                lines = f.readlines()
            if len(lines) >= 4:
                title_val = lines[0].replace("title=", "").strip()
                type_val = lines[1].replace("type=", "").strip()
                icon_val = lines[2].replace("icon=", "").strip()
                content_val = "".join(lines[4:]).strip()
                self.show_preset_dialog(title_val, content_val, type_val, file_name, icon_val)

    def reload_presets(self):
        print("Debug: Reloading presets...")
        # Remove all preset frames except the plus button
        for widget in self.presets_frame.winfo_children():
            if widget != self.plus_btn:
                widget.destroy()
        # Clear the preset_widgets dictionary
        self.preset_widgets.clear()
        # Reset position
        self.next_position = 0
        # Reload presets from the folder
        self.load_existing_presets()
        # Update the position of the plus button
        self.update_plus_position()

    def rearrange_presets(self):
        print("Debug: Rearranging presets...")
        self.next_position = 0
        for widget in self.presets_frame.winfo_children():
            if widget != self.plus_btn:
                row = self.next_position // MAX_COLUMNS
                col = self.next_position % MAX_COLUMNS
                widget.grid_configure(row=row, column=col, padx=5, pady=5, sticky="nsew")
                self.next_position += 1
        self.update_plus_position()

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = ScriptLauncherApp(root)
        root.mainloop()
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)