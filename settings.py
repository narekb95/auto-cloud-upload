import tkinter as tk
import config as cnf
import tkinter.filedialog

from enum import Enum
class SettingType(Enum):
    TEXT = 1
    NUMERIC = 2
    FOLDER = 3

class Setting:
    def __init__(self, label, attribute, value, type : SettingType):
        self.label = label
        self.attribute = attribute
        self.var = tk.StringVar(value=value)
        self.type = type

def get_current_settings(config):
    settings_items = [
        ("Target folder", "target_dir", SettingType.FOLDER),
        ("Postpone period", "postpone_period", SettingType.NUMERIC),
        ]
    settings = [Setting(label, attribute, getattr(config, attribute), type)\
                 for label, attribute, type in settings_items]
    return settings

def update_settings(settings, config):
    with config.lock:
        config.read_config()
        for setting in settings:
            setting_value = setting.var.get()
            if setting.type == SettingType.NUMERIC:
                try:
                    setting_value = float(setting_value)
                except ValueError:
                    raise ValueError(f"Invalid value for {setting.label}")
            setattr(config, setting.attribute, setting_value)
        config.update_config()


def create_settings_window(dialog, config):
    global folder_icon
    folder_icon = tk.PhotoImage(file="media/buttons/folder.png")


    def submit():
        try:
            update_settings(settings, config)
            dialog.destroy()
        except ValueError as e:
            tk.messagebox.showerror("Error", str(e))
            return

    dialog.title("Add file")

    settings_frame = tk.Frame(dialog)
    settings_frame.pack(fill=tk.X, expand=True, anchor="n", padx=30, pady=10)
    settings_frame.columnconfigure(0, weight=0)
    settings_frame.columnconfigure(1, weight=0)
    settings_frame.columnconfigure(2, weight=1)
    settings = get_current_settings(config)

    
    def update_directory(i):
        folder =tk.filedialog.askdirectory()
        if folder:
            settings[i].var.set(folder)

    for i, setting in enumerate(settings):
        tk.Label(settings_frame, text=setting.label, font=('Ariel', 10))\
            .grid(row=i, column=0, padx=10, pady=10, sticky="w")
        setting_entry = tk.Entry(settings_frame, textvariable=setting.var,\
                width = 30, font=('Ariel', 10))
        setting_entry.grid(row=i, column=2, padx=10, pady=10, sticky="ew")
        if i == 0:
            setting_entry.focus_set()
            setting_entry.select_range(0, tk.END)
    
        if setting.type == SettingType.FOLDER:
            target_folder_button = tk.Button(settings_frame, image=folder_icon, \
                command = lambda i=i: update_directory(i))
            target_folder_button.grid(row=i, column=1, padx=0, pady=10, sticky="w")

    submit_frame = tk.Frame(dialog)
    submit_frame.pack(expand=True)
    tk.Button(submit_frame, text="Submit", command=submit).pack()
    dialog.bind('<Escape>', lambda _: dialog.destroy())
    dialog.bind('<Return>', lambda _: submit())
    tk.Frame(dialog).pack(pady=8)
        
    
def handle_settings_request(root, config):
    dialog = tk.Toplevel()
    dialog.transient(root)
    dialog.grab_set()
    dialog.focus_set()
    create_settings_window(dialog, config)
    root.wait_window(dialog)

def main():
    root = tk.Tk()
    config = cnf.Config()
    create_settings_window(root, config)
    root.mainloop()

if __name__ == '__main__':
    main()