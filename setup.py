from cx_Freeze import setup, Executable

executables = [Executable("SysTrayIcon.py", base="Win32GUI", icon="favicon.ico")]

packages = [
    "idna",
    "requests",
    "os",
    "schedule",
    "time",
    "dotenv",
    "smtplib",
    "email",
    "sys",
    "pystray",
    "PIL",
]
options = {
    "build_exe": {
        "packages": packages,
        "include_files": [".env", "favicon.ico"],
    },
}

setup(
    name="Daily Meme",
    options=options,
    version="1.0.1",
    description="Sends Out Daily Memes",
    executables=executables,
)
