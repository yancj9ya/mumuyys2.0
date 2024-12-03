from GUI import App
from GUI import ToggleButton
from PIGEON import Task
from PIGEON import Log


if __name__ == "__main__":
    ToggleButton.toggle_command = Task.execute_task
    app = App()
    Log.log_emit = app.log_area
    app.mainloop()
