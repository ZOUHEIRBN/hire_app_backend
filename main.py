from bindings import app, socket


if __name__ == '__main__':
    # subprocess.Popen('activate opencv-env')
    # subprocess.Popen('celery -A db_tasks worker')
    socket.run(app, port=3000)
