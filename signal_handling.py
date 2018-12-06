from signal import signal
from signal import SIGQUIT
from signal import SIGTSTP
from signal import SIG_IGN


def handle_signal():
    signal(SIGQUIT, SIG_IGN)  # -3
    signal(SIGTSTP, SIG_IGN)  # -20


if __name__ == '__main__':
    handle_signal()
