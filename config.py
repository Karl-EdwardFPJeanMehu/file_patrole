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
            "BASELINE_PATH": os.environ.get("PT_BASELINE_PATH", "./baseline"),
            "MONITOR_DIR": os.environ.get("PT_MONITOR_DIR", "./"),
        }

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
