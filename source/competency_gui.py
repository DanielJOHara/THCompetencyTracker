
import logging

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

from source.appdata import AppData
from source.competency_logic import CompetencyLogic
from source.window import child_window, set_disabled_checkbox, set_disabled_entry, input_warning

logger = logging.getLogger(__name__)


class CompetencyUpdate(object):
    """Window to allow user to update Competency data. The data is presented as a table."""
    def __init__(self, ad: AppData, wnd_competency: ctk.CTkToplevel) -> None:
        logger.info("Creating Competency data update window")

        self.wnd_competency = wnd_competency
        self.ad = ad
        self.cl = CompetencyLogic(ad)

        # Add title top window
        wnd_competency.title("Competency Data Update")

        # Create header frame, pad to align with scrollable frame
        self.frm_h = ctk.CTkFrame(wnd_competency)
        self.frm_h.pack(padx=6, fill='x', expand=False)

        self.header = ['Display Order', 'Competency Name', 'Scope', 'Expiry', 'Prerequisite', 'Nightshift', 'Bank']
        self.width = [90, 250, 90, 90, 90, 90, 90]

        # Create list to hold header labels
        self.lbl_header = []

        # Display header row
        for x in range(len(self.header)):
            self.lbl_header.append(ctk.CTkLabel(self.frm_h, text=self.header[x], height=30, width=self.width[x],
                                                corner_radius=6, fg_color='#00B0F0'))
            self.lbl_header[x].grid(row=0, column=x)

        # Create scrollable frame
        self.frm_s = ctk.CTkScrollableFrame(wnd_competency)
        self.frm_s.pack(fill='both', expand=True)

        # Create lists to hold column widgets
        self.competency_widgets = []

        # Display widgets for all competency records
        for db_c in range(ad.md.len('Competency')):
            self.add_competency_to_display(db_c)

        # Create button frame
        self.frm_btn = ctk.CTkFrame(wnd_competency)
        self.frm_btn.pack(fill='x', expand=False)

        self.btn_update = ctk.CTkButton(self.frm_btn, text="Save", command=self.handle_save_click)
        self.btn_update.grid(row=0, column=0, pady=6, padx=10)

        self.btn_add = ctk.CTkButton(self.frm_btn, text="Add", command=self.handle_add_click)
        self.btn_add.grid(row=0, column=1, pady=6, padx=10)

        self.btn_add = ctk.CTkButton(self.frm_btn, text="Delete", command=self.handle_delete_click)
        self.btn_add.grid(row=0, column=2, pady=6, padx=10)

        self.btn_add = ctk.CTkButton(self.frm_btn, text="Exit", command=wnd_competency.destroy)
        self.btn_add.grid(row=0, column=3, pady=6, padx=10)

    def handle_save_click(self) -> None:
        """Read all values in table and update the table object if any values have changed."""
        number_changes, message = self.cl.save_competencies(self.competency_widgets)

        if message != f"{number_changes} changes saved":
            input_warning(self.wnd_competency, message)
            return

        CTkMessagebox(title="Information", message=message, icon='info')

        # Sort table and fresh display
        if number_changes > 0:
            self.display_competency_table()

    def handle_add_click(self) -> None:
        """Prompt user for row to be added."""
        # Invoke function to add row to table
        child_window(CompetencyAdd, self.ad, self.wnd_competency)

        # Refresh table sorting into display order, this will add the extra row
        self.display_competency_table()

    def handle_delete_click(self) -> None:
        # Call window to delete competencies
        child_window(CompetencyDelete, self.ad, self.wnd_competency)

        # Remove a row from the table for each deleted record
        for i in range(len(self.competency_widgets) - self.ad.md.len('Competency')):
            # Remove last row of widgets
            for widget_key in self.competency_widgets[-1]:
                self.competency_widgets[-1][widget_key].destroy()
            self.competency_widgets.pop()

        # Re-display table
        self.display_competency_table()

    def display_competency_table(self) -> None:
        """Display widgets for all competency records"""
        for db_c in range(self.ad.md.len('Competency')):
            self.add_competency_to_display(db_c)

    def add_competency_to_display(self, db_c: int) -> None:
        """Display a row of widgets for a specified Competency table index."""
        # If the index is beyond what is already in the widget lists append new widgets
        if db_c + 1 > len(self.competency_widgets):
            self.competency_widgets.append({
                'display_order': ctk.CTkEntry(self.frm_s, width=self.width[0]),
                'competency_name': ctk.CTkEntry(self.frm_s, width=self.width[1]),
                'scope': ctk.CTkComboBox(self.frm_s, width=self.width[2], state='readonly', values=['BOTH', 'RN', 'HCA']),
                'expiry': ctk.CTkEntry(self.frm_s, width=self.width[3]),
                'prerequisite': ctk.CTkCheckBox(self.frm_s, width=self.width[4] - 2 * int(self.width[4] / 3), text=""),
                'nightshift': ctk.CTkCheckBox(self.frm_s, width=self.width[5] - 2 * int(self.width[5] / 3), text=""),
                'bank': ctk.CTkCheckBox(self.frm_s, width=self.width[6] - 2 * int(self.width[6] / 3), text="")
            })
            col = 0
            for key in self.competency_widgets[db_c]:
                if key in ['prerequisite', 'nightshift', 'bank']:
                    self.competency_widgets[db_c][key].grid(row=db_c + 1, column=col, sticky='nsew', padx=int(self.width[col] / 3))
                else:
                    self.competency_widgets[db_c][key].grid(row=db_c + 1, column=col, sticky='w')
                col += 1

        # Set all widget values
        self.competency_widgets[db_c]['display_order'].delete(0, 9999)
        self.competency_widgets[db_c]['display_order'].insert(0, self.ad.md.get('Competency', 'Display Order', db_c))

        self.competency_widgets[db_c]['competency_name'].delete(0, 9999)
        self.competency_widgets[db_c]['competency_name'].insert(0, self.ad.md.get('Competency', 'Competency Name', db_c))

        self.competency_widgets[db_c]['scope'].set(self.ad.md.get('Competency', 'Scope', db_c))

        self.competency_widgets[db_c]['expiry'].delete(0, 9999)
        self.competency_widgets[db_c]['expiry'].insert(0, self.ad.md.get('Competency', 'Expiry', db_c))

        if self.ad.md.get('Competency', 'Prerequisite', db_c):
            self.competency_widgets[db_c]['prerequisite'].select()
        else:
            self.competency_widgets[db_c]['prerequisite'].deselect()

        if self.ad.md.get('Competency', 'Nightshift', db_c):
            self.competency_widgets[db_c]['nightshift'].select()
        else:
            self.competency_widgets[db_c]['nightshift'].deselect()

        if self.ad.md.get('Competency', 'Bank', db_c):
            self.competency_widgets[db_c]['bank'].select()
        else:
            self.competency_widgets[db_c]['bank'].deselect()


class CompetencyDelete(object):
    """Window to allow user to delete Competency data records."""
    def __init__(self, ad: AppData, wnd_competency_del: ctk.CTkToplevel) -> None:
        logger.info(f"Creating Competency data delete window")

        self.wnd_competency_del = wnd_competency_del
        self.ad = ad
        self.cl = CompetencyLogic(ad)

        # Add title top window
        self.wnd_competency_del.title("Competency Data Delete")

        self.frm_attribute = ctk.CTkFrame(wnd_competency_del)
        self.frm_attribute.pack(fill='both', side='left', expand=True)

        row = 0
        self.lbl_competency_name = ctk.CTkLabel(self.frm_attribute, text="Competency Name")
        self.lbl_competency_name.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.cmb_competency_name = ctk.CTkComboBox(
            self.frm_attribute,
            state='readonly',
            values=ad.md.get_list('Competency', 'Competency Name'),
            command=self.refresh_competency)
        self.cmb_competency_name.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_scope = ctk.CTkLabel(self.frm_attribute, text="Scope")
        self.lbl_scope.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.ent_scope = ctk.CTkEntry(self.frm_attribute, state='disabled')
        self.ent_scope.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_display_order = ctk.CTkLabel(self.frm_attribute, text="Display Order")
        self.lbl_display_order.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.ent_display_order = ctk.CTkEntry(self.frm_attribute, state='disabled')
        self.ent_display_order.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_expiry = ctk.CTkLabel(self.frm_attribute, text="Expiry")
        self.lbl_expiry.grid(row=row, column=0, pady=6, padx=10)
        self.ent_expiry = ctk.CTkEntry(self.frm_attribute, state='disabled')
        self.ent_expiry.grid(row=row, column=1, pady=6, padx=10)

        row += 1
        self.chc_prerequisite = ctk.CTkCheckBox(self.frm_attribute, text="Prerequisite", state='disabled')
        self.chc_prerequisite.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.chc_nightshift = ctk.CTkCheckBox(self.frm_attribute, text="Nightshift", state='disabled')
        self.chc_nightshift.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.chc_bank = ctk.CTkCheckBox(self.frm_attribute, text="Bank", state='disabled')
        self.chc_bank.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        # Action Buttons
        self.btn_delete = ctk.CTkButton(wnd_competency_del, text="Delete", command=self.handle_delete_click)
        self.btn_delete.pack(pady=6, padx=10)

        self.btn_exit = ctk.CTkButton(wnd_competency_del, text="Exit", command=wnd_competency_del.destroy)
        self.btn_exit.pack(pady=6, padx=10)

    # noinspection PyUnusedLocal
    def refresh_competency(self, event: str) -> None:
        """Display the competency record selected."""
        # Identify selected competency
        competency_name = self.cmb_competency_name.get()
        db_c = self.ad.md.index('Competency', 'Competency Name', competency_name)

        set_disabled_entry(self.ent_scope, self.ad.md.get('Competency', 'Scope', db_c))
        set_disabled_entry(self.ent_display_order, self.ad.md.get('Competency', 'Display Order', db_c))
        set_disabled_entry(self.ent_expiry, self.ad.md.get('Competency', 'Expiry', db_c))
        set_disabled_checkbox(self.chc_prerequisite, self.ad.md.get('Competency', 'Prerequisite', db_c))
        set_disabled_checkbox(self.chc_nightshift, self.ad.md.get('Competency', 'Nightshift', db_c))
        set_disabled_checkbox(self.chc_bank, self.ad.md.get('Competency', 'Bank', db_c))

    def handle_delete_click(self):
        """Delete current record."""
        competency_name = self.cmb_competency_name.get()
        success, message = self.cl.delete_competency(competency_name)

        if not success:
            if message != "No competency selected.":
                msg = CTkMessagebox(title="Dependent Record Warning", message=message,
                                    icon='warning', option_1='Delete', option_2='Cancel')
                if msg.get() == 'Cancel':
                    self.wnd_competency_del.grab_set()
                    return
                self.wnd_competency_del.grab_set()
                self.cl.delete_competency_with_dependents(competency_name)

        # Clear widgets
        self.cmb_competency_name.set('')
        self.cmb_competency_name.configure(values=self.ad.md.get_list('Competency', 'Competency Name'))
        set_disabled_entry(self.ent_scope, '')
        set_disabled_entry(self.ent_display_order, '')
        set_disabled_entry(self.ent_expiry, '')
        set_disabled_checkbox(self.chc_prerequisite, 0)
        set_disabled_checkbox(self.chc_nightshift, 0)
        set_disabled_checkbox(self.chc_bank, 0)


class CompetencyAdd(object):
    """Window to allow user to add  a single record Competency data record."""
    def __init__(self, ad: AppData, wnd_competency_add: ctk.CTkToplevel) -> None:
        logger.info(f"Creating Competency data add window")

        self.wnd_competency_add = wnd_competency_add
        self.ad = ad
        self.cl = CompetencyLogic(ad)

        # Add title top window
        wnd_competency_add.title("Competency Data Add")

        self.frm_attribute = ctk.CTkFrame(wnd_competency_add)
        self.frm_attribute.pack(fill='both', side='left', expand=True)

        row = 0
        self.lbl_competency_name = ctk.CTkLabel(self.frm_attribute, text="Competency Name")
        self.lbl_competency_name.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.ent_competency_name = ctk.CTkEntry(self.frm_attribute)
        self.ent_competency_name.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_scope = ctk.CTkLabel(self.frm_attribute, text="Scope")
        self.lbl_scope.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.cmb_scope = ctk.CTkComboBox(self.frm_attribute, state='readonly', values=['BOTH', 'RN', 'HCA'])
        self.cmb_scope.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_display_order = ctk.CTkLabel(self.frm_attribute, text="Display Order")
        self.lbl_display_order.grid(row=row, column=0, pady=6, padx=10, sticky='e')
        self.ent_display_order = ctk.CTkEntry(self.frm_attribute)
        self.ent_display_order.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.lbl_expiry = ctk.CTkLabel(self.frm_attribute, text="Expiry")
        self.lbl_expiry.grid(row=row, column=0, pady=6, padx=10)
        self.ent_expiry = ctk.CTkEntry(self.frm_attribute)
        self.ent_expiry.grid(row=row, column=1, pady=6, padx=10)

        row += 1
        self.chc_prerequisite = ctk.CTkCheckBox(self.frm_attribute, text="Prerequisite")
        self.chc_prerequisite.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.chc_nightshift = ctk.CTkCheckBox(self.frm_attribute, text="Nightshift")
        self.chc_nightshift.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        row += 1
        self.chc_bank = ctk.CTkCheckBox(self.frm_attribute, text="Bank")
        self.chc_bank.grid(row=row, column=1, pady=6, padx=10, sticky='w')

        # Action Buttons
        self.btn_add = ctk.CTkButton(wnd_competency_add, text="Add", command=self.handle_add_click)
        self.btn_add.pack(pady=6, padx=10)

        self.btn_exit = ctk.CTkButton(wnd_competency_add, text="Exit", command=wnd_competency_add.destroy)
        self.btn_exit.pack(pady=6, padx=10)

    def handle_add_click(self):
        """Update current record or insert a new one if it does not exist."""
        competency_name = self.ent_competency_name.get()
        scope = self.cmb_scope.get()
        display_order = self.ent_display_order.get()
        expiry = self.ent_expiry.get()
        prerequisite = self.chc_prerequisite.get()
        nightshift = self.chc_nightshift.get()
        bank = self.chc_bank.get()

        success, message = self.cl.add_competency(competency_name, scope, display_order, expiry, prerequisite, nightshift, bank)

        if success:
            CTkMessagebox(title="Information", message=message, icon='info')
        else:
            input_warning(self.wnd_competency_add, message)
