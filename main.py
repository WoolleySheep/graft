import graft
import logging_configuration

if __name__ == "__main__":
    logging_configuration.configure_logging()
    graft.run_gui()
