import os
import shutil

from cli.context import Context


class Postprocessor:
    def process(self, ctx: Context):
        if os.path.exists(ctx.sonar_scanner_path):
            shutil.rmtree(ctx.sonar_scanner_path)
