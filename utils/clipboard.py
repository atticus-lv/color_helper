import subprocess
import bpy
import sys
import os

TEMP_DIR = ''


def get_dir():
    global TEMP_DIR
    if TEMP_DIR == '':
        TEMP_DIR = os.path.join(os.path.expanduser('~'), 'color_helper_temp')
        if not "color_helper_temp" in os.listdir(os.path.expanduser('~')):
            os.makedirs(TEMP_DIR)

    return TEMP_DIR


class Clipboard():

    def __init__(self, file_urls=None):
        if sys.platform not in {'win32', 'darwin'}:
            raise EnvironmentError

    # mac
    def get_osascript_args(self, commands):
        args = ["osascript"]
        for command in commands:
            args += ["-e", command]
        return args

    # win
    def get_args(self, script):
        powershell_args = [
            os.path.join(
                os.getenv("SystemRoot"),
                "System32",
                "WindowsPowerShell",
                "v1.0",
                "powershell.exe",
            ),
            "-NoProfile",
            "-NoLogo",
            "-NonInteractive",
            "-WindowStyle",
            "Hidden",
        ]
        script = (
                "$OutputEncoding = "
                "[System.Console]::OutputEncoding = "
                "[System.Console]::InputEncoding = "
                "[System.Text.Encoding]::UTF8; "
                + "$PSDefaultParameterValues['*:Encoding'] = 'utf8'; "
                + script
        )
        args = powershell_args + ["& { " + script + " }"]
        return args

    def execute_powershell(self, script):
        parms = {
            'args': self.get_args(script),
            'encoding': 'utf-8',
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
        }
        popen = subprocess.Popen(**parms)
        stdout, stderr = popen.communicate()
        return popen, stdout, stderr

    def pull_image_from_clipboard(self, save_name='ch_cache_image.png'):
        filepath = os.path.join(get_dir(), save_name)
        if sys.platform == 'win32':
            image_script = (
                "$image = Get-Clipboard -Format Image; "
                f"if ($image) {{ $image.Save('{filepath}'); Write-Output 0 }}"
            )

            popen, stdout, stderr = self.execute_powershell(image_script)
        elif sys.platform == 'darwin':
            commands = [
                "set pastedImage to "
                f'(open for access POSIX file "{filepath}" with write permission)',
                "try",
                "    write (the clipboard as «class PNGf») to pastedImage",
                "end try",
                "close access pastedImage",
            ]
            popen = subprocess.Popen(self.get_osascript_args(commands))
            stdout, stderr = popen.communicate()

        # print(filepath, stdout, stderr)
        return filepath
