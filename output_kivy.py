from kivy.app import App
from kivy.lang import Builder

KV_LAYOUT = """
BoxLayout:
    padding: 20
    spacing: 10
    orientation: 'vertical'
    BoxLayout:
        id: header_frame
        orientation: 'vertical'
        Label:
            id: title_label
            text: 'Create a New Account'
    GridLayout:
        id: form_frame
        cols: 2
        Label:
            id: username_label
            text: 'Username:'
        TextInput:
            id: username_entry
            on_text_validate: app.submit_form()
        Label:
            id: password_label
            text: 'Password:'
        TextInput:
            id: password_entry
            on_text_validate: app.submit_form()
    GridLayout:
        id: action_frame
        cols: 2
        Button:
            id: submit_btn
            text: 'Submit'
            on_release: app.submit_form()
            # Unsupported event '<Enter>': app.on_hover()
        Button:
            id: clear_btn
            text: 'Clear'
            on_press: app.clear_form()
"""

class ConvertedApp(App):
    def submit_form(self, event=None, *args):
        print('Form submitted successfully!')

    def clear_form(self, event=None, *args):
        print('Form fields cleared.')

    def on_hover(self, event=None, *args):
        print('Hovering over submit button.')

    def build(self):
        return Builder.load_string(KV_LAYOUT)

if __name__ == '__main__':
    ConvertedApp().run()