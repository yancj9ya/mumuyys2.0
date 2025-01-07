import json


class Config:
    config_instance = {}

    def __init__(self, file_path):
        self.file_path = file_path
        self.json = self.load_config(self.file_path)
        self.config_instance[file_path.split("/")[-1]] = self

    @classmethod
    def save_all_config(cls):
        for config in cls.config_instance.values():
            config.save_config(config.file_path, config.json)

    def get(self, key, default=None):
        if key in self.json:
            return self.json[key]
        else:
            return default

    def load_config(self, config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file {config_file} not found.")
            return {}

    def save_config(self, config_file, data):
        try:
            with open(config_file, "w", encoding="utf-8") as f:
                print(f"Saving config file {config_file}...")
                json.dump(data, f, ensure_ascii=False, indent=4)
        except FileNotFoundError:
            print(f"Config file {config_file} not found.")

    def __getitem__(self, key):
        return self.json[key]

    def __setitem__(self, key, value):
        self.json[key] = value

    def __delitem__(self, key):
        del self.json[key]

    def __iter__(self):
        return iter(self.json.items())

    def __del__(self):
        print("Exiting config...")
        try:
            self.save_config(self.file_path, self.json)
        except:
            print("Error saving config file.")
            pass


setting = Config("PIGEON/config/setting.json")
task_option = Config("PIGEON/config/task_option.json")
