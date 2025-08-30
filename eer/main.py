from login import LoginWindow
from chat import ChatWindow
from grouplist import GroupListWindow
from network import connect_to_server

if __name__ == "__main__":
    # --- Step 1: Login ---
    login = LoginWindow()
    username = login.run()
    if not username:
        exit()

    # Shared group list
    groups = ["Kontol1", "Kontol2", "Kontol3"]

    while True:
        # --- Step 2: Select group ---
        group_window = GroupListWindow(groups)
        selected_group = group_window.run()
        group_window.root.destroy()

        if not selected_group:
            break  # User closed group selection

        # --- Step 3: Connect to server ---
        client = connect_to_server()  # reconnect every time
        chat = ChatWindow(username, client, selected_group)
        chat.run()  # ChatWindow blocks until window closed

        # After closing ChatWindow, loop continues to let user pick another group