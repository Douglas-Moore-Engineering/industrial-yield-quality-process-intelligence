"""Execute the bounded review notebooks with fresh kernels; retain outputs."""
from pathlib import Path
import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]

def main():
    paths = sorted((ROOT / 'notebooks').glob('[0-9][0-9]_*.ipynb'))
    if not paths:
        raise SystemExit('No review notebooks found')
    for path in paths:
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        NotebookClient(notebook, timeout=120, kernel_name='python3',
                       resources={'metadata': {'path': str(ROOT)}}).execute()
        nbformat.write(notebook, path)
        print(f'PASS: {path.relative_to(ROOT)}')

if __name__ == '__main__':
    main()
