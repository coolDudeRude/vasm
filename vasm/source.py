"""Source mapping logic for vasm"""

import re
from . import ir


def create_synline_map(text: str) -> list[ir.SourceMarker]:
    """Create source marker map for improved error messages"""

    pattern = re.compile(r'^#line (\d+)( "([^"]+)")?', re.MULTILINE)

    source_map = []

    for match in pattern.finditer(text):
        marker = ir.SourceMarker(
            index=match.start(),
            original_line=int(match.group(1)),
            original_file=match.group(2).strip(' "'),
        )
        source_map.append(marker)

    return source_map


def get_original_location(
    text: str, source_map: list[ir.SourceMarker], failure_index: int
):
    """Translates index in a stream into file/line information."""
    active_marker = None

    for marker in source_map:
        if marker.index <= failure_index:
            active_marker = marker
        else:
            break

    if not active_marker:
        return "unknown", 0, 0

    text_segment = text[active_marker.index : failure_index]

    # Calculate the row
    line_count = text_segment.count("\n")
    real_line = active_marker.original_line + line_count

    # calculate the column
    if line_count == 0:
        real_col = failure_index - active_marker.index

    else:
        last_newline_pos = text_segment.rfind("\n")
        real_col = len(text_segment) - last_newline_pos - 1

    return active_marker.original_file, real_line, real_col
