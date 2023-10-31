import argparse
import pathlib
import typing
from typing import Iterator
from typing import Optional

from PIL import Image as image  # noqa: N813 rename to match pep8 convention
from PIL import ImageOps as image_ops  # noqa: N813


def iter_files(dirpath: pathlib.Path) -> Iterator[pathlib.Path]:
    try:
        for x in dirpath.iterdir():
            yield from iter_files(x)
    except NotADirectoryError:
        yield dirpath


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="instaborder",
        description="Square pictures for instagram",
    )
    parser.add_argument(
        "dir",
        help="directory containing files to square",
        type=pathlib.Path,
    )
    return parser


def process(
    img: image.Image,
    /,
    *,
    size: Optional[tuple[int, int]] = None,
    color: str = "black",
    centering: tuple[float, float] = (0.5, 0.5),
) -> image.Image:
    if size is None:
        size = (max(img.size),) * 2

    return image_ops.pad(
        img,
        size=size,
        color=color,
        centering=centering,
    )


def main() -> None:
    args = get_parser().parse_args()
    directory = typing.cast(pathlib.Path, args.dir)
    images = (
        (x, image.open(x))
        for x in iter_files(directory)
        if x.suffix in (".jpg", ".jpeg")
    )
    images = ((path, process(img)) for path, img in images)
    for path, img in images:
        img.save(path)


if __name__ == "__main__":
    main()
