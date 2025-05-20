import socket
import json
import base64
import logging

server_address=('0.0.0.0',7777)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        logging.warning(f"sending message ")
        if not command_str.endswith("\r\n\r\n"):
        command_str += "\r\n\r\n"
        
        sock.sendall(command_str.encode())
        # Look for the response, waiting until socket is done (no more data)
        data_received="" #empty string
        while True:
            #socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
            data = sock.recv(16)
            if data:
                #data is not empty, concat with previous content
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                # no more data, stop the process by break
                break
        # at this point, data_received (string) will contain all data coming from the socket
        # to be able to use the data_received as a dict, need to load it using json.loads()
        hasil = json.loads(data_received)
        logging.warning("data received from server:")
        return hasil
    except:
        logging.warning("error during data receiving")
        return False


def remote_list():
    command_str=f"LIST"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        print("daftar file : ")
        for nmfile in hasil['data']:
            print(f"- {nmfile}")
        return True
    else:
        print("Gagal mengambil daftar file.")
        return False

def remote_get(filename=""):
    command_str=f"GET {filename}"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        #proses file dalam bentuk base64 ke bentuk bytes
        namafile = hasil['data_namafile']
        isifile = base64.b64decode(hasil['data_file'])
        filepath = os.path.join('files', namafile)
        with open(filepath, 'wb') as f:
            f.write(isifile)
        print(f"File {namafile} berhasil diunduh ke folder files/.")
        return True
    else:
        print(f"Gagal mengunduh file: {hasil['data']}")
        return False

def remote_upload(filepath):
    try:
        filename = os.path.basename(filepath)
        fullpath = os.path.join('files', filename)
        with open(fullpath, 'rb') as f:
            filedata = base64.b64encode(f.read()).decode()
        payload = json.dumps({
            "command": "upload",
            "filename": filename,
            "filedata": filedata
        }) + "\r\n\r\n"
        hasil = send_command(payload)
        if hasil['status'] == 'OK':
            print(f"Upload berhasil: {hasil['data']}")
        else:
            print(f"Gagal upload: {hasil['data']}")
    except Exception as e:
        print(f"Error saat upload: {e}")

def remote_delete(filename):
    command_str = f"DELETE {filename}"
    hasil = send_command(command_str)
    if hasil['status'] == 'OK':
        print(f"File {filename} berhasil dihapus.")
    else:
        print(f"Gagal menghapus file: {hasil['data']}")


def menu():
    while True:
        print("\nMenu:")
        print("1. Lihat daftar file di server")
        print("2. Download file dari server")
        print("3. Upload file ke server")
        print("4. Hapus file di server")
        print("5. Keluar")

        pilihan = input("Pilih (1-5): ")

        if pilihan == '1':
            remote_list()
        elif pilihan == '2':
            filename = input("Masukkan nama file yang ingin diunduh: ")
            remote_get(filename)
        elif pilihan == '3':
            filepath = input("Masukkan path file yang ingin diupload: ")
            remote_upload(filepath)
        elif pilihan == '4':
            filename = input("Masukkan nama file yang ingin dihapus: ")
            remote_delete(filename)
        elif pilihan == '5':
            print("Keluar.")
            break
        else:
            print("Pilihan tidak valid.")


if __name__=='__main__':
    menu()