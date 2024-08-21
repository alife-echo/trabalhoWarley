import rpyc
import os
import threading
from tkinter import messagebox
import numpy as np
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
            removed = self._remove_interest(filename, client_ref)
            if removed:
                return f"Interesse cancelado para o arquivo {filename}."
            else:
                return f"Não foi possível cancelar o interesse para o arquivo {filename}."
        return f"Não há interesse registrado para o arquivo {filename}."
    def exposed_send_notify(self,filename):
        return f"O arquivo '{filename}' está agora disponível"
    
    def _check_and_notify(self, filename):
        if filename in interesses:
            for interest in interesses[filename]:
                try:
                    client_ref = interest['client_ref']
                    print("Atributos e métodos disponíveis:", dir(client_ref))              
                    self.exposed_send_notify(filename)
                 
                        
                except Exception as e:
                    print(f"Falha ao notificar cliente: {e}")

            del interesses[filename]


    def _remove_interest(self, filename, client_ref):
        if filename in interesses:
            original_length = len(interesses[filename])
            interesses[filename] = [
                interest for interest in interesses[filename]
                if not self._is_same_client(interest["client_ref"], client_ref)
            ]
            if len(interesses[filename]) < original_length:
                if not interesses[filename]:
                    del interesses[filename]
                return True
        return False

    def _is_same_client(self, ref1, ref2):
        try:
            return ref1 == ref2
        except EOFError:
            return False

if __name__ == "__main__":
    if not os.path.exists("arquivos"):
        os.makedirs("arquivos")
    print(os.listdir("arquivos"))
    print(interesses)
    from rpyc.utils.server import ThreadedServer
    server = ThreadedServer(FileTransferService, port=18861)
    server.start()