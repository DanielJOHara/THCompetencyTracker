"""This module displays the root window tah offers the primary options for the application."""
import logging
import os
import sys

import customtkinter as ctk
import tkinter as tk
from CTkMessagebox import CTkMessagebox
from PIL import ImageTk

from source.appdata import AppData
from source.command_line import resource
from source.master_data import MasterData, MasterDataError
from source.window import child_window, show_master_data_error
from source.data_management import DataManagement
from source.competency_tracking import CompetencyTracking

logger = logging.getLogger(__name__)


class RootWindow:
    """ Setup root menu and event loop for application."""
    def __init__(self, ad: AppData) -> None:
        logger.info("Creating CustomTkinter root window")

        self.ad = ad

        # Set colour themes: 'blue' (standard), 'green", 'dark-blue'
        ctk.set_default_color_theme(ad.args.theme)

        # Create root window with single frame of action buttons
        self.wnd_root = ctk.CTk()
        ad.wnd_root = self.wnd_root

        # Change window icon
        icon_path = resource(ad.args.icon)
        if os.path.isfile(icon_path):
            self.wnd_root.iconpath = ImageTk.PhotoImage(file=icon_path)
            self.wnd_root.wm_iconbitmap()
            self.wnd_root.iconphoto(False, str(self.wnd_root.iconpath))

        self.wnd_root.title("Staff Competency Tracker")

        self.frm_button = ctk.CTkFrame(self.wnd_root)
        self.frm_button.pack(pady=20, padx=60, fill='both', expand=False)

        self.btn_competency = ctk.CTkButton(self.frm_button, text="Competency Tracking", state='disabled',
                                            command=lambda: child_window(CompetencyTracking, ad, self.wnd_root))
        self.btn_competency.pack(pady=12, padx=20)

        self.btn_reload = ctk.CTkButton(self.frm_button,
                                        text="Reload Master Data", command=self.handle_reload_click)
        self.btn_reload.pack(pady=12, padx=20)

        self.btn_save = ctk.CTkButton(self.frm_button, text="Save Master Data",
                                      state='disabled', command=self.handle_save_click)
        self.btn_save.pack(pady=12, padx=20)

        self.btn_data_input = ctk.CTkButton(self.frm_button, text="Data Management", state='disabled',
                                            command=lambda: child_window(DataManagement, ad, self.wnd_root))
        self.btn_data_input.pack(pady=12, padx=20)

        self.lbl_about = ctk.CTkLabel(self.wnd_root, text=f"{ad.app_name} {ad.app_version}")
        self.lbl_about.pack(pady=0, padx=20, anchor='e')

        # Call routine on exit to test for changes
        self.wnd_root.protocol('WM_DELETE_WINDOW', self.on_closing)

        # Call routine on start up to read master data
        self.wnd_root.after_idle(self.on_startup)

        self.wnd_root.mainloop()

        logger.info(f"Exited CustomTkinter mainloop")

    def on_startup(self) -> None:
        """When the root menu first opens check the required directories are accessible
           and load the master Excel data."""
        # Check Master Excel file directory
        if not os.access(self.ad.args.master_excel_directory, os.W_OK):
            logger.error(f"Master Excel directory {self.ad.args.master_excel_directory} is not accessible")
            wnd_mb = CTkMessagebox(title="File Access Error",
                                   message="Master Excel directory is not accessible", icon='warning')
            self.wnd_root.wait_window(wnd_mb)
            sys.exit(1)

        master_excel_path = str(os.path.join(self.ad.args.master_excel_directory, self.ad.args.master_excel_file_name))
        self.ad.md = MasterData(master_excel_path, self.ad.args.retention)
        try:
            self.ad.md.load(master_excel_path, readonly=self.ad.args.readonly)
            self.set_button_states()

            # In readonly mode hide root window and start competency tracking window
            if self.ad.args.readonly:
                self.wnd_root.withdraw()
                child_window(CompetencyTracking, self.ad, self.wnd_root)

        except MasterDataError as e:
            show_master_data_error(str(e), self.wnd_root)
        except (IOError, ValueError) as e:
            logger.warning(e)
            if self.ad.args.readonly:
                self.frm_button.destroy()
                self.wnd_root.textbox = ctk.CTkTextbox(master=self.wnd_root, width=400, height=100)
                self.wnd_root.textbox.pack(pady=12, padx=20, fill='both', expand=False)
                self.wnd_root.textbox.insert("0.0", f"Failed to read master data:\n{e}")
            else:
                if str(e).startswith("Master Excel in use"):
                    msg = CTkMessagebox(title="Warning", message=str(e) + "\nHow would you like to continue",
                                        option_1='Read Only', option_2='Full Access')
                    if msg.get() == 'Read Only':
                        self.ad.args.readonly = True
                        try:
                            self.ad.md.load(master_excel_path, readonly=self.ad.args.readonly)
                            self.wnd_root.withdraw()
                            child_window(CompetencyTracking, self.ad, self.wnd_root)
                        except (IOError, ValueError) as e:
                            self.frm_button.destroy()
                            self.wnd_root.textbox = ctk.CTkTextbox(master=self.wnd_root, width=400, height=100)
                            self.wnd_root.textbox.pack(pady=12, padx=20, fill='both', expand=False)
                            self.wnd_root.textbox.insert("0.0", f"Failed to read master data:\n{e}")
                else:
                    CTkMessagebox(title="Data Load Error", message=e, icon='warning')

    def set_button_states(self) -> None:
        """Enable (normal) buttons that dependant on the master spreadsheet being loaded."""
        if hasattr(self, 'btn_competency'):
            self.btn_competency.configure(state='normal')
        if hasattr(self, 'btn_save'):
            self.btn_save.configure(state='normal')
        if hasattr(self, 'btn_data_input'):
            self.btn_data_input.configure(state='normal')

    def handle_reload_click(self) -> None:
        """Prompt user for the location of a master Excel file and load it."""
        excel_path = tk.filedialog.askopenfilename(
            initialdir=self.ad.args.master_excel_directory,
            initialfile=self.ad.args.master_excel_file_name,
            title="Select Competence Master Excel File",
            filetype=(('xlsx files', '*.xlsx'),)).replace('/', '\\')
        logger.info(f"User selected to re-load master Excel: {excel_path}")
        if excel_path:
            try:
                self.ad.md.load(str(excel_path))
                self.set_button_states()
            except MasterDataError as e:
                show_master_data_error(str(e), self.wnd_root)
            except (IOError, ValueError) as e:
                logger.warning(e)
                CTkMessagebox(title="Data Load Error", message=e, icon='warning')

    def handle_save_click(self) -> None:
        """Write the master Excel using the current data."""
        logger.info("User selected to save master Excel")
        self.ad.md.write()
        self.ad.master_updated = False
        CTkMessagebox(title="Information", message="Master data saved", icon='info')

    def on_closing(self) -> None:
        """When the root window is closed check if there are any data updates
           and prompt user if they should be saved."""
        if self.ad.master_updated:
            msg = CTkMessagebox(title="Warning", message="You have unsaved changes",
                                option_1='Save Changes', option_2='Exit', option_3='Cancel')
            if msg.get() == 'Save Changes':
                logger.info("On exit user selected to save master Excel")
                self.ad.md.write()
            elif msg.get() == 'Cancel':
                logger.info("User canceled exit when informed there were changes")
                return
            else:
                logger.info("On exit user selected no to save master Excel changes")

        self.wnd_root.destroy()
