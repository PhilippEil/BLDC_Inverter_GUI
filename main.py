"""main.py

    BLDC Inverter GUI
    
    This file init the Program.
    
    
"""
__author__ = "Philipp Eilmann"
__version__ = "0.0.1"

import logging
from moduls.app import App


if __name__ == "__main__":
    """ Main function
    """
    logging.basicConfig(level=logging.INFO)
    app = App()
    try:
        app.run()
    except KeyboardInterrupt:  
        logging.info("Exit")
    except Exception as e:
        logging.error(f"Error: {e}")
        logging.info("Exit")
    finally:
        app.cleanUp()
    
