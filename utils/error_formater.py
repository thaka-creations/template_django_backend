import re
import ast


def format_error(error):
    """
    Formats a Django or DRF error into a standardized string message,
    always including the field name when available.
    """

    def extract_message(msg):
        s = str(msg)
        # Handle DRF's ErrorDetail
        match = re.search(r"ErrorDetail\(string='(.+?)', code='(.+?)'\)", s)
        if match:
            return match.group(1)

        # Handle dict-like string "{'field': ['error']}"
        if s.startswith("{") and s.endswith("}"):
            try:
                d = ast.literal_eval(s)
                if isinstance(d, dict):
                    messages = []
                    for field, v in d.items():
                        if isinstance(v, (list, tuple)):
                            for item in v:
                                messages.append(field_message(field, item))
                        else:
                            messages.append(field_message(field, v))
                    return "; ".join(messages)
            except Exception:
                pass
        return s

    def field_message(field, msg):
        text = extract_message(msg)
        if text == "This field is required.":
            return f"{field} is required"
        return f"{field}: {text}"

    # DRF ValidationError
    if hasattr(error, "detail"):
        detail = error.detail
        if isinstance(detail, dict):
            messages = []
            for field, msgs in detail.items():
                if isinstance(msgs, (list, tuple)):
                    for msg in msgs:
                        messages.append(field_message(field, msg))
                else:
                    messages.append(field_message(field, msgs))
            return ", ".join(messages)

        elif isinstance(detail, (list, tuple)):
            # List-level errors, not tied to a field
            return ", ".join(extract_message(msg) for msg in detail)

        else:
            return extract_message(detail)

    # Django ValidationError with message_dict
    elif hasattr(error, "message_dict"):
        messages = []
        for field, msgs in error.message_dict.items():
            if isinstance(msgs, (list, tuple)):
                for msg in msgs:
                    messages.append(field_message(field, msg))
            else:
                messages.append(field_message(field, msgs))
        return ", ".join(messages)

    # Django ValidationError with messages only
    elif hasattr(error, "messages"):
        return ", ".join(extract_message(msg) for msg in error.messages)

    # Fallback
    else:
        if str(error).strip() == "This field is required.":
            return "A required field is missing"
        return extract_message(error)
