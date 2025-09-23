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
    down = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(VK_F2, 0, 0, 0, None))
    up   = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(VK_F2, 0, KEYEVENTF_KEYUP, 0, None))
    SendInput(1, ctypes.byref(down), ctypes.sizeof(down))
    SendInput(1, ctypes.byref(up),   ctypes.sizeof(up))

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
combo_fired = False

def maybe_fire_combo():
    global combo_fired
    if r2_down and r3_down:
        if not combo_fired:
            combo_fired = True
            print("R2+R3 → F2")
            send_f2()
    else:
        combo_fired = False

# ---- DualSense Parsing (USB & BT) -------------------------------------------
def parse_dualsense(buf: bytes):
    """Gibt (r2_pressed, r3_pressed) zurück. Nimmt Report ID 0x01 an."""
    print(f"Raw report: {buf[:min(20, len(buf))].hex()}")  # Debug: first 20 bytes
    
    if not buf or buf[0] != 0x01:
        print(f"Invalid report ID: {buf[0] if buf else 'None'}")
        return (False, False)

    # USB-Layout (64-Byte Report):
    #   R2 digital: byte 9, bit 3 ; R3: byte 9, bit 7
    # BT-Layout (kürzerer Report):
    #   R2 digital: byte 6, bit 3 ; R3: byte 6, bit 7
    # Quelle / Mapping: nondebug/dualsense. :contentReference[oaicite:2]{index=2}
    if len(buf) >= 11:  # wahrscheinlich USB
        b9 = buf[9]
        r2 = bool((b9 >> 3) & 1)
        r3 = bool((b9 >> 7) & 1)
        print(f"USB mode: byte[9]=0x{b9:02x}, R2={r2}, R3={r3}")
        return (r2, r3)
    elif len(buf) >= 7:  # wahrscheinlich BT
        b6 = buf[6]
        r2 = bool((b6 >> 3) & 1)
        r3 = bool((b6 >> 7) & 1)
        print(f"BT mode: byte[6]=0x{b6:02x}, R2={r2}, R3={r3}")
        return (r2, r3)
    else:
        print(f"Buffer too short: {len(buf)} bytes")
        return (False, False)

# ---- WindowProc: WM_INPUT abfangen ------------------------------------------
def wndproc(hWnd, msg, wParam, lParam):
    global r2_down, r3_down
    if msg == WM_INPUT:
        print(f"WM_INPUT received, wParam=0x{wParam:x}, lParam=0x{lParam:x}")
        
        # Größe bestimmen - use correct header size
        size = ctypes.c_uint(0)
        header_size = ctypes.sizeof(ctypes.c_void_p) * 3  # RAWINPUTHEADER size
        
        result = ctypes.windll.user32.GetRawInputData(
            lParam, RID_INPUT, None, ctypes.byref(size), header_size
        )
        
        if result != 0:
            print(f"GetRawInputData size query failed: {result}")
            return 0
            
        if size.value == 0:
            print("GetRawInputData returned 0 size")
            return 0
            
        print(f"Raw input size: {size.value} bytes")
        
        buf = ctypes.create_string_buffer(size.value)
        actual_size = ctypes.windll.user32.GetRawInputData(
            lParam, RID_INPUT, buf, ctypes.byref(size), header_size
        )
        
        if actual_size != size.value:
            print(f"GetRawInputData failed: expected {size.value}, got {actual_size}")
            return 0
            
        raw = buf.raw
        print(f"RAWINPUT header: {raw[:min(24, len(raw))].hex()}")
        
        # Parse RAWINPUT structure:
        # typedef struct tagRAWINPUT {
        #   RAWINPUTHEADER header;
        #   union {
        #     RAWMOUSE mouse;
        #     RAWKEYBOARD keyboard; 
        #     RAWHID hid;
        #   } data;
        # } RAWINPUT;
        
        if len(raw) >= 24:  # Minimum for RAWINPUTHEADER
            # RAWINPUTHEADER: dwType(4) + dwSize(4) + hDevice(8) + wParam(8)
            dwType = int.from_bytes(raw[0:4], "little")
            dwSize = int.from_bytes(raw[4:8], "little")
            print(f"RAWINPUT: dwType={dwType}, dwSize={dwSize}")
            
            if dwType == 2:  # RIM_TYPEHID
                # RAWHID starts after RAWINPUTHEADER (24 bytes on 64-bit)
                hid_offset = 24
                if len(raw) >= hid_offset + 8:
                    dwSizeHid = int.from_bytes(raw[hid_offset:hid_offset+4], "little")
                    dwCount = int.from_bytes(raw[hid_offset+4:hid_offset+8], "little")
                    print(f"RAWHID: dwSizeHid={dwSizeHid}, dwCount={dwCount}")
                    
                    data_offset = hid_offset + 8
                    data = raw[data_offset:data_offset + dwSizeHid * dwCount]
                    print(f"HID data length: {len(data)} bytes")
                    
                    if dwCount >= 1 and len(data) >= dwSizeHid:
                        report = data[:dwSizeHid]
                        print(f"Processing report of {len(report)} bytes")
                        
                        r2, r3 = parse_dualsense(report)
                        if r2 != r2_down or r3 != r3_down:
                            r2_down, r3_down = r2, r3
                            print(f"State change: R2={r2_down} R3={r3_down}")
                            maybe_fire_combo()
                    else:
                        print(f"Invalid HID data: dwCount={dwCount}, data_len={len(data)}, dwSizeHid={dwSizeHid}")
            else:
                print(f"Not a HID device: dwType={dwType}")
        else:
            print(f"Raw input too short: {len(raw)} bytes")
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

print("RawInput ready (DualSense passiv). Drücke R2+R3 für F2. STRG+C zum Beenden.")
print("Debug mode: Alle Raw Input Nachrichten werden angezeigt.")

# Message Loop
while True:
    win32gui.PumpWaitingMessages()
    win32api.Sleep(1)
