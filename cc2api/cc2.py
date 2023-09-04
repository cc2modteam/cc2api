"""Run CC2 and read/write to its stdout/stdin """
import time
from io import StringIO
from subprocess import Popen, PIPE
from pathlib import Path
from threading import Thread, Lock


class CC2(Thread):
    def __init__(self, exe: Path, cwd: Path, luafile: Path, *args, **kwargs):
        super().__init__(**kwargs)
        cmdline = [exe]
        if args:
            cmdline.extend(args)
        self.lock = Lock()
        self.proc = Popen(cmdline,
                          stdout=PIPE,
                          encoding="utf-8",
                          shell=False,
                          cwd=cwd)
        self.ready = False
        self.luafile = luafile
        self.buf = StringIO()
        self.counter = time.time()

    def writeline(self, line: str) -> None:
        with self.luafile.open("w") as lua:
            lua.write(line + "\n")

    def run_lua(self, code: str):
        self.ready = False
        chunk = f"""
        g_api_counter = {self.counter}
        if g_api_counter > g_api_counter_last then
            g_api_counter_last = g_api_counter
            local cc2api_st, cc2api_ret = pcall(
            function()                        
            return {code}
            end)
            if cc2api_ret ~= nil then
              print(cc2api_ret)    
            end
        end
        """
        self.counter += 1
        self.writeline(chunk)
        while not self.ready:
            time.sleep(1)
        print(self.buf.getvalue())
        self.buf = StringIO()

    def readline(self) -> str:
        ret = self.proc.stdout.readline()
        ret = ret.strip()
        if "CC2API READY" in ret:
            self.ready = True
        else:
            if ret:
                self.buf.write(ret)

    def run(self) -> None:
        while self.proc.poll() is None:
            self.readline()
            time.sleep(0.05)
