def str_wrapper(input_str):
    input_str = str(input_str)
    return "\"" + input_str + "\""


def add_str(str1: str, str2: str) -> str:
    return str1 + " " + str2


def add_nothing_str(str1: str) -> str:
    return str1 + " " + "nothing"


