import tkinter as tk

class GroupListWindow:
    def __init__(self, groups=None):
        self.root = tk.Tk()
        self.root.title("Group List")
        self.root.geometry("400x500")
        self.root.configure(bg="white")

        # Store groups & selected group
        self.groups = groups if groups else []
        self.selected_group = None  

        # --- Title ---
        header = tk.Label(
            self.root, text="Group List",
            font=("Arial", 18, "bold"),
            bg="white", pady=10
        )
        header.pack(fill=tk.X)

        # --- Container for groups ---
        self.group_frame = tk.Frame(self.root, bg="white")
        self.group_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Display existing groups or empty state
        self.display_groups()

        # --- Create Group Button ---
        create_btn = tk.Button(
            self.root, text="Create group",
            font=("Arial", 12, "bold"),
            bg="#89b4fa", fg="black",
            activebackground="#74c7ec",
            relief="solid", bd=1,
            command=self.create_group
        )
        create_btn.pack(pady=15, ipadx=10, ipady=5, fill=tk.X, padx=20)

    # --- Show groups or placeholder ---
    def display_groups(self):
        for widget in self.group_frame.winfo_children():
            widget.destroy()

        if not self.groups:
            no_group_label = tk.Label(
                self.group_frame, text="No group to be found",
                font=("Arial", 12), bg="white", fg="gray"
            )
            no_group_label.pack(pady=20)
            return

        for idx, group in enumerate(self.groups):
            color = "#a6e3a1" if idx % 2 == 0 else "#f9e2af"

            frame = tk.Frame(
                self.group_frame,
                bg="white", highlightbackground=color,
                highlightcolor=color, highlightthickness=2, bd=0
            )
            frame.pack(fill=tk.X, pady=8, padx=5)

            label = tk.Label(
                frame, text=group,
                font=("Arial", 14, "bold"),
                bg="white", fg="black", pady=8
            )
            label.pack(fill=tk.X)

            # clicking group opens it
            frame.bind("<Button-1>", lambda e, g=group: self.open_group(g))
            label.bind("<Button-1>", lambda e, g=group: self.open_group(g))

    # --- When a group is clicked ---
    def open_group(self, group_name):
        self.selected_group = group_name
        self.root.destroy()  # close window and return to main

    # --- Create new group ---
    def create_group(self):
        new_name = f"Group {len(self.groups) + 1}"
        self.groups.append(new_name)
        self.display_groups()

    # --- Run and return selected group ---
    def run(self):
        self.root.mainloop()
        return self.selected_group
