#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import sys

if sys.platform == "darwin":
    from Foundation import NSData, NSUnarchiver

    def decode_streamtyped(data):
        nsdata = NSData.dataWithBytes_length_(data, len(data))
        obj = NSUnarchiver.unarchiveObjectWithData_(nsdata)
        if obj is not None and hasattr(obj, "string"):
            s = obj.string()
            if s is not None:
                return s.UTF8String().decode()
            else:
                return ""
        return None

else:
    import typedstream

    def decode_streamtyped(buffer):
        """Parse NSAttributedString from typedstream format.

        Args:
            buffer: The attributedBody buffer from the database (bytes)

        Returns:
            str: The parsed text string, or empty string if parsing fails
        """
        try:
            root = typedstream.unarchive_from_data(buffer)
        except (ValueError, TypeError, OSError):
            return None

        if hasattr(root, 'contents') and root.contents:
            # First item typically contains the string value (NSString)
            first_item = root.contents[0]
            if hasattr(first_item, 'value') and hasattr(first_item.value, 'value'):
                return first_item.value.value

        return None
