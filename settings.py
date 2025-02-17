import tkinter as tk
import config as cnf
import tkinter.filedialog

class Setting:
    def __init__(self, label, attribute, value, is_numeric):
        self.label = label
        self.attribute = attribute
        self.var = tk.StringVar(value=value)
        self.is_numeric = is_numeric

def get_current_settings(config):
    settings_items = [
        ("Target folder", "target_dir", False),
        ("Update frequency", "update_frequency", True),
        ("Scheduler frequency", "scheduler_frequency", True),
        ("Postpone period", "postpone_period", True)
        ]
    settings = [Setting(label, attribute, getattr(config, attribute), is_numeric)\
                 for label, attribute, is_numeric in settings_items]
    return settings

def update_settings(settings, config, data_man):
    with config.lock:
        config.read_config()
        for setting in settings:
            setattr(config, setting.attribute, int(setting.var.get()) if setting.is_numeric else setting.var.get())
        data_man.update_target_dir(settings[0].var.get())
        config.update_config()

def create_settings_window(dialog, config, data_man):
    def submit():
        update_settings(settings, config, data_man)
        dialog.destroy()

    dialog.title("Add file")

    settings_frame = tk.Frame(dialog)
    settings_frame.pack(fill=tk.X, expand=True, anchor="n", padx=30, pady=10)
    settings_frame.columnconfigure(0, weight=0)
    settings_frame.columnconfigure(1, weight=0)
    settings_frame.columnconfigure(2, weight=1)
    settings = get_current_settings(config)
    for i, setting in enumerate(settings):
        tk.Label(settings_frame, text=setting.label, font=('Ariel', 10))\
            .grid(row=i, column=0, padx=10, pady=10, sticky="w")
        setting_entry = tk.Entry(settings_frame, textvariable=setting.var,\
                width = 30, font=('Ariel', 10))
        setting_entry.grid(row=i, column=2, padx=10, pady=10, sticky="ew")
        if i == 0:
            setting_entry.focus_set()
            setting_entry.select_range(0, tk.END)
    
    def update_directory():
        folder =tk.filedialog.askdirectory()
        if folder:
            settings[0].var.set(folder)

    folder_icon = tk.PhotoImage(file="media/buttons/folder.png")
    target_folder_button = tk.Button(settings_frame, image=folder_icon, \
        command = update_directory)
    target_folder_button.image = folder_icon  # Keep a reference to avoid garbage collection
    target_folder_button.grid(row=0, column=1, padx=0, pady=10, sticky="w")

    submit_frame = tk.Frame(dialog)
    submit_frame.pack(expand=True)
    tk.Button(submit_frame, text="Submit", command=submit).pack()
    dialog.bind('<Escape>', lambda _: dialog.destroy())
    dialog.bind('<Return>', lambda _: submit())
    tk.Frame(dialog).pack(pady=8)
        
    
def handle_settings_request(root, config, data_man):
    dialog = tk.Toplevel()
    dialog.transient(root)
    dialog.grab_set()
    dialog.focus_set()
    create_settings_window(dialog, config, data_man)
    root.wait_window(dialog)

def main():
    root = tk.Tk()
    config = cnf.Config()
    create_settings_window(root, config)
    root.mainloop()

if __name__ == '__main__':
    main()