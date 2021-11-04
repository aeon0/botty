from keyboard._winkeyboard import CallNextHookEx, LowLevelKeyboardProc, GetModuleHandleW, SetWindowsHookEx, UnhookWindowsHookEx, GetMessage, TranslateMessage, DispatchMessage, DWORD, c_int, LPMSG
import atexit

LLKHF_INJECTED = 0x00000010
LLMHF_INJECTED = 0x00000001

def remove_key_flags():
    def low_level_handler(nCode, wParam, lParam):
        lParam.contents.flags &= ~LLKHF_INJECTED
        lParam.contents.flags &= ~LLMHF_INJECTED
        return CallNextHookEx(None, nCode, wParam, lParam)

    WH_KEYBOARD_LL = c_int(13)
    keyboard_callback = LowLevelKeyboardProc(low_level_handler)
    handle =  GetModuleHandleW(None)
    thread_id = DWORD(0)
    keyboard_hook = SetWindowsHookEx(WH_KEYBOARD_LL, keyboard_callback, handle, thread_id)
    atexit.register(UnhookWindowsHookEx, keyboard_callback)

if __name__ == "__main__":
    remove_key_flags()
    msg = LPMSG()
    while not GetMessage(msg, 0, 0, 0):
        TranslateMessage(msg)
        DispatchMessage(msg)
