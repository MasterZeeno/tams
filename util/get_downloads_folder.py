import os
import platform
from pathlib import Path
from typing import Optional

def get_downloads_folder(path: Optional[str] = None) -> str:
    if path:
        os.makedirs(path, exist_ok=True)
        return path

    dir_name = "Downloads"
    system = platform.system().lower()
    platform_str = platform.platform().lower()

    # Android (Termux or others)
    if "android" in platform_str:
        storage = "storage"
        for dl_base in ("/sdcard", f"/{storage}/emulated/0", storage):
            for base in (dir_name[:i].lower() for i in (len(dir_name), -1)):
                dl_dir = (
                    Path(dl_base) / base if dl_base.startswith("/")
                    else Path.home() / dl_base / base
                )
                if dl_dir.exists():
                    return str(dl_dir)
        return str(Path.home() / storage / dir_name)  # fallback

    # Windows
    elif "windows" in system:
        import ctypes.wintypes
        CSIDL_PERSONAL = 0x0005
        SHGFP_TYPE_CURRENT = 0

        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        return os.path.join(buf.value, dir_name)

    # macOS
    elif "darwin" in system:
        return str(Path.home() / dir_name)

    # Linux
    elif "linux" in system:
        xdg_config = Path.home() / ".config/user-dirs.dirs"
        if xdg_config.exists():
            with open(xdg_config) as f:
                for line in f:
                    if "XDG_DOWNLOAD_DIR" in line:
                        download_path = line.split('=')[1].strip().strip('"')
                        return download_path.replace("$HOME", str(Path.home()))
        return str(Path.home() / dir_name)

    # Fallback
    return str(Path.home() / dir_name)