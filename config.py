import os


class Config:
    # Creates a new config object

    _instance = None

    _valid_monitor_file_types = ["txt"]

    _verbose_mode = False

    _dev_mode = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def get_valid_monitor_file_types(self):
        return self._valid_monitor_file_types

    def __init__(self):

        self.config: dict = {
            "PT_BASELINE_PATH": os.environ.get("PT_BASELINE_PATH", "./baseline"),
            "PT_MONITOR_DIRS": os.environ.get(
                "PT_MONITOR_DIRS", "./"
            ),
        }
        self.config["PT_IGNORED_DIRS"] = os.environ.get(
            "PT_IGNORED_DIRS",
            f"{os.path.dirname(self.config['PT_BASELINE_PATH'])}, .git",
        )

    def get(self, key: str) -> str:
        # Returns the value of the specified key
        # if not it throws an error
        if key not in self.config:
            if key not in os.environ:
                print(f"configs: {self.config}")
                raise KeyError(f"Config key,'{key}', not found.")

            else:
                self.config[key] = os.environ.get(key)

        return self.config.get(key) or ""

    def set(self, key, value):
        try:
            os.environ[key] = value
            self.config[key] = value
        except Exception as e:
            print(f"Error {e}")
            raise

    def exists(self, key):
        """Checks if the specified key exists in the config"""
        if key not in self.config or self.config[key] is None:
            return False
        else:
            return True

    def enable_verbose_mode(self):
        self._verbose_mode = True

    def is_verbose_mode(self):
        return self._verbose_mode 

    def enable_dev_mode(self):
        """ Sets program to dev mode """
        self._dev_mode = True

    def is_dev_mode(self):
        """ Checks whether programming is running in dev mode """
        return self._dev_mode
