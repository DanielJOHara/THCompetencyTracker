"""This module displays the windows to select data management processes."""
import logging

import customtkinter as ctk

from source.appdata import AppData
from source.role_competency_gui import RoleCompetencyGrid
from source.window import child_window
from source.service_gui import ServiceUpdate
from source.role_gui import RoleUpdate
from source.staff_gui import StaffUpdate
from source.competency_gui import CompetencyUpdate
from source.staff_role_gui import StaffRoleUpdate
from source.choose_colours import ChooseColours

logger = logging.getLogger(__name__)


class DataManagement(object):
    def __init__(self, ad: AppData, wnd_data: ctk.CTkToplevel) -> None:
        """Window to offer user list of master data tables to update."""
        logger.info("Creating Data Management window")

        wnd_data.title("Data Management")

        self.frm_button = ctk.CTkFrame(wnd_data)
        self.frm_button.pack(pady=20, padx=60, fill='both', expand=True)

        self.btn_service = ctk.CTkButton(self.frm_button, text="Service Areas",
                                         command=lambda: child_window(ServiceUpdate, ad, wnd_data))
        self.btn_service.pack(pady=12, padx=20)

        self.btn_role = ctk.CTkButton(self.frm_button, text="Roles",
                                      command=lambda: child_window(RoleUpdate, ad, wnd_data))
        self.btn_role.pack(pady=12, padx=20)

        self.btn_staff = ctk.CTkButton(self.frm_button, text="Staff",
                                       command=lambda: child_window(StaffUpdate, ad, wnd_data))
        self.btn_staff.pack(pady=12, padx=20)

        self.btn_competency = ctk.CTkButton(self.frm_button, text="Competencies",
                                            command=lambda: child_window(CompetencyUpdate, ad, wnd_data))
        self.btn_competency.pack(pady=12, padx=20)

        self.btn_staff_role = ctk.CTkButton(self.frm_button, text="Staff Roles",
                                            command=lambda: child_window(StaffRoleUpdate, ad, wnd_data))
        self.btn_staff_role.pack(pady=12, padx=20)

        self.btn_role_comp = ctk.CTkButton(self.frm_button, text="Role Competencies",
                                           command=lambda: child_window(RoleCompetencyGridSelect, ad, wnd_data))
        self.btn_role_comp.pack(pady=12, padx=20)

        self.btn_colour = ctk.CTkButton(self.frm_button, text="Colour Selector",
                                        command=lambda: child_window(ChooseColours, ad, wnd_data))
        self.btn_colour.pack(pady=12, padx=20)


class RoleCompetencyGridSelect(object):
    """Window for the user to enter the Service Code and Staff Type for which
       to generate the role competency grid."""
    def __init__(self, ad: AppData, wnd_cg_select: ctk.CTkToplevel) -> None:
        logger.info("Creating Role Competency Grid Selection window")

        self.wnd_cg_select = wnd_cg_select
        self.ad = ad

        # Add title top window
        wnd_cg_select.title("Role Competency Grid Selection")

        self.frm_attribute = ctk.CTkFrame(wnd_cg_select)
        self.frm_attribute.pack(fill='both', side='left', expand=True)

        row = 0
        self.lbl_service_code = ctk.CTkLabel(self.frm_attribute, text="Service Code")
        self.lbl_service_code.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.cmb_service_code = ctk.CTkComboBox(self.frm_attribute, state='readonly',
                                                values=ad.md.get_list('Service', 'Service Code'),
                                                command=self.call_review)
        self.cmb_service_code.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_staff_type = ctk.CTkLabel(self.frm_attribute, text="Staff Type")
        self.lbl_staff_type.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.cmb_staff_type = ctk.CTkComboBox(self.frm_attribute, state='readonly',
                                              values=['RN', 'HCA'], command=self.call_review)
        self.cmb_staff_type.grid(row=row, column=1, pady=6, padx=10, sticky='w')

    # noinspection PyUnusedLocal
    def call_review(self, event):
        """Function to review inputs and call role competency grid window if required."""

        service_code = self.cmb_service_code.get()
        staff_type = self.cmb_staff_type.get()
        if service_code and staff_type:
            # Call routine to generate grid, waiting for it to close then close this window
            child_window(RoleCompetencyGrid, self.ad, self.wnd_cg_select, service_code, staff_type)
            self.wnd_cg_select.destroy()
