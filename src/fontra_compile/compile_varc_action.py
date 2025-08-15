import os
import pathlib
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import AsyncGenerator

from fontra.core.protocols import ReadableFontBackend
from fontra.workflow.actions import OutputProcessorProtocol, registerOutputAction

from .builder import Builder


@registerOutputAction("compile-varc")
@dataclass(kw_only=True)
class FontraCompileAction:
    destination: str
    input: ReadableFontBackend | None = field(init=False, default=None)
    subroutinize: bool = True
    useExtendedGvar: bool = False

    @asynccontextmanager
    async def connect(
        self, input: ReadableFontBackend
    ) -> AsyncGenerator[ReadableFontBackend | OutputProcessorProtocol, None]:
        self.input = input
        try:
            yield self
        finally:
            self.input = None

    async def process(
        self, outputDir: os.PathLike = pathlib.Path(), *, continueOnError=False
    ) -> None:
        outputDir = pathlib.Path(outputDir)
        outputFontPath = outputDir / self.destination
        assert self.input is not None
        builder = Builder(
            reader=self.input,
            buildCFF2=outputFontPath.suffix.lower() == ".otf",
            subroutinize=self.subroutinize,
            useExtendedGvar=self.useExtendedGvar,
        )
        await builder.setup()
        ttFont = await builder.build()
        ttFont.save(outputFontPath)
