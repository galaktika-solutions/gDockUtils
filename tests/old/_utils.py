import subprocess
import tempfile


class RecordingPopen(subprocess.Popen):
    tempfile_pairs = []

    @classmethod
    def clear(cls):
        for a, b in cls.tempfile_pairs:
            a.close(), b.close()
        cls.tempfile_pairs = []

    def __init__(self, *args, **kwargs):
        stdout = tempfile.TemporaryFile(mode="w+", encoding="utf-8")
        stderr = tempfile.TemporaryFile(mode="w+", encoding="utf-8")
        self.tempfile_pairs.append((stdout, stderr))
        kwargs["stdout"], kwargs["stderr"] = stdout, stderr
        super().__init__(*args, **kwargs)
