def setup_logger(msg):
    with open("logs.txt", "a") as file:
        file.write(msg)
