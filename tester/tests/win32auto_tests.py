from time import sleep
from pywinauto.keyboard import send_keys


def list_windows_test():
    list_windows()


def print_windows_info(backend='uia'):
    app = Application(backend=backend).connect(process=3220)

    # Access both windows by index
    window1 = app.window(found_index=0)
    window2 = app.window(found_index=1)

    # Print control identifiers for each
    print("Window 1 controls:")
    window1.print_control_identifiers()

    print("\nWindow 2 controls:")
    window2.print_control_identifiers()

    elements = find_elements(backend='uia', process=3220)

    for i, element in enumerate(elements):
        print(f"Element {i}:")
        print(f"  Title: \'{element.name}\'")
        print(f"  Class Name: \'{element.class_name}\'")
        print(f"  Control Type: {element.control_type}")
        print(f"  Automation ID: {element.automation_id}")
        print(f"  Rect: {element.rectangle}")


# Connect to the application
app = Application(backend="win32").connect(process=3220)
print('Connection successful.')
# Target the blank window by its class name and rectangle
client = app.window(found_index=0)
print('Window connection successful.')
ctrl = client.child_window(title="Chrome Legacy Window", class_name="Chrome_RenderWidgetHostHWND")

app = Application(backend='win32').connect(process=3220)

# Target the window
window = app.window(found_index=0)

# Bring the window into focus
window.set_focus()

# Press and hold the 'Shift' key (you can adjust the hold duration)
sleep(3)
send_keys('3{down}')  # Shift key down
sleep(2)  # Hold for 2 seconds (adjust as needed)
send_keys('3{up}')  # Release the Shift key
