import ast
import textwrap

# ==========================================
# [1] Tkinter Python Code (Input)
# ==========================================
TKINTER_CODE = """
import tkinter as tk

def submit_action():
    print("Button was clicked!")

root = tk.Tk()
root.title("AST Transpiler App")

my_label = tk.Label(root, text="Welcome to the Tkinter to Kivy transpiler!")
my_label.pack()

my_button = tk.Button(root, text="Submit", command=submit_action)
my_button.pack()

root.mainloop()
"""


# ==========================================
# [2] AST NodeVisitor (Extractor)
# ==========================================
class TkinterASTVisitor(ast.NodeVisitor):
    """
    Traverses the Python AST to extract Tkinter widget declarations, 
    their properties (geometry, bindings), and callback functions.
    """
    def __init__(self):
        self.root_widget = None
        self.widgets = {}      # Format: {var_name: {type, parent, props, geometry}}
        self.functions = []    # Stores AST nodes for functions

    def visit_FunctionDef(self, node):
        # Extract callback functions so we can port them to Kivy App methods
        self.functions.append(node)
        self.generic_visit(node)

    def visit_Assign(self, node):
        # Check if the assignment is a Tkinter widget instantiation (e.g., tk.Label)
        if isinstance(node.value, ast.Call) and self._is_tkinter_call(node.value):
            call = node.value
            widget_type = call.func.attr
            
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id
                    
                    if widget_type == 'Tk':
                        self.root_widget = var_name
                    else:
                        parent = call.args[0].id if call.args else None
                        props = {kw.arg: self._extract_value(kw.value) for kw in call.keywords}
                        
                        self.widgets[var_name] = {
                            'type': widget_type,
                            'parent': parent,
                            'props': props,
                            'geom': None
                        }
        self.generic_visit(node)

    def visit_Expr(self, node):
        # Extract Geometry managers (e.g. my_label.pack())
        if isinstance(node.value, ast.Call):
            call = node.value
            if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name):
                var_name = call.func.value.id
                method = call.func.attr
                
                # Check if it's a geometry manager call
                if var_name in self.widgets and method in ['pack', 'grid', 'place']:
                    self.widgets[var_name]['geom'] = method
                    
        self.generic_visit(node)

    def _is_tkinter_call(self, call):
        if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name):
            return call.func.value.id in ('tk', 'tkinter')
        return False

    def _extract_value(self, node):
        if isinstance(node, ast.Constant):
            return node.value # Returns strings, ints, etc.
        elif isinstance(node, ast.Name):
            return node.id    # Returns variable/function names
        return None


# ==========================================
# [3] Code Generator (Kivy / .kv emitter)
# ==========================================
class KivyCodeGenerator:
    """
    Takes the extracted metadata from the AST Visitor and emits 
    pure Kivy Python and KV layout strings.
    """
    def __init__(self, visitor):
        self.visitor = visitor
        
        # Mapping simple Tkinter widgets to Kivy equivalents
        self.widget_map = {
            'Label': 'Label',
            'Button': 'Button',
            'Entry': 'TextInput'
        }

    def generate(self):
        kv_code = self._generate_kv()
        py_code = self._generate_py(kv_code)
        return py_code, kv_code

    def _generate_kv(self):
        # We default to a vertical BoxLayout since .pack() was heavily used
        kv_lines = [
            "BoxLayout:", 
            "    orientation: 'vertical'",
            "    padding: 20",
            "    spacing: 10"
        ]

        for name, data in self.visitor.widgets.items():
            if not data['geom']: continue # Only render widgets that were packed/placed

            kivy_type = self.widget_map.get(data['type'], 'Widget')
            kv_lines.append(f"    {kivy_type}:")
            kv_lines.append(f"        id: {name}")

            for prop, val in data['props'].items():
                if prop == 'text':
                    kv_lines.append(f"        text: {repr(val)}")
                elif prop == 'command':
                    # Bind Tkinter command to Kivy on_release event
                    kv_lines.append(f"        on_release: app.{val}()")
                    
        return "\n".join(kv_lines)

    def _generate_py(self, kv_code):
        py_lines = [
            "from kivy.app import App",
            "from kivy.lang import Builder",
            "",
            'KV_LAYOUT = """\n' + kv_code + '\n"""',
            "",
            "class ConvertedApp(App):"
        ]

        # Port extracted Tkinter functions into Kivy App methods
        has_methods = False
        for func_node in self.visitor.functions:
            has_methods = True
            
            # Inject 'self' argument into the AST node signature for class method context
            if not any(arg.arg == 'self' for arg in func_node.args.args):
                func_node.args.args.insert(0, ast.arg(arg='self'))
                
            # Unparse AST back to string (Requires Python 3.9+)
            method_code = ast.unparse(func_node)
            py_lines.extend(textwrap.indent(method_code, "    ").split('\n'))
            py_lines.append("")

        if not has_methods:
            py_lines.append("    pass")

        # Build method loading the KV layout
        py_lines.append("    def build(self):")
        py_lines.append("        return Builder.load_string(KV_LAYOUT)")
        py_lines.append("")
        py_lines.append("if __name__ == '__main__':")
        py_lines.append("    ConvertedApp().run()")

        return "\n".join(py_lines)


# ==========================================
# [4] Pipeline Execution (Bringing it together)
# ==========================================
if __name__ == "__main__":
    print("--- 1. Original Tkinter Code ---")
    print(TKINTER_CODE.strip())
    print("\n" + "="*50 + "\n")

    # Step A: [Python ast.parse]
    parsed_ast = ast.parse(TKINTER_CODE)

    # Step B: [AST NodeVisitor]
    visitor = TkinterASTVisitor()
    visitor.visit(parsed_ast)

    # Step C: [Code Generator]
    generator = KivyCodeGenerator(visitor)
    kivy_py, kivy_kv = generator.generate()

    print("--- 2. Generated Kivy Layout (.kv logic) ---")
    print(kivy_kv)
    print("\n" + "="*50 + "\n")

    print("--- 3. Generated Kivy Python Application ---")
    print(kivy_py)