def summarize_changes(change_payload: dict) -> str | None:
    """
    Works with either payload style:
      A) { "changes": [ {...}, {...} ] }      (folder-scoped trigger)
      B) { "changeType": "...", "file": {...} }  (global trigger = your case)
    """
    # A) folder-trigger delivers a list
    if "changes" in change_payload:
        changes = change_payload["changes"]
    else:
        changes = [change_payload]            # B) wrap single object

    if not changes:
        return None

    out = []
    for c in changes:
        # name can live in different keys depending on trigger version
        name = (
            c.get("fileName") or
            (c.get("file", {}).get("name")) or
            c.get("name") or
            "unknown"
        )
        ctype = c.get("changeType") or c.get("type") or "change"
        out.append(f"- {name} ({ctype})")

    return "\n".join(out)
