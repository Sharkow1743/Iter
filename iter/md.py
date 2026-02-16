import re
from typing import List, Tuple

from iter.enums import SpanType
from iter.models.span import Span

def parse_markdown(text: str) -> Tuple[List[Span], str]:
    result = []

    patterns = [
        (SpanType.BOLD, r'\*(.*?)\*'),
        (SpanType.STRIKETHROUGH, r'~(.*?)~'),
        (SpanType.SPOILER, r'\!(.*?)\!'),
        (SpanType.MONOSPACE, r'`(.*?)`'),
        (SpanType.UNDERLINE, r'_(.*?)\_'),
        (SpanType.ITALIC, r'\/(.*?)\/'),
        (SpanType.HASHTAG, r'(#[a-zA-Z0-9_]+)'),
    ]

    COMBINED_PATTERN = "|".join(p for _, p in patterns)

    def process_match(match, md_type):
        overhead = 0
        for m in re.finditer(COMBINED_PATTERN, text[:match.start()]):
            content = m.group(m.lastindex)
            overhead += len(m.group(0)) - len(content)
        
        actual_offset = match.start() - overhead
        
        content = match.group(1)
        
        span = Span(
            type=md_type,
            offset=actual_offset,
            length=len(content),
            tag=content if md_type == SpanType.HASHTAG else None
        )
        result.append(span)

        return content

    for span_type, pattern in patterns:
        text = re.sub(pattern, lambda m: process_match(m, span_type), text)
    
    result.sort(key=lambda x: x.offset)
    
    return result, text.strip()