"""PyInstaller entrypoint — uses absolute imports so the frozen binary
works without relative-import support."""
from idle_daemon.__main__ import main

if __name__ == "__main__":
    main()
