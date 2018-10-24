import fileinput
import os


class PrettyPrint:
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    BLUE = '\033[94m'
    GREEN = '\033[92m'
    PINK = '\033[95m'
    RED = '\033[91m'
    YELLOW = '\033[93m'

    @staticmethod
    def msg_blue(s):
        print('{}==>{} {}{}{}'.format(
            PrettyPrint.BLUE, PrettyPrint.END,
            PrettyPrint.BOLD, s, PrettyPrint.END))

    @staticmethod
    def print_green(s):
        print('{}{}{}'.format(PrettyPrint.GREEN, s, PrettyPrint.END))


def get_input(msg: str) -> str:
    name = None
    while not name:
        name = input('{} '.format(msg))
    return name


def yes_or_no(question):
    while True:
        answer = input(question + ' (y/n): ').lower().strip()
        if answer in ('y', 'yes', 'n', 'no'):
            return answer in ('y', 'yes')
        else:
            print('You must answer yes or no.')


def replace_text(filename: str, text_to_search: str, replacement_text: str):
    with fileinput.FileInput(filename, inplace=True) as file:
        for line in file:
            print(line.replace(text_to_search, replacement_text), end='')


def add_after_variable(filename: str, var: str, text_to_add: str):
    """
    Adds the desired text after a certain variable.
    """
    symbols_open = ('(', '[', '{')
    symbols_close = (')', ']', '}')

    with fileinput.FileInput(filename, inplace=True) as file:
        stack = []
        found_var = False
        for line in file:
            if '{} = '.format(var) in line:
                found_var = True
                for char in line:
                    if char in symbols_open:
                        stack.append(char)
                    elif char in symbols_close:
                        stack.pop(-1)
            elif stack:
                for char in line:
                    if char in symbols_open:
                        stack.append(char)
                    elif char in symbols_close:
                        stack.pop(-1)

            if not stack and found_var:
                line = line.replace(line, line + text_to_add)
                found_var = False

            print(line, end='')


def append_to_file(filename: str, text_to_append: str, recreate: bool = False):
    path = os.path.dirname(filename)
    if path and not os.path.isdir(path):
        os.mkdir(path)

    if recreate and os.path.exists(filename):
        os.remove(filename)

    with open(filename, 'a') as fp:
        fp.write(text_to_append)


def get_template_content(filename: str) -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    tpl = os.path.join(dir_path, 'templates', filename)
    with open(tpl, 'r') as file_tpl:
        content = file_tpl.read()
    return content
