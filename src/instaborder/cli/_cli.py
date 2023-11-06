import argparse
import itertools
import pathlib
import sys
import typing
from typing import Iterable
from typing import Iterator
from typing import Optional

from PIL import Image as image  # noqa: N813 rename to match pep8 convention
from PIL import ImageOps as image_ops  # noqa: N813


def iter_files(dirpath: pathlib.Path, all_files=False) -> Iterator[pathlib.Path]:
    try:
        for x in dirpath.iterdir():
            if not all_files and x.name.startswith("."):
                continue
            yield from iter_files(x)
    except NotADirectoryError:
        yield dirpath


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="instaborder",
        description="Square pictures for instagram",
    )
    parser.add_argument(
        "paths",
        help="path to image or directory of images",
        nargs="+",
        type=pathlib.Path,
    )
    parser.add_argument(
        "--recursive",
        "-r",
        dest="recursive",
        action="store_true",
        default=False,
        help="recurse into directories",
    )
    parser.add_argument(
        "--all",
        "-A",
        dest="all_files",
        action="store_true",
        default=False,
        help="include hidden files and directories"
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
    parser = get_parser()
    args = parser.parse_args()
    paths: Iterable[pathlib.Path] = (
        typing.cast(pathlib.Path, x) for x in args.paths
    )

    if args.recursive:
        paths = itertools.chain.from_iterable((
            iter_files(x, all_files=args.all_files)
            for x in paths
        ))
    else:
        paths, clone = itertools.tee(paths, 2)
        for x in clone:
            if x.is_dir():
                print(
                    f"Skipping directory: {x}",
                    file=sys.stderr,
                )
    images: Iterable[tuple[pathlib.Path, image.Image]] = (
        (x, image.open(x))
        for x in paths
        if x.is_file() and x.suffix in (".jpg", ".jpeg")
    )

    images, to_count = itertools.tee(images, 2)
    found = sum(1 for _ in to_count)
    print(f"{found} images found.", file=sys.stderr)
    images = (
        (path, process(img))
        for path, img in images
        if max(img.size) > min(img.size)
    )

    counter = 0
    for path, img in images:
        img.save(path)
        counter += 1
    print(f"{counter} images resized.", file=sys.stderr)


if __name__ == "__main__":
    main()
