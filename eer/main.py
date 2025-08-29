from login import LoginWindow
from chat import ChatWindow
from network import connect_to_server
from grouplist import GroupListWindow

if __name__ == "__main__":
    client = connect_to_server()
    login = LoginWindow()
    username = login.run()

    if username:
        groups = ["Kontol1", "Kontol2", "Kontol3"]  # Shared list object
        while True:
            group_window = GroupListWindow(groups)
            selected_group = group_window.run()
            group_window.root.destroy()  # Ensure window is closed
            if not selected_group:
                break
            chat = ChatWindow(username, client, selected_group)
            chat.run()