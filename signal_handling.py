from signal import signal
from signal import SIGQUIT
from signal import SIGTSTP
from signal import SIGTERM
from signal import SIG_IGN


def handle_signal():
    signal(SIGQUIT, SIG_IGN)  # -3
    signal(SIGTSTP, SIG_IGN)  # -20
    signal(SIGTERM, SIG_IGN)
