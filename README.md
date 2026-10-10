# Tkinter to Kivy

> **Warning:** This project is fully AI-generated. The code, architecture, and documentation were created by an artificial intelligence model and are provided as an experimental proof of concept. Review and test thoroughly before production use.

---

## Overview

Migrating desktop GUIs from Tkinter to cross-platform frameworks like Kivy usually requires manual rewriting. This project automates that workflow using Python's native `ast` module:

```
[Tkinter Python Code]
         |
         v
[Python ast.parse]
         |
         v
[AST NodeVisitor]  --> Extracts widgets, nested Frames, grid/pack geometry, and bindings
         |
         v
[Code Generator]   --> Emits runnable Kivy Python application + .kv layout string
```

---

## Features

- AST-Powered Parsing: Safe, static inspection of Python source code without executing runtime scripts.
- Nested Layouts: Recursively processes `tk.Frame` hierarchies and maps them to nested Kivy containers.
- Dynamic Geometry Inference:
  - Stacks via `.pack()` are mapped to vertical `BoxLayout`.
  - Matrix forms via `.grid()` are automatically converted to `GridLayout`, calculating the required `cols` attribute dynamically.
- Widget Translation: Maps `tk.Label`, `tk.Button`, and `tk.Entry` to Kivy's `Label`, `Button`, and `TextInput`.
- Event and Binding Handling:
  - Translates `command=func` to `on_release: app.func()`.
  - Maps common `.bind(...)` events (e.g., `<Button-1>` to `on_press`, `<Return>` to `on_text_validate`).
  - Automatically comments out unsupported touch/hover events (e.g., `<Enter>`) to prevent runtime Kivy `BuilderException` errors.
- Callback Parameter Re-scoping: Converts functions into class methods by automatically injecting `self` and `*args`.

---

## Requirements

- Python 3.9 to 3.12 (Python 3.11 or 3.12 recommended on Windows for pre-built Kivy wheels).
- Kivy (required to run the generated output file):
  ```bash
  pip install kivy
  ```

---

## Usage

### 1. Setup the Environment

```bash
python -m pip install --upgrade pip
pip install kivy
```

*(Note: If you have Python 3.14+ installed globally on Windows, create a Python 3.12 virtual environment first with `py -3.12 -m venv .venv` and activate it before installing Kivy).*

### 2. Run the Transpiler

Transpile a Tkinter script into a Kivy script:

```bash
python transpiler.py input_tk.py output_kivy.py
```

If run without arguments, it defaults to reading `input_tk.py` and writing to `output_kivy.py`:

```bash
python transpiler.py
```

### 3. Run the Generated App

```bash
python output_kivy.py
```

---

## Input vs. Output Example

### Input (Tkinter)
```python
import tkinter as tk

def submit_form(event=None):
    print("Form submitted!")

root = tk.Tk()
root.title("Registration")

form_frame = tk.Frame(root)
form_frame.pack()

username_label = tk.Label(form_frame, text="Username:")
username_label.grid(row=0, column=0)

username_entry = tk.Entry(form_frame)
username_entry.grid(row=0, column=1)
username_entry.bind("<Return>", submit_form)

submit_btn = tk.Button(root, text="Submit", command=submit_form)
submit_btn.pack()

root.mainloop()
```

### Transpiled Output (Kivy)
```python
from kivy.app import App
from kivy.lang import Builder

KV_LAYOUT = """
BoxLayout:
    orientation: 'vertical'
    padding: 20
    spacing: 10
    GridLayout:
        id: form_frame
        cols: 2
        Label:
            id: username_label
            text: 'Username:'
        TextInput:
            id: username_entry
            on_text_validate: app.submit_form()
    Button:
        id: submit_btn
        text: 'Submit'
        on_release: app.submit_form()
"""

class ConvertedApp(App):
    def submit_form(self, *args, event=None):
        print("Form submitted!")

    def build(self):
        return Builder.load_string(KV_LAYOUT)

if __name__ == '__main__':
    ConvertedApp().run()
```

---

## License

This project is licensed under the MIT License.