def parse_res_to_tuple(resolution: str):
    cutoff = resolution.index('x')
    try:
        width, height = int(resolution[:cutoff]), int(resolution[cutoff + 1:])
        return width, height
    except Exception:
        raise ValueError('Invalid input resolution, format should be {width}x{height}')
