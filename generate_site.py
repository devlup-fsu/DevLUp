"""
Super Simple Static Site Generator v1.0

by Miles Burkart
"""

import os
import sys
import re
from pathlib import Path

LAYOUT_DIR = '_layout'
TEMPLATE_DIR = '_templates'

HTML_EXTENSION = '.html'

TEMPLATE_PATTERN = re.compile(r"\{\{(.*?)\}\}", re.DOTALL)


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
        raise FileNotFoundError(f'Could not find template at {template_path}')

    with open(template_path, 'r') as f:
        template_content = f.read()

    evaluated_parts: list[str] = []

    last_match_end = 0

    for m in re.finditer(TEMPLATE_PATTERN, template_content):
        expression = m.group(1).strip()
        evaluated_expression = str(eval(expression, kwargs))
        match_start, match_end = m.span()

        evaluated_parts.append(template_content[last_match_end:match_start])
        evaluated_parts.append(evaluated_expression)
        last_match_end = match_end

    evaluated_parts.append(template_content[last_match_end:])

    return ''.join(evaluated_parts)


def main():
    if not os.path.isdir(LAYOUT_DIR):
        print(f'Error: Could not find layout directory at {LAYOUT_DIR}', file=sys.stderr)
        return 1

    for root, dirs, files in os.walk(LAYOUT_DIR):
        for file in files:
            if not file.endswith(HTML_EXTENSION):
                # Only target HTML files
                continue

            file_path = Path(root) / file

            try:
                file_content = template(str(file_path), use_template_dir=False, template=template)
            except FileNotFoundError as e:
                print('Error:', e, file=sys.stderr)
                return 2

            write_file_path = Path(*file_path.parts[1:])  # Remove layout directory from start of path
            with open(write_file_path, 'w') as f:
                f.write(file_content)

            print(f'Wrote page to', write_file_path)

    print('Done!')
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
