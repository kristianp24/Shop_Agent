from dotenv import load_dotenv
from costum_env_utils import doublecheck_env

def check_env_variables():
    load_dotenv()

    # Check and print results
    doublecheck_env("example.env")