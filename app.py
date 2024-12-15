# this file is the main file of the program

from GUI import App
from GUI import ToggleButton
from GUI.tab_pretask import PreTaskTab, AtomTask
from PIGEON.MidTrans import Task
from PIGEON.log import Log
from PIGEON.taskmanager import taskManager
from PIGEON.scheduler import scheduler


if __name__ == "__main__":
    AtomTask.scheduler = scheduler
    ToggleButton.toggle_command = scheduler.submit_task
    app = App()
    Log.log_emit = app.log_area
    app.mainloop()
