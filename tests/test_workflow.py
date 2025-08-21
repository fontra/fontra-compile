from __future__ import annotations

import pathlib
import random
import subprocess
from dataclasses import dataclass, replace

import pytest
import yaml
from fontra.core.classes import VariableGlyph
from fontra.workflow.actions import registerFilterAction
from fontra.workflow.actions.base import BaseFilter
from fontra.workflow.workflow import Workflow
from test_compile import cleanupTTX

testDir = pathlib.Path(__file__).resolve().parent
dataDir = testDir / "data"


@registerFilterAction("randomize-glyph-source-order")
@dataclass(kw_only=True)
class RandomizeGlyphSourceOrder(BaseFilter):
    async def processGlyph(self, glyph: VariableGlyph) -> VariableGlyph:
        newSources = list(glyph.sources)
        random.shuffle(newSources)
        return replace(glyph, sources=newSources)


testData = [
    (
        """
steps:
- input: fontra-read
  source: "tests/data/MutatorSans.fontra"
- output: compile-varc
  destination: "output1.ttf"
""",
        "MutatorSans.ttf.ttx",
    ),
    (
        """
steps:
- input: fontra-read
  source: "tests/data/MutatorSans.fontra"
- output: compile-varc
  destination: "output1.otf"
""",
        "MutatorSans.otf.ttx",
    ),
    (
        """
steps:
- input: fontra-read
  source: "tests/data/MutatorSans.fontra"
- filter: convert-to-quadratics
- output: compile-varc
  destination: "output1.ttf"
""",
        "MutatorSans-glyf0.ttf.ttx",
    ),
    (
        """
# Check that we produce the same output regardless of glyph source order.
steps:
- input: fontra-read
  source: "tests/data/MutatorSans.fontra"
- filter: randomize-glyph-source-order
- output: compile-varc
  destination: "output-random-source-order.ttf"
""",
        "MutatorSans.ttf.ttx",
    ),
    (
        """
# Check that we produce the same output regardless of glyph source order.
steps:
- input: fontra-read
  source: "tests/data/MutatorSans.fontra"
- filter: randomize-glyph-source-order
- output: compile-varc
  destination: "output-random-source-order.otf"
""",
        "MutatorSans.otf.ttx",
    ),
    (
        """
# This test font contains two problem cases:
# 1. VG_531A_00 contains a rectangle that has no width in a single source,
#    which uncovered a bug with implied lineto calls with the CFF writer.
# 2. uni3479 (㑹) which uses "asymmetrical" axes, that lead to wrong results
#    in normalized space: https://github.com/fontra/fontra-compile/issues/45
steps:
- input: fontra-read
  source: "tests/data/notosanscjksc.fontra"
- output: compile-varc
  destination: "output.otf"
""",
        "notosanscjksc.otf.ttx",
    ),
    (
        """
steps:
- input: fontra-read
  source: "tests/data/MutatorSansAxisValueLabels.fontra"
- output: compile-fontmake
  destination: "output-fontmake.ttf"
""",
        "MutatorSansAxisValueLabels-fontmake.ttx",
    ),
    (
        """
steps:
- input: fontra-read
  source: "tests/data/MutatorSans.fontra"
- output: compile-fontmake
  options:
    flatten-components:  # no value
  destination: "output-fontmake.ttf"
  addMinimalGaspTable: true
""",
        "MutatorSans-fontmake.ttx",
    ),
    (
        """
steps:
- input: fontra-read
  source: "tests/data/MutatorSans.fontra"
- output: compile-fontmake
  options:
    flatten-components:  # no value
  destination: "output-fontmake.otf"
""",
        "MutatorSans-fontmake-cff2.ttx",
    ),
    (
        """
steps:
- input: fontra-read
  source: "tests/data/MutatorSans.fontra"
- filter: subset-axes
  axisNames: []
- output: compile-fontmake
  options:
    flatten-components:  # no value
  destination: "output-fontmake-static.ttf"
""",
        "MutatorSans-fontmake-static.ttx",
    ),
    (
        """
steps:
- input: fontra-read
  source: "tests/data/MutatorSans.fontra"
- filter: subset-axes
  axisNames: []
- output: compile-fontmake
  options:
    flatten-components:  # no value
  destination: "output-fontmake-static.otf"
""",
        "MutatorSans-fontmake-static-cff.ttx",
    ),
    (
        """
steps:
- input: fontra-read
  source: "tests/data/MutatorSans.fontra"
- output: compile-fontc
  destination: "output-fontc.ttf"
""",
        "MutatorSans-fontc.ttx",
    ),
    (
        """
steps:
- input: fontra-read
  source: "tests/data/MutatorSans.fontra"
- filter: subset-axes
  axisNames: []
- output: compile-fontc
  destination: "output-fontc-static.ttf"
""",
        "MutatorSans-fontc-static.ttx",
    ),
]


@pytest.mark.parametrize("workflowSource, ttxFileName", testData)
async def test_workflow(tmpdir, workflowSource, ttxFileName):
    tmpdir = pathlib.Path(tmpdir)
    config = yaml.safe_load(workflowSource)

    workflow = Workflow(config=config)

    async with workflow.endPoints() as endPoints:
        assert endPoints.endPoint is not None

        for output in endPoints.outputs:
            await output.process(tmpdir)
            ttxPath = dataDir / ttxFileName
            outPath = tmpdir / output.destination
            assert outPath.exists(), outPath
            outTTXPath = tmpdir / (outPath.stem + ".ttx")
            subprocess.run(["ttx", "-o", outTTXPath, outPath], check=True)

            # # Write expected
            # ttxPath.write_text(outTTXPath.read_text())

            ttxLines = cleanupTTX(outTTXPath.read_text())
            expectedLines = cleanupTTX(ttxPath.read_text())
            assert expectedLines == ttxLines, outTTXPath
