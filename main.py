""" main.py

BLDC Inverter GUI

This is a simple GUI for controlling a BLDC inverter.
It allows the user to set the duty cycle and frequency of the inverter.

This file is the main entry point for the application.
It initializes the application and starts the main loop.
    
@Author: Philipp Eilmann
@copyright: 2025 Philipp Eilmann
"""

__version__ = "0.0.2"

import logging
from moduls.app import App


if __name__ == "__main__":
    """ Main function
    """
    logging.basicConfig(level=logging.INFO, 
                        format='%(name)-30s - %(levelname)-8s - %(message)s')
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
    
