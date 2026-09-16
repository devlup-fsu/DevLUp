"""
Super Simple Static Site Generator v1.3

by Miles Burkart
"""

import os
import sys
import re
from re import Match
from pathlib import Path
import time
import json

LAYOUT_DIR = '_layout'
TEMPLATE_DIR = '_templates'

HTML_EXTENSION = '.html'

TEMPLATE_PATTERN = re.compile(r"\{\{(.*?)\}\}", re.DOTALL)

COLOR_ERR = '\x1b[31m'
COLOR_OK = '\x1b[32m'
COLOR_RESET = '\x1b[0m'


def get_match_pos(m: Match) -> tuple[int, int]:
    """
    Returns the line and column number where a match was found.
    """
    start = m.start()
    line = m.string.count('\n', 0, start) + 1
    col = start - m.string.rfind('\n', 0, start)
    return line, col


def template(template_path: str, use_template_dir=True, **kwargs) -> str:
    """
    Takes in a path to a template file and returns a formatted string
    where all expressions in that template are evaluated.
    """

    if use_template_dir:
        template_path = TEMPLATE_DIR + '/' + template_path
        if not template_path.endswith(HTML_EXTENSION):
            template_path += HTML_EXTENSION
    
    if not os.path.isfile(template_path):
        raise FileNotFoundError(f'Could not find template at "{template_path}"')

    with open(template_path, 'r') as f:
        template_content = f.read()

    evaluated_parts: list[str] = []

    last_match_end = 0

    for m in re.finditer(TEMPLATE_PATTERN, template_content):
        expression = m.group(1).strip()
        try:
            evaluated_expression = str(eval(expression, kwargs))
        except Exception as e:
            # Generate a trace so the user knows where the error is
            message = str(e)
            if '\n' not in message:
                message += '\n  Trace:'
            line, col = get_match_pos(m)
            raise e.__class__(f'{message}\n    {template_path}, line {line} col {col}')

        match_start, match_end = m.span()

        evaluated_parts.append(template_content[last_match_end:match_start])
        evaluated_parts.append(evaluated_expression)
        last_match_end = match_end

    evaluated_parts.append(template_content[last_match_end:])

    return ''.join(evaluated_parts)


def readjson(file_path: str):
    with open(file_path, 'r') as f:
        return json.load(f)


def main():
    if not os.path.isdir(LAYOUT_DIR):
        print(f'{COLOR_ERR}Error: Could not find layout directory at {LAYOUT_DIR}{COLOR_RESET}', file=sys.stderr)
        return 1

    template_kwargs = {
        'template': template,
        'listdir': os.listdir,
        'json': readjson
    }

    generated_file_count = 0
    start_time = time.time()

    for root, dirs, files in os.walk(LAYOUT_DIR):
        for file in files:
            if not file.endswith(HTML_EXTENSION):
                # Only target HTML files
                continue

            file_path = Path(root) / file

            try:
                file_content = template(str(file_path), use_template_dir=False, **template_kwargs)
            except Exception as e:
                print(f'{COLOR_ERR}Error: {e}{COLOR_RESET}', file=sys.stderr)
                return 2

            write_file_path = Path(*file_path.parts[1:])  # Remove layout directory from start of path
            write_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(write_file_path, 'w') as f:
                f.write(file_content)
                generated_file_count += 1

            print(f'Wrote page to', write_file_path)

    elapsed_time_ms = (time.time() - start_time) * 1000
    print(f'{COLOR_OK}Done! Generated {generated_file_count} files in {elapsed_time_ms:.2f}ms')
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
