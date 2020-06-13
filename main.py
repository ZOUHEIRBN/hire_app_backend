from bindings import app, socket, celery

if __name__ == '__main__':
    socket.run(app, port=3000)
