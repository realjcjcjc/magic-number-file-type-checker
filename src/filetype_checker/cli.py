import argparse


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="ftcheck",
        description="Detect file type using magic numbers (scaffold).",
    )

    parser.add_argument("path", nargs="?", help="Path to the file to check.")
    args = parser.parse_args()

    if not args.path:
        print("ftcheck: scaffold ready (detection not implemented).")
        return 0

    print(f"ftcheck: inspects {args.path} (not implemented).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())