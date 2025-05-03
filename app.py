# this file is the main file of the program

from GUI import App
from GUI import ToggleButton
from GUI.tab_pretask import PreTaskTab, AtomTask
from PIGEON.log import Log
from PIGEON.scheduler import scheduler


if __name__ == "__main__":
    AtomTask.scheduler = scheduler
    ToggleButton.toggle_command = scheduler.submit_task
    app = App()
    Log.log_emit = app.tab_view.log_area
    app.mainloop()
