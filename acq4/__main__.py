if __package__ is None:
    import acq4
    __package__ = 'acq4'

from .startup import startAcq4Application


startAcq4Application()
