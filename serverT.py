import select, socket, sys, queue

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 50007              # Arbitrary non-privileged port
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setblocking(0)
    server.bind((HOST, PORT))
    server.listen(5)
    inputs = [server]
    outputs = []
    message_queues = {}

    while inputs:
        readable, writable, exceptional = select.select(inputs, outputs, inputs)

        for read in readable:
            if read is server:
                connection, client_address = read.accept()
                connection.setblocking(0)
                inputs.append(connection)
                message_queues[connection] = queue.Queue()

            else:
                data = read.recv(1024)

                if data.decode("utf-8") == "shutdown":
                    server.close()
                    exit(1)

                elif data:
                    message_queues[read].put(data)
                    if read not in outputs:
                        outputs.append(read)

                else:
                    if read in outputs:
                        outputs.remove(read)
                        read.close()
                        del message_queues[read]

        for write in writable:
            try:
                next_msg = message_queues[write].get_nowait()
            except queue.Empty:
                outputs.remove(write)
            else:
                write.send(next_msg)

        for exception in exceptional:
            inputs.remove(exception)
            if exception in outputs:
                outputs.remove(exception)
            exception.close
            del message_queues[exception]
