import time
from os import path, remove as delete_file

import tkinter as tk
from tkinter import ttk

from data_manager import DataManager, get_data_file
from config import Config, get_config_file
import helpers
from add_file import handle_add_file
from settings import handle_settings_request
from helpers import timestamp_to_date, get_unsynced_files
from file_observer import FileChangeHandler, FolderDeletionHandler

DEFAULT_CHECK_INTERVAL = 10

last_check = 0

DEFAULT_FONT = ("Arial", 10)

config = Config()
data_man : DataManager = DataManager(config.target_dir)

def get_data():
    files = sorted(data_man.files, key=lambda f: f['last-update'] if 'last-update' in f else 0, reverse=True)
    return list(map(lambda f: {
        'name': f['name'],
        'timestamp': timestamp_to_date(f['last-update']) if 'last-update' in f else 'N/A',
        'path': path.join(config.target_dir, f['name'])
        }, files))

def open_files(files):
    for file in files:
        file_path = path.join(config.target_dir, file)
        helpers.open_file(file_path)


def remove_files(files):
    global data_man
    with config.lock:
        data_man.remove_files(files)

def delete_selected(tree):
    files = get_selected_files(tree)
    for file in files:
        delete_file(path.join(config.target_dir, file))

def remove_and_delete_selected(tree):
    files = get_selected_files(tree)
    # This order is important, otherwise get into race condition
    for file in files:
        delete_file(path.join(config.target_dir, file))
    remove_files(files)

def refresh_table():
    global last_check
    global config
    synced_tree.delete(*synced_tree.get_children())
    create_table()
    target_dir_var.set(config.target_dir)
    refresh_unsynced_files()

def handle_tree_selection_event(event, other_tree):
    selected = event.widget.selection()
    if not selected:
        return
    other_tree.selection_remove(other_tree.selection())

    no_items_selected = (len(synced_tree.selection()) == 0 and len(unsynced_tree.selection()) == 0)
    no_synced_selected = len(synced_tree.selection()) == 0
    edit_menu.entryconfig("Open", state=tk.NORMAL if not no_items_selected else tk.DISABLED)
    edit_menu.entryconfig("Remove", state=tk.NORMAL if not no_synced_selected else tk.DISABLED)
    edit_menu.entryconfig("Delete", state=tk.NORMAL if not no_items_selected else tk.DISABLED)

def on_open_file(tree, event):
    item = tree.identify_row(event.y)
    if item:
        open_files([tree.item(item, "values")[0]])

def create_table():
    data = get_data()
    tree = synced_tree
    for row in data:
        tree.insert("", "end", values=(row["name"], row["timestamp"]))

def get_selected_files(tree):
    return [tree.item(item, "values")[0] for item in tree.selection()]

def open_selected(tree):
    selected_files = get_selected_files(tree)
    open_files(selected_files)

def remove_selected():
    selected_items = synced_tree.selection()
    selected_files = get_selected_files(synced_tree)

    remove_files(selected_files)
    for item in reversed(selected_items):
        synced_tree.delete(item)
    refresh_unsynced_files()
    
def delete_unsynced_files():
    response = tk.messagebox.askyesno("Delete Unsynced Files", "Are you sure you want to delete all unsynced files?")
    if not response:
        return

    dir, unsynced_files = get_unsynced_files(config, data_man)
    print('Unsynced files:', unsynced_files)
    for file in unsynced_files:
        delete_file(path.join(dir, file))
    refresh_unsynced_files()

def refresh_unsynced_files():
    global config, data_man
    unsynced_tree.delete(*unsynced_tree.get_children())
    dir, unsynced_files = get_unsynced_files(config, data_man)
    for file in unsynced_files:
        unsynced_tree.insert("", "end", values=(file,))

def on_add_file():
    try:
        handle_add_file(root, config, data_man)
    except Exception as e:
        print(e)
    refresh_table()

def empty_click_handler(event, tree):
    item = tree.identify_row(event.y)
    if not item:
        synced_tree.selection_remove(synced_tree.selection())
        unsynced_tree.selection_remove(unsynced_tree.selection())

def handle_synced_right_click(event):
    unsynced_tree.selection_remove(unsynced_tree.selection())
    current_item = synced_tree.identify_row(event.y)
    if current_item and current_item not in synced_tree.selection():
        synced_tree.selection_set(current_item)
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="Add Files", command=on_add_file)
    menu.add_command(label="Open file(s)", command=lambda: open_selected(synced_tree), state=tk.DISABLED if len(synced_tree.selection()) == 0 else tk.NORMAL)
    menu.add_command(label="Remove file(s)", command=remove_selected, state=tk.DISABLED if len(synced_tree.selection()) == 0 else tk.NORMAL)
    menu.add_command(label="Delete file(s)", command=lambda: remove_and_delete_selected(synced_tree), state=tk.DISABLED if len(synced_tree.selection()) == 0 else tk.NORMAL)
    menu.post(event.x_root, event.y_root)

def handle_unsynced_right_click(event):
    synced_tree.selection_remove(synced_tree.selection())
    current_item = unsynced_tree.identify_row(event.y)
    if current_item and current_item not in unsynced_tree.selection():
        unsynced_tree.selection_set(current_item)
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="Open", command=lambda: open_selected(unsynced_tree), state=tk.DISABLED if len(unsynced_tree.selection()) == 0 else tk.NORMAL)
    menu.add_command(label="Delete", command=lambda: delete_selected(unsynced_tree), state=tk.DISABLED if len(unsynced_tree.selection()) == 0 else tk.NORMAL)
    menu.add_command(label="Delete All", command=lambda: delete_unsynced_files(), state=tk.DISABLED if unsynced_tree.get_children() == () else tk.NORMAL)
    menu.post(event.x_root, event.y_root)

def create_synced_files_frame(window):
    synced_files_frame = tk.Frame(window)
    window.add(synced_files_frame)
    synced_label = tk.Label(synced_files_frame, text="Synced Files", font=DEFAULT_FONT)
    synced_label.pack(pady=1)
    
    global synced_tree
    synced_tree = ttk.Treeview(synced_files_frame, columns=("Name", "Timestamp"), show="headings")
    synced_tree.pack(fill=tk.BOTH, expand=True)
    synced_tree.heading("Name", text="Name")
    synced_tree.heading("Timestamp", text="Timestamp")
    synced_tree.column("Name", anchor="w")
    synced_tree.column("Timestamp", anchor="w")
    synced_tree.bind("<Double-Button-1>", lambda e: on_open_file(synced_tree, e))
    synced_tree.bind("<Button-1>", lambda e: empty_click_handler(e, synced_tree))
    synced_tree.bind("<Button-3>", handle_synced_right_click)
    synced_tree.bind("<<TreeviewSelect>>", lambda e: handle_tree_selection_event(e, unsynced_tree))
    refresh_table()

def create_unsynced_files_frame(window):
    unsynced_files_frame = tk.Frame(window)
    window.add(unsynced_files_frame, minsize=175)
    label = tk.Label(unsynced_files_frame, text="Unsynced Files", font=DEFAULT_FONT)
    label.pack(pady=1)
    
    global unsynced_tree
    unsynced_tree = ttk.Treeview(unsynced_files_frame, columns=("Name",), show="")
    unsynced_tree.pack(fill=tk.BOTH, expand=True)
    unsynced_tree.column("Name", anchor="w")
    unsynced_tree.bind("<Button-3>", handle_unsynced_right_click)
    unsynced_tree.bind("<<TreeviewSelect>>", lambda e: handle_tree_selection_event(e, synced_tree))
    unsynced_tree.bind("<Double-Button-1>", lambda e: on_open_file(unsynced_tree, e))
    unsynced_tree.bind("<Button-1>", lambda e: empty_click_handler(e, unsynced_tree))
    refresh_unsynced_files()

def on_settings_click():
    handle_settings_request(root, config)
    refresh_table()

def handle_escape(_):
    if len(synced_tree.selection()) > 0:
        synced_tree.selection_remove(synced_tree.selection())
    else:
        root.destroy()


def open_selected_items():
    if len(synced_tree.selection()) > 0:
        open_selected(synced_tree)
    elif len(unsynced_tree.selection()) > 0:
        open_selected(unsynced_tree)
    else:
        raise Exception("No items selected, button should be disabled")

def delete_selected_items():
    if len(synced_tree.selection()) > 0:
        remove_and_delete_selected(synced_tree)
    elif len(unsynced_tree.selection()) > 0:
        delete_selected(unsynced_tree)
    else:
        raise Exception("No items selected, button should be disabled")

def create_menu_bar(root):
    menu_bar = tk.Menu(root)

    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Add Files", command=on_add_file)
    file_menu.add_command(label="Delete Unsynced", command=delete_unsynced_files)
    file_menu.add_separator()
    file_menu.add_command(label="Settings", command=on_settings_click)
    menu_bar.add_cascade(label="File", menu=file_menu)

    global edit_menu
    edit_menu = tk.Menu(menu_bar, tearoff=0)
    edit_menu.add_command(label="Open", command=open_selected_items, state=tk.DISABLED)
    edit_menu.add_command(label="Remove", command=remove_selected, state=tk.DISABLED)
    edit_menu.add_command(label="Delete", command=delete_selected_items, state=tk.DISABLED)
    menu_bar.add_cascade(label="Edit", menu=edit_menu)

    root.config(menu=menu_bar)

def main():
    global root
    root = tk.Tk()
    root.geometry("600x400")
    root.title("Auto Cloud Upload")
    root.bind("<Escape>", handle_escape)
    root.bind("<Delete>", lambda e: remove_selected())
    root.bind("<Return>", lambda e: open_selected())
    root.bind("<Control-a>", lambda e: synced_tree.selection_set(synced_tree.get_children()))

    global target_dir_var
    target_dir_var = tk.StringVar()

    ttk.Style().configure("Treeview", font=DEFAULT_FONT)
    paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL)
    paned_window.pack(fill=tk.BOTH, expand=True)
    create_unsynced_files_frame(paned_window)
    create_synced_files_frame(paned_window)

    bottom_menu = tk.Frame(root)
    bottom_menu.pack(fill=tk.X)
    tk.Label(bottom_menu, text="Target Directory: ", font=DEFAULT_FONT).pack(side=tk.LEFT, padx=5)
    tk.Label(bottom_menu, textvariable=target_dir_var, font=DEFAULT_FONT).pack(side=tk.LEFT, padx=5)

    create_menu_bar(root)

    global last_data_update
    last_data_update = 0

    def on_data_update(_):
        global last_data_update
        global data_man
        if time.time() - last_data_update < .2:
            return
        last_data_update = time.time()
        time.sleep(.2)
        data_man.read_data()
        refresh_table()

    global last_target_folder_update
    last_target_folder_update = 0
    def on_target_folder_update(_):
        global last_target_folder_update
        if time.time() - last_target_folder_update < .2:
            return
        last_target_folder_update = time.time()
        time.sleep(.2)
        refresh_unsynced_files()

    def config_update(_):
        old_target = config.target_dir
        config.read_config()
        if old_target != config.target_dir:
            refresh_table()
            refresh_unsynced_files()
            target_dir_var.set(config.target_dir)
            target_folder_observer.update_watched_dirs(config.target_dir)

    file_observer = FileChangeHandler([get_data_file()], on_data_update)
    file_observer.start()

    target_folder_observer = FolderDeletionHandler(config.target_dir, on_target_folder_update)
    target_folder_observer.start()

    config_observer = FileChangeHandler([get_config_file()], config_update)
    config_observer.start()

    root.mainloop()

if __name__ == "__main__":
    main()

