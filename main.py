import os

from bindings import app, socket


if __name__ == '__main__':
    socket.run(app, port=3000)
