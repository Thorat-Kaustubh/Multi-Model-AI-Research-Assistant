import subprocess
import os

with open("test_results.txt", "w", encoding="utf-8") as f:
    process = subprocess.Popen(
        [r".\.venv\Scripts\python.exe", "deep_research_test.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8"
    )
    for line in process.stdout:
        print(line, end="")
        f.write(line)
    process.wait()
