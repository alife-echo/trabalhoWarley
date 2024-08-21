import rpyc
import os
from tkinter import *
from tkinter import filedialog
import customtkinter as ctk
from tkinter import messagebox


local_interests = []
class ClientService(rpyc.Service):
    def on_connect(self, conn):
        print("Conectado ao servidor")

    def on_disconnect(self, conn):
        print("Desconectado do servidor")

  
def notify_file_available(filename):
        messagebox.showinfo("Notificação", conn.root.send_notify(filename))

def input_register_interest():
    textDialog = ctk.CTkInputDialog(text="Digite o nome do arquivo de interesse", title="Marcar Interesse")
    filename = textDialog.get_input()
    if filename:
        register_interest(filename)

def register_interest(filename):
    try:
        duration = 60 * 60  # Duração do interesse (em segundos)
        conn.root.register_interest(filename, conn, duration)
        local_interests.append(filename)
        messagebox.showinfo("Sucesso", f"Interesse no arquivo '{filename}' registrado com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao registrar interesse: {e}")


def setPreviewFile(filepath):
    path_entry.delete(0, END)
    path_entry.insert(0, filepath)

def selectFile():
    global filename
    filename = filedialog.askopenfilename(
        initialdir=os.getcwd(),
        title="Selecionar Arquivo",
    )
    setPreviewFile(filename)

def saveFile():
    try:
        with open(filename, "rb") as file:
            data = file.read()
        conn.root.upload_files(os.path.basename(filename), data)
        setPreviewFile("")

        messagebox.showinfo("Sucesso", "Upload realizado com sucesso!")
        
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao fazer upload: {e}")

def download_file(filename):
    try:
        file_data = conn.root.download_files(filename)
        if isinstance(file_data, bytes):
            download_path = os.path.join("downloads", filename)
            with open(download_path, "wb") as f:
                f.write(file_data)
            messagebox.showinfo("Sucesso", f"Arquivo '{filename}' baixado com sucesso em 'downloads'")
        else:
            messagebox.showerror("Erro", file_data)
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao baixar arquivo: {e}")

def input_get_name_download_file():
    textDialog = ctk.CTkInputDialog(text="Nome Arquivo Para Baixar", title="Baixar")
    filename = textDialog.get_input()
    if filename:
        download_file(filename)

def open_new_window_show_files():
    new_window_custom = ctk.CTkToplevel()
    new_window_custom.title("Ver Arquivos")
    new_window_custom.geometry("550x300")
    button_for_download_archive = ctk.CTkButton(master=new_window_custom, text="Baixar Arquivo", width=75, command=input_get_name_download_file)
    button_for_download_archive.place(relx=0.5, rely=0.5, anchor=CENTER)

    try:
        files = conn.root.list_files()
        if files:
            for idx, file in enumerate(files):
                file_label = ctk.CTkLabel(new_window_custom, text=file)
                file_label.pack(anchor='w')
        else:
            no_files_label = ctk.CTkLabel(new_window_custom, text="Nenhum arquivo disponível.")
            no_files_label.pack()
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao listar arquivos: {e}")


def input_get_name_mark_disinterest():
    textDialog = ctk.CTkInputDialog(text="Nome Arquivo Desmarcar Interesse", title="Desmarcar")
    filename = textDialog.get_input()
    if filename:
        cancel_interest(filename)

def cancel_interest(filename):
    try:
        response = conn.root.cancel_interest(filename,conn)
        if "cancelado" in response:
            if filename in local_interests:
                local_interests.remove(filename)
            update_interest_window()
            messagebox.showinfo("Sucesso", f"Interesse no arquivo '{filename}' cancelado com sucesso!")
        else:
            messagebox.showerror("Falha", response)
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao cancelar interesse: {e}")




def update_interest_window():
    files = [file for file in os.listdir("arquivos") if file in local_interests]
    
    for widget in interest_window.winfo_children():
        widget.destroy()  

    if files:
        for idx, file in enumerate(files):
            file_label = ctk.CTkLabel(interest_window, text=file)
            file_label.pack(anchor='w')
    else:
        no_files_label = ctk.CTkLabel(interest_window, text="Nenhum arquivo marcado como interesse.")
        no_files_label.pack()




def open_new_window_file_interest():
    global interest_window
    interest_window = ctk.CTkToplevel()
    interest_window.title("Arquivos com interesse")
    interest_window.geometry("550x300")
    button_for_download_archive = ctk.CTkButton(master=interest_window, text="Marcar Desinteresse", width=75, command=input_get_name_mark_disinterest)
    button_for_download_archive.place(relx=0.5, rely=0.5, anchor=CENTER)
    try:
        files = [file for file in local_interests if file in local_interests]
        if files:
            for idx, file in enumerate(files):
                file_label = ctk.CTkLabel(interest_window, text=file)
                notify_file_available(file)
                file_label.pack(anchor='w')
        else:
            no_files_label = ctk.CTkLabel(interest_window, text="Nenhum arquivo marcado como interesse.")
            no_files_label.pack()
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao listar arquivos de interesse: {e}")


conn = rpyc.connect("localhost", 18861, service=ClientService)

root = ctk.CTk()
root.title("Gerenciador de Arquivos")
root.geometry("650x400")
root.config(background="#2F3136")

frame = ctk.CTkLabel(root, text="")
frame.place(relx=0.83, rely=0.3, anchor=CENTER)

button_upload = ctk.CTkButton(master=root, text="Escolher Arquivo", command=selectFile)
path_entry = ctk.CTkEntry(master=root, width=200)
saveBtn = ctk.CTkButton(master=root, text="Upload", width=50, command=saveFile)
button_query_file = ctk.CTkButton(master=root, text="Mostrar Arquivos", command=open_new_window_show_files)
button_mark_interest = ctk.CTkButton(master=root, text="Marcar Interesse", command=input_register_interest)
button_show_file_interest = ctk.CTkButton(master=root, text="Mostrar Arquivos com Interesse",command=open_new_window_file_interest)

path_entry.place(relx=0.55, rely=0.3, anchor=CENTER)
saveBtn.place(relx=0.75, rely=0.3, anchor=CENTER)
button_upload.place(relx=0.3, rely=0.3, anchor=CENTER)
button_query_file.place(relx=0.5, rely=0.4, anchor=CENTER)
button_mark_interest.place(relx=0.5, rely=0.5, anchor=CENTER)
button_show_file_interest.place(relx=0.5, rely=0.6, anchor=CENTER)

root.mainloop()