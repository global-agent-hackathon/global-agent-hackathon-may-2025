import platform
import subprocess


class OpenApp:
    @staticmethod
    def open(path: str):
        os = platform.system()
        try:
            if os == "Darwin":
                subprocess.run(["open", path])
            elif os == "Windows":
                subprocess.Popen(path)
            else:
                raise Exception(
                    f"Not implemented for {os} operating system WIP")
        except Exception as e:
            raise Exception(
                f"Not able to run the application {path} for os {os} due to {e}")
