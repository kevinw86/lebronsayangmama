from login import LoginWindow
from chat import ChatWindow
from network import connect_to_server
from grouplist import GroupListWindow

if __name__ == "__main__":
    client = connect_to_server()
    login = LoginWindow()
    username = login.run()

    if username:
        ChatWindow(username, client).run()
