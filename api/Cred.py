import os
from typing import Literal

def write_to_env(variables) -> None | Literal['Device already added']:
    with open('.env', 'a'):
        pass  # Create the file if it doesn't exist
    with open('.env', 'r+') as env_file:
        env_content: str = env_file.read()
        key_already_present = False
        for key, value in variables.items():
            if key == 'macadress' or (key not in env_content):
                env_file.write(f"{key}=\"{value}\"\n")
            else:
                key_already_present = True
        if key_already_present:
            return "Device already added"