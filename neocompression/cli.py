import argparse
from pathlib import Path

from .core import compress_path, decompress_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="NeoCompression - adaptive binary compression container"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    p_compress = subparsers.add_parser("compress", help="Compress file or folder")
    p_compress.add_argument("source", type=str, help="File or directory to compress")
    p_compress.add_argument("output", type=str, help="Output .neo container path")
    p_compress.add_argument(
        "--chunk-bits",
        type=int,
        default=8192,
        help="Chunk size in bits for internal processing",
    )

    p_decompress = subparsers.add_parser("decompress", help="Decompress .neo container")
    p_decompress.add_argument("container", type=str, help="Input .neo container path")
    p_decompress.add_argument(
        "output-dir", type=str, help="Directory to restore original files into"
    )

    args = parser.parse_args()

    if args.command == "compress":
        compress_path(args.source, args.output, chunk_bits=args.chunk_bits)
    elif args.command == "decompress":
        decompress_file(args.container, args.output_dir)


if __name__ == "__main__":
    main()
