import tkinter as tk
from tkinter import simpledialog


def custom_messagebox(title, message, options):
    # Create a custom dialog window
    dialog = tk.Toplevel()
    dialog.title(title)
    dialog.geometry("300x150")
    dialog.resizable(False, False)
    
    # Center the window
    
    # Add the message
    label = tk.Label(dialog, text=message, wraplength=250)
    label.pack(pady=10)
    
    # Variable to store user response
    response = tk.StringVar()
    response.set(None)
    
    # Button commands to set the response and close the dialog
    def set_response(value):
        response.set(value)
        dialog.destroy()
    
    # Add buttons
    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=10)
    
    buttons = [
        tk.Button(button_frame, text=option, command=lambda opt=option: set_response(opt))
        for option in options
    ]
    for button in buttons:
        button.pack(side=tk.LEFT, padx=5)    
    # Wait for the dialog to be closed
    dialog.wait_window()
    
    return response.get()


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    result = custom_messagebox("Action Required", "What would you like to do?", ["Upload", "Download", "Cancel"])
    print(f"User selected: {result}")
