import re
from typing import List, Tuple

from iter.enums import SpanType
from iter.models.span import Span

def parse_markdown(text: str) -> Tuple[List[Span], str]:
    result = []

    # Added patterns for LINK, MENTION, and QUOTE.
    # LINK is placed before other formatting to correctly handle styles within link text.
    patterns = [
        (SpanType.LINK, r'\[(.*?)\]\((.*?)\)'),
        (SpanType.BOLD, r'\*(.*?)\*'),
        (SpanType.STRIKETHROUGH, r'~(.*?)~'),
        (SpanType.SPOILER, r'\!(.*?)\!'),
        (SpanType.MONOSPACE, r'`(.*?)`'),
        (SpanType.UNDERLINE, r'_(.*?)_'),
        (SpanType.ITALIC, r'\/(.*?)\/'),
        (SpanType.MENTION, r'(@[a-zA-Z0-9_]+)'),
        (SpanType.QUOTE, r'^\s*>\s*(.*)'),
    ]

    # The combined pattern is used for calculating the correct offsets.
    COMBINED_PATTERN = "|".join(p for _, p in patterns)
    
    # A map from the index of a capturing group in the combined pattern to its SpanType.
    group_to_type_map = {}
    group_offset = 1
    for span_type, pattern_str in patterns:
        num_groups = re.compile(pattern_str).groups
        for i in range(num_groups):
            group_to_type_map[group_offset + i] = span_type
        group_offset += num_groups


    def process_match(match, md_type):
        overhead = 0
        # Calculate the offset adjustment caused by removing markdown syntax
        # in the text preceding the current match.
        for m in re.finditer(COMBINED_PATTERN, text[:match.start()]):
            overhead_span_type = group_to_type_map.get(m.lastindex)
            content_for_overhead = ""

            if overhead_span_type == SpanType.LINK:
                # For a link, the content is the first captured group (the text).
                # We need to find the correct group index in the combined match `m`.
                for i, group in enumerate(m.groups()):
                    if group is not None and group_to_type_map.get(i + 1) == SpanType.LINK:
                        content_for_overhead = m.group(i + 1)
                        break
            elif overhead_span_type:
                content_for_overhead = m.group(m.lastindex)

            overhead += len(m.group(0)) - len(content_for_overhead)

        actual_offset = match.start() - overhead
        
        content = ""
        url = None

        # Handle different span types to extract content and tags.
        if md_type == SpanType.LINK:
            content = match.group(1)
            url = match.group(2)
        else:
            content = match.group(1)

        span = Span(
            type=md_type,
            offset=actual_offset,
            length=len(content),
            url=url
        )
        result.append(span)

        return content

    # Process each pattern. The quote pattern requires the re.MULTILINE flag.
    for span_type, pattern in patterns:
        if span_type == SpanType.QUOTE:
            text = re.sub(pattern, lambda m: process_match(m, span_type), text, flags=re.MULTILINE)
        else:
            text = re.sub(pattern, lambda m: process_match(m, span_type), text)
    
    result.sort(key=lambda x: x.offset)
    
    return result, text.strip()