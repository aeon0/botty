from colorama import init, Fore

init()

class BNipError(Exception):
    def __init__(self, error_code: str | int, error_message: str, additional_info: str):
        self.error_code = error_code
        self.error_message = error_message
        self.additional_info = additional_info
    
    def __str__(self):
        self.additional_info = ":" + self.additional_info if self.additional_info else ""
        return f"{Fore.RED}{self.error_code}:{Fore.CYAN}{self.error_message}{Fore.YELLOW}{self.additional_info}{Fore.RESET}"


class BNipSyntaxError(BNipError):
    def __init__(self, error_code: str | int, error_message: str, expression: str):
        super().__init__(error_code, error_message, expression.strip())

class BNipWarning(BNipError):
    def __init__(self, error_code: str | int, error_message: str, expression: str):
        super().__init__(error_code, error_message, expression.strip())
