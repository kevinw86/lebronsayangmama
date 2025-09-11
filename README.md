# lebronsayangmama
An instant messaging project written in Python.

Project Structure
- backend.py → Runs as the server. Handles connections, messages, and communication between clients.
- main.py → Runs as the client. Each client connects to the server and can send/receive messages.
- chat.py, grouplist.py, login.py, network.py, notification.py → Helper modules used by the client and server to handle chat features, groups, login, network functions, and notifications.

The main files you need to run are only backend.py and main.py.

How to Run:
1. Start the server: python backend.py
    After running, you will see something like: Listening to IP address ...

2. Start the clients: python main.py
    You can run as many clients as you like, but 3–5 clients works best for testing.

DEMO SETUP
For our test demo, we used 3 clients connected to the same server. This helps show how messages are shared and how the system handles multiple users

