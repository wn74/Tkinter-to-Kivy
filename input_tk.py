import tkinter as tk

def submit_form(event=None):
    print("Form submitted successfully!")

def clear_form(event=None):
    print("Form fields cleared.")

def on_hover(event=None):
    print("Hovering over submit button.")

root = tk.Tk()
root.title("User Registration Form")

# 1. Header Section (uses pack)
header_frame = tk.Frame(root)
header_frame.pack()

title_label = tk.Label(header_frame, text="Create a New Account")
title_label.pack()

# 2. Form Section (uses grid for 2-column layout)
form_frame = tk.Frame(root)
form_frame.pack()

username_label = tk.Label(form_frame, text="Username:")
username_label.grid(row=0, column=0)

username_entry = tk.Entry(form_frame)
username_entry.grid(row=0, column=1)
# Binding the Enter key to the submit function
username_entry.bind("<Return>", submit_form)

password_label = tk.Label(form_frame, text="Password:")
password_label.grid(row=1, column=0)

password_entry = tk.Entry(form_frame)
password_entry.grid(row=1, column=1)
password_entry.bind("<Return>", submit_form)

# 3. Action Buttons Section (uses grid for side-by-side buttons)
action_frame = tk.Frame(root)
action_frame.pack()

submit_btn = tk.Button(action_frame, text="Submit", command=submit_form)
submit_btn.grid(row=0, column=0)
# Binding mouse enter event
submit_btn.bind("<Enter>", on_hover)

clear_btn = tk.Button(action_frame, text="Clear")
clear_btn.grid(row=0, column=1)
# Binding left mouse click instead of using 'command'
clear_btn.bind("<Button-1>", clear_form)

root.mainloop()