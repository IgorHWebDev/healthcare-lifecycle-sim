import streamlit.web.cli as stcli
import sys
from pathlib import Path

if __name__ == "__main__":
    file_path = str(Path(__file__).parent / "run.py")
    sys.argv = ["streamlit", "run", file_path]
    sys.exit(stcli.main()) 