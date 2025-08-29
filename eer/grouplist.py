import tkinter as tk
import tkinter.messagebox
import tkinter.simpledialog

class GroupListWindow:
    def __init__(self, groups=None):
        self.root = tk.Tk()
        self.root.title("Group List")
        self.root.geometry("400x500")
        self.root.configure(bg="white")

        self.groups = groups if groups else []
        self.selected_group = None  
        self.selected_group_index = None

        header = tk.Label(
            self.root, text="Group List",
            font=("Arial", 18, "bold"),
            bg="white", pady=10
        )
        header.pack(fill=tk.X)

        container = tk.Frame(self.root, bg="white")
        container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        self.canvas = tk.Canvas(container, bg="white", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(
            container, orient="vertical", command=self.canvas.yview
        )
        self.group_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.group_frame, anchor="nw")

        self.group_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Mouse wheel support
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        self.display_groups()

        create_btn = tk.Button(
            self.root, text="Create group",
            font=("Arial", 12, "bold"),
            bg="#89b4fa", fg="black",
            activebackground="#74c7ec",
            relief="solid", bd=1,
            command=self.create_group
        )
        create_btn.pack(pady=10, ipadx=10, ipady=5, fill=tk.X, padx=0)

        rename_btn = tk.Button(
            self.root, text="Rename group",
            font=("Arial", 12, "bold"),
            bg="#fab387", fg="black",
            activebackground="#f9e2af",
            relief="solid", bd=1,
            command=self.rename_group
        )
        rename_btn.pack(pady=5, ipadx=10, ipady=5, fill=tk.X, padx=0)

    def _on_mousewheel(self, event):
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")

    def display_groups(self):
        for widget in self.group_frame.winfo_children():
            widget.destroy()

        if not self.groups:
            no_group_label = tk.Label(
                self.group_frame, text="No group to be found",
                font=("Arial", 12), bg="white", fg="gray"
            )
            no_group_label.pack(pady=20, fill=tk.X, expand=True)
            return

        for idx, group in enumerate(self.groups):
            color = "#a6e3a1" if idx % 2 == 0 else "#f9e2af"

            frame = tk.Frame(
                self.group_frame,
                bg="white", highlightbackground=color,
                highlightcolor=color, highlightthickness=2, bd=0
            )
            frame.pack(fill=tk.X, expand=True, pady=2, padx=0)

            label = tk.Label(
                frame, text=group,
                font=("Arial", 14, "bold"),
                bg="white", fg="black", pady=8
            )
            label.pack(fill=tk.X, expand=True)

            frame.bind("<Button-1>", lambda e, i=idx, g=group: self.select_group(i, g))
            label.bind("<Button-1>", lambda e, i=idx, g=group: self.select_group(i, g))
            frame.bind("<Double-Button-1>", lambda e, g=group: self.open_group(g))
            label.bind("<Double-Button-1>", lambda e, g=group: self.open_group(g))

    def select_group(self, idx, group_name):
        self.selected_group_index = idx
        self.selected_group = group_name

    def open_group(self, group_name):
        self.selected_group = group_name
        self.root.quit()

    def create_group(self):
        new_name = f"Group {len(self.groups) + 1}"
        self.groups.append(new_name)
        self.display_groups()

    def rename_group(self):
        if self.selected_group_index is None:
            tk.messagebox.showwarning("No group selected", "Please select a group to rename.")
            return

        new_name = tk.simpledialog.askstring("Rename Group", "Enter new group name:", initialvalue=self.groups[self.selected_group_index])
        if new_name and new_name.strip():
            self.groups[self.selected_group_index] = new_name.strip()
            self.display_groups()
            self.selected_group = new_name.strip()

    def _update_scrollbar(self, event=None):
        frame_height = self.group_frame.winfo_height()
        canvas_height = self.canvas.winfo_height()
        if frame_height > canvas_height:
            self.scrollbar.pack(side="right", fill="y")
        else:
            self.scrollbar.pack_forget()

    def run(self):
        self.root.mainloop()
        return self.selected_group
