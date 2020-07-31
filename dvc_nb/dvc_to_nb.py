import os
from extract import extract_cells
from generate import generate

def main():
    cells = extract_cells()
    generate(cells)

if __name__ == '__main__':
    main()
    