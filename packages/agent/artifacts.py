"""Sanitize HTML before wrapping it in a restrictive, standalone document."""

import nh3

CSP = (
    "default-src 'none'; style-src 'unsafe-inline'; img-src 'none'; "
    "form-action 'none'; base-uri 'none'"
)
TAGS = {
    "p",
    "div",
    "span",
    "section",
    "article",
    "header",
    "footer",
    "main",
    "aside",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "li",
    "strong",
    "em",
    "b",
    "i",
    "blockquote",
    "pre",
    "code",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    "hr",
    "br",
    "style",
    "small",
    "dl",
    "dt",
    "dd",
    "a",
}


def sanitize_html(content: str) -> str:
    cleaned = nh3.clean(
        content,
        tags=TAGS,
        attributes={"*": {"class", "style", "id"}},
        clean_content_tags={"script", "iframe", "object", "embed", "svg", "math"},
        url_schemes=set(),
        link_rel=None,
        strip_comments=True,
    )
    return (
        '<!doctype html><html><head><meta charset="utf-8">'
        f'<meta http-equiv="Content-Security-Policy" content="{CSP}">'
        '<meta name="referrer" content="no-referrer">'
        "<style>body{font:16px/1.6 system-ui;padding:32px;color:#17332d;"
        "overflow-wrap:anywhere}table{border-collapse:collapse;width:100%}"
        "td,th{border:1px solid #dbe4df;padding:12px}pre{white-space:pre-wrap}</style>"
        f"</head><body>{cleaned}</body></html>"
    )
