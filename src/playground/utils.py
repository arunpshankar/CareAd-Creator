from src.config.logging import logger 
from typing import Any 
import yaml 


def read_api_key(file_path: str) -> Any:
    """
    Reads an API key from a YAML file.

    Parameters:
    - file_path (str): The path to the YAML file containing the API key.

    Returns:
    - Any: The API key retrieved from the file.

    Raises:
    - FileNotFoundError: If the YAML file is not found.
    - yaml.YAMLError: If there is an error parsing the YAML file.
    """
    try:
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
            api_key = config.get('key')
            if api_key is None:
                logger.error(f"No 'key' found in {file_path}")
                raise ValueError(f"No 'key' found in the YAML file at {file_path}")
            # logger.info("API key successfully retrieved.")
            return api_key
    except FileNotFoundError:
        logger.error(f"The file {file_path} was not found.")
        raise
    except yaml.YAMLError as e:
        logger.error("Error parsing YAML file.")
        raise