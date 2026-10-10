import ast
import sys
import os
import textwrap

class TkinterASTVisitor(ast.NodeVisitor):
    def __init__(self):
        self.root_widget = None
        self.widgets = {}
        self.functions = []

    def visit_FunctionDef(self, node):
        self.functions.append(node)
        self.generic_visit(node)

    def visit_Assign(self, node):
        if isinstance(node.value, ast.Call) and self._is_tkinter_call(node.value):
            call = node.value
            widget_type = call.func.attr
            
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id
                    
                    if widget_type == 'Tk':
                        self.root_widget = var_name
                        parent = None
                    else:
                        parent = call.args[0].id if call.args else None
                    
                    props = {kw.arg: self._extract_value(kw.value) for kw in call.keywords}
                    
                    self.widgets[var_name] = {
                        'type': widget_type,
                        'parent': parent,
                        'props': props,
                        'geom': None,
                        'geom_props': {},
                        'bindings': {}
                    }
        self.generic_visit(node)

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call):
            call = node.value
            if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name):
                var_name = call.func.value.id
                method = call.func.attr
                
                if var_name in self.widgets:
                    if method in ['pack', 'grid', 'place']:
                        self.widgets[var_name]['geom'] = method
                        self.widgets[var_name]['geom_props'] = {
                            kw.arg: self._extract_value(kw.value) for kw in call.keywords
                        }
                    elif method == 'bind' and len(call.args) == 2:
                        event_str = self._extract_value(call.args[0])
                        handler = self._extract_value(call.args[1])
                        self.widgets[var_name]['bindings'][event_str] = handler
                        
        self.generic_visit(node)

    def _is_tkinter_call(self, call):
        if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name):
            return call.func.value.id in ('tk', 'tkinter')
        return False

    def _extract_value(self, node):
        if isinstance(node, ast.Constant):
            return node.value 
        elif isinstance(node, ast.Name):
            return node.id    
        return None


class KivyCodeGenerator:
    def __init__(self, visitor):
        self.visitor = visitor
        
        self.widget_map = {
            'Label': 'Label',
            'Button': 'Button',
            'Entry': 'TextInput'
        }
        
        self.event_map = {
            '<Button-1>': 'on_press',
            '<ButtonRelease-1>': 'on_release',
            '<Return>': 'on_text_validate',
            
        }

        self.tree = {}
        for name, data in self.visitor.widgets.items():
            parent = data['parent']
            if parent is not None:
                self.tree.setdefault(parent, []).append(name)

    def generate(self):
        kv_code = self._generate_kv()
        py_code = self._generate_py(kv_code)
        return py_code

    def _generate_kv(self):
        if not self.visitor.root_widget:
            return ""
            
        kv_lines = self._render_node(self.visitor.root_widget, depth=0)
        return "\n".join(kv_lines)

    def _render_node(self, name, depth):
        data = self.visitor.widgets[name]
        lines = []
        indent = "    " * depth
        
        is_container = name in self.tree or data['type'] == 'Tk'
        
        if is_container:
            children = self.tree.get(name, [])
            child_geoms = [self.visitor.widgets[c]['geom'] for c in children if c in self.visitor.widgets]
            
            if 'grid' in child_geoms:
                kivy_type = 'GridLayout'
                max_col = max((self.visitor.widgets[c]['geom_props'].get('column', 0) for c in children), default=0)
                cols = max_col + 1
            else:
                kivy_type = 'BoxLayout'
        else:
            kivy_type = self.widget_map.get(data['type'], 'Widget')
            
        if depth == 0:
            lines.append(f"{kivy_type}:")
        else:
            lines.append(f"{indent}{kivy_type}:")
            lines.append(f"{indent}    id: {name}")

        if is_container:
            if depth == 0:
                lines.append(f"{indent}    padding: 20")
                lines.append(f"{indent}    spacing: 10")
            if kivy_type == 'GridLayout':
                lines.append(f"{indent}    cols: {cols}")
            elif kivy_type == 'BoxLayout':
                lines.append(f"{indent}    orientation: 'vertical'")

        for prop, val in data['props'].items():
            if prop == 'text':
                lines.append(f"{indent}    text: {repr(val)}")
            elif prop == 'command':
                lines.append(f"{indent}    on_release: app.{val}()")
                
        for event, handler in data['bindings'].items():
            kivy_event = self.event_map.get(event)
            if kivy_event:
                lines.append(f"{indent}    {kivy_event}: app.{handler}()")
            else:
                # Comment out unsupported events (like Tkinter hover events) to prevent BuilderException
                lines.append(f"{indent}    # Unsupported event '{event}': app.{handler}()")

        if is_container:
            for child in self.tree.get(name, []):
                if self.visitor.widgets[child]['geom'] or self.visitor.widgets[child]['type'] == 'Frame':
                    lines.extend(self._render_node(child, depth + 1))
                    
        return lines

    def _generate_py(self, kv_code):
        py_lines = [
            "from kivy.app import App",
            "from kivy.lang import Builder",
            "",
            'KV_LAYOUT = """\n' + kv_code + '\n"""',
            "",
            "class ConvertedApp(App):"
        ]

        has_methods = False
        for func_node in self.visitor.functions:
            has_methods = True
            
            if not any(arg.arg == 'self' for arg in func_node.args.args):
                func_node.args.args.insert(0, ast.arg(arg='self'))
                
            func_node.args.vararg = ast.arg(arg='args')
                
            method_code = ast.unparse(func_node)
            py_lines.extend(textwrap.indent(method_code, "    ").split('\n'))
            py_lines.append("")

        if not has_methods:
            py_lines.append("    pass")

        py_lines.append("    def build(self):")
        py_lines.append("        return Builder.load_string(KV_LAYOUT)")
        py_lines.append("")
        py_lines.append("if __name__ == '__main__':")
        py_lines.append("    ConvertedApp().run()")

        return "\n".join(py_lines)


def transpile_file(input_filepath, output_filepath):
    if not os.path.exists(input_filepath):
        print(f"Error: Input file '{input_filepath}' does not exist.")
        sys.exit(1)

    print(f"Reading Tkinter code from: {input_filepath}")
    with open(input_filepath, "r", encoding="utf-8") as f:
        tkinter_source = f.read()

    # 1. Parse AST
    parsed_ast = ast.parse(tkinter_source)

    # 2. Extract layout, widgets, bindings
    visitor = TkinterASTVisitor()
    visitor.visit(parsed_ast)

    # 3. Generate Kivy application code
    generator = KivyCodeGenerator(visitor)
    kivy_py_code = generator.generate()

    # 4. Save to output file
    with open(output_filepath, "w", encoding="utf-8") as f:
        f.write(kivy_py_code)

    print(f"Transpilation successful! Saved Kivy application to: {output_filepath}")


if __name__ == "__main__":
    # Accepts optional CLI arguments: python transpiler.py [input_file] [output_file]
    input_path = sys.argv[1] if len(sys.argv) > 1 else "input_tk.py"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "output_kivy.py"

    transpile_file(input_path, output_path)