"""Transform loading and conversion utilities."""
from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from coorx import AffineTransform, SRT3DTransform, Transform, create_transform


def load_transform_from_anything(thing, **kwargs) -> Transform:
    """Load a transform from various input formats.

    Supports:
    - pyqtgraph.SRTTransform objects
    - coorx Transform objects (returned as-is)
    - Lists (interpreted as 4x4 matrix)
    - Dicts with 'type' key (passed to coorx.create_transform)
    - Config-style dicts with 'pos', 'scale', 'angle' keys

    Parameters
    ----------
    thing : various
        The input to convert to a transform.
    **kwargs
        Additional keyword arguments passed to the transform constructor.

    Returns
    -------
    Transform
        The loaded transform.
    """
    if isinstance(thing, pg.SRTTransform):
        return SRT3DTransform.from_pyqtgraph(thing, **kwargs)
    elif isinstance(thing, Transform):
        return thing
    elif isinstance(thing, list):
        return AffineTransform.from_matrix(np.array(thing), **kwargs)
    elif "type" in thing:
        return create_transform(**thing, **kwargs)
    else:  # config-style dict
        thing = thing.copy()
        thing.setdefault("offset", thing.pop("pos", None))
        if thing["offset"] is not None and len(thing["offset"]) == 2:
            thing["offset"] = [thing["offset"][0], thing["offset"][1], 0]
        if len(thing.get("scale", [])) == 2:
            thing["scale"] = [thing["scale"][0], thing["scale"][1], 1]
        return SRT3DTransform(**thing, **kwargs)
