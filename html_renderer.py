""" Tools to render colored output"""


def sp():
    return "&nbsp;"


def span(klass: str, content: str) -> str:
    return f'<span class="{klass}">{content}</span>'


def op(content: str) -> str:
    return span("clr_operator", content)


def keyword(content: str) -> str:
    return span("clr_keyword", content)


def user_type(content: str) -> str:
    return span("clr_user_type", content)


def viper_type(content: str) -> str:
    return span("clr_viper_type", content)


def number(content: str) -> str:
    return span("clr_number", content)


def boolean(content: str) -> str:
    return keyword(content)


def string(content: str) -> str:
    return span("clr_string", content)


def quote(content: str) -> str:
    return span("clr_quote", content)


def uuid(content: str) -> str:
    return span("clr_uuid", content)

def comment(content: str) -> str:
    return span("clr_comment", content)
