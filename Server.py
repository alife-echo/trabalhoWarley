import rpyc
import os
import threading

# Dicionário para armazenar interesses de clientes em arquivos
interesses = {}

class FileTransferService(rpyc.Service):
    def on_connect(self, conn):
        print("Cliente conectado")

    def on_disconnect(self, conn):
        print("Cliente desconectado")

    def exposed_upload_files(self, filename, data):
        filepath = os.path.join("arquivos", filename)
        with open(filepath, "wb") as f:
            f.write(data)
        self._check_and_notify(filename)
        return f"Arquivo {filename} carregado com sucesso."

    def exposed_list_files(self):
        return os.listdir("arquivos")

    def exposed_download_files(self, filename):
        filepath = os.path.join("arquivos", filename)
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                return f.read()
        else:
            return f"Arquivo {filename} não encontrado."

    def exposed_register_interest(self, filename, client_ref, duration):
        if filename not in interesses:
            interesses[filename] = []
        
        interesse = {
            "client_ref": client_ref,
            "timeout": threading.Timer(duration, self._remove_interest, [filename, client_ref])
        }
        interesses[filename].append(interesse)
        interesse['timeout'].start()
        return f"Interesse registrado para o arquivo {filename}."

    def exposed_cancel_interest(self, filename, client_ref):
        if filename in interesses:
            self._remove_interest(filename, client_ref)
            return f"Interesse cancelado para o arquivo {filename}."
        return f"Não há interesse registrado para o arquivo {filename}."

    def _check_and_notify(self, filename):
        if filename in interesses:
            for interest in interesses[filename]:
                try:
                    interest['client_ref'].notify_file_available(filename)
                except Exception as e:
                    print(f"Falha ao notificar cliente: {e}")

            del interesses[filename]

    def _remove_interest(self, filename, client_ref):
        if filename in interesses:
            interesses[filename] = [
                interest for interest in interesses[filename]
                if interest["client_ref"] != client_ref
            ]
            if not interesses[filename]:
                del interesses[filename]

if __name__ == "__main__":
    if not os.path.exists("arquivos"):
        os.makedirs("arquivos")

    from rpyc.utils.server import ThreadedServer
    server = ThreadedServer(FileTransferService, port=18861)
    server.start()
