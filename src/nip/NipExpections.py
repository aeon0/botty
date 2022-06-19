from colorama import init, Fore

class NipError(Exception):
    def __init__(self, error_code: str | int, error_msg: str, additional_info: str = ""):
        self.error_code = error_code
        self.error_msg = error_msg
        self.additional_info = additional_info

    def __str__(self):
        return f"{Fore.RED}{self.error_code}:{Fore.CYAN}{self.error_msg}{':' + self.additional_info if self.additional_info else ''}{Fore.RESET}"

class NipSyntaxError(NipError):
    def __init__(self, error_code: str | int, error_msg: str, expression: str):
        super().__init__(error_code, error_msg, expression)


class NipTranspileError(NipError):
    def __init__(self, error_code: str | int, error_msg: str, expression: str):
        super().__init__(error_code, error_msg, expression)

