import platform
import os
import subprocess


class CheckPermission:
    @staticmethod
    def checkDiskPermission():
        def hasFullAccess() -> bool:
            system = platform.system()

            if system == "Darwin":
                try:
                    protected_folder = os.path.expanduser("~/Library/Mail")
                    if os.path.exists(protected_folder):
                        _ = os.listdir(protected_folder)
                    print("full disk access is granted!")
                    return True
                except PermissionError:
                    return False
                except Exception:
                    return False
            else:
                return False
        if not hasFullAccess():
            print("Full Disk Access is not granted. Opening Settings...")
            subprocess.run(
                ["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles"])
