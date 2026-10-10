# Tkinter-to-Kivy

> **Warning:** This project is fully AI-generated. The code, architecture, and documentation were created by an artificial intelligence model and are provided as an experimental proof of concept. Review and test thoroughly before production use.

An AST-based Python transpiler that automatically converts Tkinter code into modern Kivy applications and .kv layout declarations.

---

### `README.md`

```markdown
# Tk2Kivy Transpiler

An Abstract Syntax Tree (AST) transpiler that extracts GUI widget declarations, geometries, and callbacks from Tkinter code and generates Kivy application code and .kv layouts.

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
[AST NodeVisitor]  --> Extracts widgets, properties, geometry, and callbacks
         |
         v
[Code Generator]   --> Emits Kivy Python + .kv Layout string
```

---

## Features

- AST-Powered Parsing: Safe, static inspection of Python source code without executing runtime scripts.
- Widget Translation: Converts `tk.Label`, `tk.Button`, and `tk.Entry` into native Kivy UI components (`Label`, `Button`, `TextInput`).
- Callback and Binding Migration: Automatically converts Tkinter `command=func` callbacks into Kivy-compatible `on_release: app.func()` methods and injects `self`.
- Zero External Dependencies: Built entirely using Python standard libraries (`ast`, `textwrap`).

---

## Requirements

- Python 3.9+ (uses `ast.unparse`)
- Kivy (only needed to run the emitted output code):
  ```bash
  pip install kivy
  ```

---

## Usage

### 1. Run the Transpiler

Clone the repository and run the transpiler script:

```bash
git clone https://github.com/your-username/tk2kivy-transpiler.git
cd tk2kivy-transpiler
python transpiler.py
```

### 2. Input vs. Output Example

#### Input (Tkinter)
```python
import tkinter as tk

def on_click():
    print("Button pressed!")

root = tk.Tk()
label = tk.Label(root, text="Hello, Tkinter!")
label.pack()

button = tk.Button(root, text="Click Me", command=on_click)
button.pack()

root.mainloop()
```

#### Transpiled Output (Kivy)
```python
from kivy.app import App
from kivy.lang import Builder

KV_LAYOUT = """
BoxLayout:
    orientation: 'vertical'
    padding: 20
    spacing: 10
    Label:
        id: label
        text: 'Hello, Tkinter!'
    Button:
        id: button
        text: 'Click Me'
        on_release: app.on_click()
"""

class ConvertedApp(App):
    def on_click(self):
        print("Button pressed!")

    def build(self):
        return Builder.load_string(KV_LAYOUT)

if __name__ == '__main__':
    ConvertedApp().run()
```

---

## Roadmap and Limitations

This repository is currently a Proof of Concept (PoC) demonstrating AST-based layout transpilation:

- [x] Basic widget extraction (`Label`, `Button`, `Entry`)
- [x] Basic geometry extraction (`.pack()` mapped to vertical `BoxLayout`)
- [x] Callback parameter re-scoping (`def f() -> def f(self)`)
- [ ] Support for `.grid()` to `GridLayout`
- [ ] Nested hierarchies via `tk.Frame`
- [ ] Event extraction for `.bind("<Event>", handler)`

---

## License

This project is licensed under the MIT License.
```