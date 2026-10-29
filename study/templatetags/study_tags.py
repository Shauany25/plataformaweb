import html
import re
from urllib.parse import urlsplit
import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def exam_text(value):
    # Os enunciados são dados externos. HTML bruto é sempre escapado antes do Markdown.
    escaped = html.escape(value or '')
    output = markdown.markdown(escaped, extensions=['tables', 'nl2br'])
    # Markdown pode criar URLs javascript mesmo depois de escapar o HTML.
    def clean_url(match):
        attribute, url = match.group(1), html.unescape(match.group(2))
        parsed = urlsplit(url)
        if parsed.scheme != 'https':
            return f'{attribute}="#"'
        if attribute == 'src' and parsed.hostname not in {'enem.dev', 'raw.githubusercontent.com', 'api.enem.dev'}:
            return 'src=""'
        return match.group(0)
    output = re.sub(r'(href|src)="([^"]*)"', clean_url, output)
    output = output.replace('<img ', '<img loading="lazy" ')
    return mark_safe(output)

@register.filter
def is_due(value):
    from django.utils import timezone
    return value is not None and value <= timezone.now()
