import customtkinter as ctk
from CTkMessagebox import CTkMessagebox


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.wnd_root = ctk.CTk()
        self.after_idle(self.on_startup)

    def on_startup(self) -> None:
        # Load required data here, assume it fails
        mbox = CTkMessagebox()
        self.wait_window(mbox)
        self.destroy()


if __name__ == '__main__':
    app = App()
    app.mainloop()
