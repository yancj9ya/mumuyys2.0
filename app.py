# this file is the main file of the program

from GUI import App
from GUI import ToggleButton
from PIGEON.MidTrans import Task
from PIGEON.log import Log


if __name__ == "__main__":
    ToggleButton.toggle_command = Task.execute_task
    app = App()
    Log.log_emit = app.log_area
    app.mainloop()
