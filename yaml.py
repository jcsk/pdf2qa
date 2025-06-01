try:
    import yaml as _yaml
    safe_load = _yaml.safe_load
    dump = _yaml.dump
except Exception:  # ModuleNotFoundError or other
    import json

    def safe_load(stream):
        if hasattr(stream, 'read'):
            data = stream.read()
        else:
            data = stream
        return json.loads(data)

    def dump(data, stream=None, **kwargs):
        text = json.dumps(data, **kwargs)
        if stream is not None:
            stream.write(text)
        else:
            return text
