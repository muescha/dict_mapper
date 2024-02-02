import re


def camel_to_snake(camel_case):
    snake_case = re.sub('([a-z0-9])([A-Z])', r'\1_\2', camel_case)
    return snake_case.lower()

