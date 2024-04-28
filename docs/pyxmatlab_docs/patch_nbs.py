"""Patch notebooks."""

from pathlib import Path
from textwrap import dedent

from nbformat import NO_CONVERT, NotebookNode, read, write

SRC = "source"
"""Cell source key."""
CODE = "code"
"""Code cell type."""


def main():  # noqa: D103
    patch_nbs()


def patch_nbs():
    """Patch notebooks.

    Patch Thebe buttons in. Insert `parameters` tags to the first code cell. Insert
    `hide-input` tags to code cells.
    """
    for path in Path("docs").rglob("*.ipynb"):
        nb: NotebookNode = read(path, NO_CONVERT)  # type: ignore  # pyright 1.1.348,  # nbformat: 5.9.2
        # ? Patch the first code cell
        code_cells = ((i, c) for i, c in enumerate(nb.cells) if c.cell_type == CODE)
        i, first = next(code_cells)
        nb.cells[i][SRC] = patch(
            first.get(SRC, ""),
            """
            from pyxmatlab_docs.nbs import init

            paths = init()
            """,
        )
        # ? Insert tags to first code cell
        nb.cells[i] = insert_tag(first, ["hide-input", "parameters"])
        # ? Insert tags to remaining code cells
        for i, cell in code_cells:
            nb.cells[i] = insert_tag(cell, ["hide-input"])
        # ? Write the notebook back
        write(nb, path)


def insert_tag(cell: NotebookNode, tags_to_insert: list[str]) -> NotebookNode:
    """Insert tags to a notebook cell.

    Parameters
    ----------
    cell
        Notebook cell to insert tags to.
    tags_to_insert
        Tags to insert.

    References
    ----------
    - [Jupyter Book: Add tags using Python code](https://jupyterbook.org/en/stable/content/metadata.html#add-tags-using-python-code)
    """
    tags = cell.get("metadata", {}).get("tags", [])
    cell["metadata"]["tags"] = sorted(set(tags) | set(tags_to_insert))
    return cell


def patch(src: str, content: str, end: str = "\n\n") -> str:
    """Prepend source lines to cell source if not there already.

    Parameters
    ----------
    src
        Source to prepend to.
    content
        Content to prepend.
    end
        Ending to append to the content.
    """
    content = dedent(content).strip()
    return src if src.startswith(content) else f"{content}{end}{src}"


if __name__ == "__main__":
    main()
