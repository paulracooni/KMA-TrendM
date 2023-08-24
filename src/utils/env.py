import os
import dotenv

dotenv.load_dotenv()

class Env:

    @classmethod
    def get(cls, key):
        return os.getenv(key)
