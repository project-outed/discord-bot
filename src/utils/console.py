import sys
import datetime
from src.enum.console import ConsoleLevel

class Console:

    RESET = "\033[0m"
    GRAY = "\033[90m"

    @staticmethod
    def _log(message: str, level: ConsoleLevel, module: str = None):
        try:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            name, color = level.value
            
            ts_str = f"{Console.GRAY}[{timestamp}]{Console.RESET}"
            lvl_str = f"{color}{name.ljust(7)}{Console.RESET}"
            mod_str = f"{Console.GRAY}[{module}]{Console.RESET} " if module else ""
            
            output = f"{ts_str} {lvl_str} {mod_str}{message}"
            
            print(output, file=sys.stdout if level != ConsoleLevel.ERROR else sys.stderr)
        except Exception as e:
            print(f"Logger Error: {e}", file=sys.stderr)

    @staticmethod
    def info(message: str, module: str = None):
        Console._log(message, ConsoleLevel.INFO, module)

    @staticmethod 
    def success(message: str, module: str = None):
        Console._log(message, ConsoleLevel.SUCCESS, module)
    
    @staticmethod
    def warning(message: str, module: str = None):
        Console._log(message, ConsoleLevel.WARNING, module)

    @staticmethod
    def error(message: str, module: str = None):
        Console._log(message, ConsoleLevel.ERROR, module)

    @staticmethod
    def debug(message: str, module: str = None):
        Console._log(message, ConsoleLevel.DEBUG, module)

    @staticmethod
    def log(message: str, module: str = None):
        Console._log(message, ConsoleLevel.DEFAULT, module)
