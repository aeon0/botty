from mouse._winmouse import CallNextHookEx, NULL, c_int, LowLevelMouseProc, SetWindowsHookEx, UnhookWindowsHookEx, LPMSG, GetMessage, TranslateMessage, DispatchMessage
import atexit

LLKHF_INJECTED = 0x00000010
LLMHF_INJECTED = 0x00000001

def remove_mouse_flag():
    def low_level_mouse_handler(nCode, wParam, lParam):
        lParam.contents.flags &= ~LLKHF_INJECTED
        lParam.contents.flags &= ~LLMHF_INJECTED
        return CallNextHookEx(NULL, nCode, wParam, lParam)

    WH_MOUSE_LL = c_int(14)
    mouse_callback = LowLevelMouseProc(low_level_mouse_handler)
    mouse_hook = SetWindowsHookEx(WH_MOUSE_LL, mouse_callback, NULL, NULL)
    atexit.register(UnhookWindowsHookEx, mouse_callback)

if __name__ == "__main__":
    remove_mouse_flag()
    msg = LPMSG()
    while not GetMessage(msg, 0, 0, 0):
        TranslateMessage(msg)
        DispatchMessage(msg)
