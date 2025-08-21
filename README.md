# fontra-compile — A Variable Font outline compiler for Fontra

This is for now a work in progress proof of concept.

Initial goals:

- Focus on outlines and (variable) components
- Input: Fontra "backend" objects ([core](https://github.com/fontra/fontra/tree/main/src/fontra/backends) and [rcjk](https://github.com/fontra/fontra-rcjk/blob/main/src/fontra_rcjk/backend_fs.py))
- Initially [`glyf-1`](https://github.com/harfbuzz/boring-expansion-spec/blob/main/glyf1.md)-only
- [Variable Components](https://github.com/harfbuzz/boring-expansion-spec/blob/main/glyf1-varComposites.md)
- [Cubics outlines in glyf](https://github.com/harfbuzz/boring-expansion-spec/blob/main/glyf1-cubicOutlines.md)

Future goals:

- Output regular components when possible
- Add option to convert cubic curves to quadratics
- Add option to convert quadratic curves to cubics
- Add option to flatten variable components
- Add option to build a backwards compatible `glyf-0` table

## Install

- Clone this repository
- `cd` into the cloned repository folder
- Create and activate a virtual environment with Python 3.10 or up
- Install dependencies:

  `pip install -r requirements.txt`

- Install this package:

  `pip install -e .`

## Usage

    $ fontra-compile source.designspace out.ttf
    $ fontra-compile source.designspace out.ttf --glyph-names A,B,C
    $ fontra-compile source.rcjk out.ttf
    $ fontra-compile source.otf out.ttf
    $ fontra-compile source.ttf out.ttf
