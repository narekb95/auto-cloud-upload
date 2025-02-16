import tkinter as tk
import config as cnf

class Setting:
    def __init__(self, label, attribute, value):
        self.label = label
        self.attribute = attribute
        self.var = tk.StringVar(value=value)

def get_current_settings(config):
    settings_items = [
        ("Target folder", "target_dir"),
        ("Update frequency", "update_frequency"),
        ("Scheduler frequency", "scheduler_frequency")]
    settings = [Setting(label, attribute, getattr(config, attribute))\
                 for label, attribute in settings_items]
    return settings

def update_settings(settings, config):
    with config.lock:
        config.read_config()
        old_dir = config.target_dir
        for setting in settings:
            setattr(config, setting.attribute, setting.var.get())
        if old_dir != config.target_dir:
            config.reset_files()
        config.update_config()

def create_settings_window(dialog, config):
    def submit():
        update_settings(settings, config)
        dialog.destroy()

    dialog.title("Add file")

    settings_frame = tk.Frame(dialog)
    settings_frame.pack(fill=tk.X, expand=True, anchor="n", padx=30, pady=10)
    settings_frame.columnconfigure(0, weight=0)
    settings_frame.columnconfigure(1, weight=1)
    settings_frame.columnconfigure(2, weight=0)
    settings = get_current_settings(config)
    for i, setting in enumerate(settings):
        tk.Label(settings_frame, text=setting.label, font=('Ariel', 10))\
            .grid(row=i, column=0, padx=10, pady=10, sticky="w")
        setting_entry = tk.Entry(settings_frame, textvariable=setting.var,\
                width = 30, font=('Ariel', 10))
        setting_entry.grid(row=i, column=1, padx=10, pady=10, sticky="ew")
        if i == 0:
            setting_entry.focus_set()
            setting_entry.select_range(0, tk.END)
    
    target_button = tk.Button(settings_frame, text="Browse", command=lambda setting=settings[0]:\
                                setting.var.set(tk.filedialog.askdirectory()))
    target_button.grid(row=0, column=2, padx=10, pady=10, sticky="w")

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