import ctypes
import win32con
import win32gui
import win32api
import win32ui

# ---- WinAPI: SendInput für F2 -----------------------------------------------
SendInput = ctypes.windll.user32.SendInput
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
VK_F2 = 0x71

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ki", KEYBDINPUT)]

def send_f2():
    # Use the working method: keybd_event with scan codes
    try:
        scan_code = win32api.MapVirtualKey(VK_F2, 0)
        ctypes.windll.user32.keybd_event(VK_F2, scan_code, 0, 0)  # Key down
        win32api.Sleep(10)
        ctypes.windll.user32.keybd_event(VK_F2, scan_code, 2, 0)  # Key up
        print("✅ F2 sent successfully")
    except Exception as e:
        print(f"❌ F2 send failed: {e}")

def send_f3():
    # Use the same method as F2 for consistency
    VK_F3 = 0x72
    try:
        scan_code = win32api.MapVirtualKey(VK_F3, 0)
        ctypes.windll.user32.keybd_event(VK_F3, scan_code, 0, 0)  # Key down
        win32api.Sleep(10)
        ctypes.windll.user32.keybd_event(VK_F3, scan_code, 2, 0)  # Key up
        print("✅ F3 sent successfully")
    except Exception as e:
        print(f"❌ F3 send failed: {e}")

# ---- Raw Input Registrierung -------------------------------------------------
RIDEV_INPUTSINK = 0x00000100
RID_INPUT = 0x10000003
WM_INPUT = 0x00FF

# RAWINPUTDEVICE struct
class RAWINPUTDEVICE(ctypes.Structure):
    _fields_ = [("usUsagePage", ctypes.c_ushort),
                ("usUsage", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("hwndTarget", ctypes.c_void_p)]

RegisterRawInputDevices = ctypes.windll.user32.RegisterRawInputDevices

# Flags und Latches
r2_down = False
r3_down = False
l2_down = False
l3_down = False
combo_fired = False

def maybe_fire_combo():
    global combo_fired
    
    if r2_down and r3_down:
        if not combo_fired:
            combo_fired = True
            print("🔥 R2+R3 → F2")
            send_f2()
    elif l2_down and l3_down:
        if not combo_fired:
            combo_fired = True
            print("🔥 L2+L3 → F3")
            send_f3()
    else:
        combo_fired = False

# ---- DualSense Parsing (USB & BT) -------------------------------------------
def parse_dualsense(buf: bytes):
    """Gibt (r2_pressed, r3_pressed, l2_pressed, l3_pressed) zurück. Nimmt Report ID 0x01 an."""
    # Reduced debug output
    if not buf or buf[0] != 0x01:
        print(f"Invalid report ID: {buf[0] if buf else 'None'}")
        return (False, False, False, False)

    if len(buf) >= 10:
        b6 = buf[6] if len(buf) >= 7 else 0
        b8 = buf[8] if len(buf) >= 9 else 0
        b9 = buf[9]  
        
        # R2 detection: byte[9] = 0xff when pressed
        r2 = (b9 == 0xff)
        
        # R3 detection: byte[6].bit7 (0x80)
        r3 = bool((b6 >> 7) & 1)
        
        # L2 detection: byte[8] = 0xff when pressed
        l2 = (b8 == 0xff)
        
        # L3 detection: byte[6].bit6 (0x40)
        l3 = bool((b6 >> 6) & 1)
        
        return (r2, r3, l2, l3)
    
    return (False, False, False, False)

# ---- WindowProc: WM_INPUT abfangen ------------------------------------------
def wndproc(hWnd, msg, wParam, lParam):
    global r2_down, r3_down, l2_down, l3_down
    if msg == WM_INPUT:
        # Größe bestimmen - use correct header size
        size = ctypes.c_uint(0)
        header_size = ctypes.sizeof(ctypes.c_void_p) * 3  # RAWINPUTHEADER size
        
        result = ctypes.windll.user32.GetRawInputData(
            lParam, RID_INPUT, None, ctypes.byref(size), header_size
        )
        
        if result != 0:
            return 0
            
        if size.value == 0:
            return 0
            
        buf = ctypes.create_string_buffer(size.value)
        actual_size = ctypes.windll.user32.GetRawInputData(
            lParam, RID_INPUT, buf, ctypes.byref(size), header_size
        )
        
        if actual_size != size.value:
            return 0
            
        raw = buf.raw
        
        if len(raw) >= 24:  # Minimum for RAWINPUTHEADER
            dwType = int.from_bytes(raw[0:4], "little")
            
            if dwType == 2:  # RIM_TYPEHID
                hid_offset = 24
                if len(raw) >= hid_offset + 8:
                    dwSizeHid = int.from_bytes(raw[hid_offset:hid_offset+4], "little")
                    dwCount = int.from_bytes(raw[hid_offset+4:hid_offset+8], "little")
                    
                    data_offset = hid_offset + 8
                    data = raw[data_offset:data_offset + dwSizeHid * dwCount]
                    
                    if dwCount >= 1 and len(data) >= dwSizeHid:
                        report = data[:dwSizeHid]
                        
                        r2, r3, l2, l3 = parse_dualsense(report)
                        
                        if r2 != r2_down or r3 != r3_down or l2 != l2_down or l3 != l3_down:
                            r2_down, r3_down, l2_down, l3_down = r2, r3, l2, l3
                            print(f"🎮 Buttons: R2={r2_down} R3={r3_down} L2={l2_down} L3={l3_down}")
                            maybe_fire_combo()
    return win32gui.DefWindowProc(hWnd, msg, wParam, lParam)

# ---- Fenster + Message Loop --------------------------------------------------
wc = win32gui.WNDCLASS()
hinst = wc.hInstance = win32api.GetModuleHandle(None)
wc.lpszClassName = "DS_RawInput_Listener"
wc.lpfnWndProc = wndproc
atom = win32gui.RegisterClass(wc)
hwnd = win32gui.CreateWindow(atom, "hidden", 0, 0, 0, 0, 0, 0, 0, hinst, None)

# Gamepad registrieren (UsagePage=0x01 Generic Desktop, Usage=0x05 Game Pad)
rid = RAWINPUTDEVICE(0x01, 0x05, RIDEV_INPUTSINK, hwnd)
if not RegisterRawInputDevices(ctypes.byref(rid), 1, ctypes.sizeof(rid)):
    raise ctypes.WinError()

print("🎮 DualSense Raw Input ready!")
print("📋 Combos: R2+R3 → F2 | L2+L3 → F3")
print("⏹️  Press CTRL+C to exit")

# Message Loop
while True:
    win32gui.PumpWaitingMessages()
    win32api.Sleep(1)
