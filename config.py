import os


class Config:
    # Creates a new config object

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # config_dir = os.path.dirname(os.path.abspath(__file__))
        # root_dir = os.path.dirname(__file__)

        self.config: dict = {
            "PT_BASELINE_PATH": os.environ.get("PT_BASELINE_PATH", "./baseline"),
            "PT_MONITOR_DIRS": os.environ.get(
                "PT_MONITOR_DIRS", "./test_dir,./other_test_dir/"
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
        os.environ[key] = value
        self.config[key] = value

    def exists(self, key):
        """Checks if the specified key exists in the config"""
        if key not in self.config or self.config[key] is None:
            return False
        else:
            return True
