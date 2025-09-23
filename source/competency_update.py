"""This module contains the routines to manage the Competency table."""
import logging

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

from source.appdata import AppData
from source.window import child_window, set_disabled_checkbox, set_disabled_entry, input_warning

logger = logging.getLogger(__name__)


class CompetencyUpdate(object):
    """Window to allow user to update Competency data. The data is presented as a table."""
    def __init__(self, ad: AppData, wnd_competency: ctk.CTkToplevel) -> None:
        logger.info("Creating Competency data update window")

        self.wnd_competency = wnd_competency
        self.ad = ad

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
        self.ent_display_order = []
        self.ent_competency_name = []
        self.cmb_scope = []
        self.ent_expiry = []
        self.chc_prerequisite = []
        self.chc_nightshift = []
        self.chc_bank = []

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
        # Validate integer attributes
        for db_c in range(self.ad.md.len('Competency')):
            if not self.ent_display_order[db_c].get().isdigit():
                input_warning(self.wnd_competency, "Display Order field must be integer!")
                return
            if self.ent_expiry[db_c].get() and not self.ent_expiry[db_c].get().isdigit():
                input_warning(self.wnd_competency, "Expiry field must be integer or blank!")
                return

        # Check every value to see if it has changed
        number_changes = 0
        for db_c in range(self.ad.md.len('Competency')):
            # Propagate Competency Name changes to foreign keys in other tables
            if self.ad.md.get('Competency', 'Competency Name', db_c) != self.ent_competency_name[db_c].get():
                self.ad.master_updated = True
                old = self.ad.md.get('Competency', 'Competency Name', db_c)
                new = self.ent_competency_name[db_c].get()
                self.ad.md.replace('Role Competency', 'Competency Name', old, new)
                self.ad.md.replace('Staff Competency', 'Competency Name', old, new)

            if self.ent_expiry[db_c].get():
                expiry = int(self.ent_expiry[db_c].get())
            else:
                expiry = ''
            if (self.ad.md.get('Competency', 'Competency Name', db_c) != self.ent_competency_name[db_c].get()
                    or self.ad.md.get('Competency', 'Display Order', db_c) != int(self.ent_display_order[db_c].get())
                    or self.ad.md.get('Competency', 'Scope', db_c) != self.cmb_scope[db_c].get()
                    or self.ad.md.get('Competency', 'Prerequisite', db_c) != self.chc_prerequisite[db_c].get()
                    or self.ad.md.get('Competency', 'Nightshift', db_c) != self.chc_nightshift[db_c].get()
                    or self.ad.md.get('Competency', 'Bank', db_c) != self.chc_bank[db_c].get()):
                number_changes += 1
                self.ad.master_updated = True
                self.ad.md.update_row('Competency', db_c, {'Competency Name': self.ent_competency_name[db_c].get(),
                                                           'Display Order': int(self.ent_display_order[db_c].get()),
                                                           'Scope': self.cmb_scope[db_c].get(),
                                                           'Expiry': expiry,
                                                           'Prerequisite': self.chc_prerequisite[db_c].get(),
                                                           'Nightshift': self.chc_nightshift[db_c].get(),
                                                           'Bank': self.chc_bank[db_c].get()})

        CTkMessagebox(title="Information", message=f"{number_changes} changes saved", icon='info')

        # Sort table and fresh display
        if number_changes > 0:
            self.ad.md.sort_table('Competency')
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
        for i in range(len(self.ent_display_order) - self.ad.md.len('Competency')):
            # Remove last row of widgets
            self.ent_display_order[-1].destroy()
            self.ent_display_order.pop()
            self.ent_competency_name[-1].destroy()
            self.ent_competency_name.pop()
            self.cmb_scope[-1].destroy()
            self.cmb_scope.pop()
            self.ent_expiry[-1].destroy()
            self.ent_expiry.pop()
            self.chc_prerequisite[-1].destroy()
            self.chc_prerequisite.pop()
            self.chc_nightshift[-1].destroy()
            self.chc_nightshift.pop()
            self.chc_bank[-1].destroy()
            self.chc_bank.pop()

        # Re-display table
        self.display_competency_table()

    def display_competency_table(self) -> None:
        """Display widgets for all competency records"""
        for db_c in range(self.ad.md.len('Competency')):
            self.add_competency_to_display(db_c)

    def add_competency_to_display(self, db_c: int) -> None:
        """Display a row of widgets for a specified Competency table index."""
        # If the index is beyond what is already in the widget lists append new widgets
        if db_c + 1 > len(self.ent_display_order):
            col = 0
            self.ent_display_order.append(ctk.CTkEntry(self.frm_s, width=self.width[col]))
            self.ent_display_order[db_c].grid(row=db_c + 1, column=col, sticky='w')

            col += 1
            self.ent_competency_name.append(ctk.CTkEntry(self.frm_s, width=self.width[col]))
            self.ent_competency_name[db_c].grid(row=db_c + 1, column=col, sticky='w')

            col += 1
            self.cmb_scope.append(ctk.CTkComboBox(self.frm_s, width=self.width[col],
                                                  state='readonly', values=['BOTH', 'RN', 'HCA']))
            self.cmb_scope[db_c].grid(row=db_c + 1, column=col, sticky='w')

            col += 1
            self.ent_expiry.append(ctk.CTkEntry(self.frm_s, width=self.width[col]))
            self.ent_expiry[db_c].grid(row=db_c + 1, column=col, sticky='w')

            col += 1
            self.chc_prerequisite.append(ctk.CTkCheckBox(self.frm_s,
                                                         width=self.width[col] - 2 * int(self.width[col] / 3), text=""))
            self.chc_prerequisite[db_c].grid(row=db_c + 1, column=col, sticky='nsew', padx=int(self.width[col] / 3))

            col += 1
            self.chc_nightshift.append(ctk.CTkCheckBox(self.frm_s,
                                                       width=self.width[col] - 2 * int(self.width[col] / 3), text=""))
            self.chc_nightshift[db_c].grid(row=db_c + 1, column=col, sticky='nsew', padx=int(self.width[col] / 3))

            col += 1
            self.chc_bank.append(ctk.CTkCheckBox(self.frm_s,
                                                 width=self.width[col] - 2 * int(self.width[col] / 3), text=""))
            self.chc_bank[db_c].grid(row=db_c + 1, column=col, sticky='nsew', padx=int(self.width[col] / 3))

        # Set all widget values
        self.ent_display_order[db_c].delete(0, 9999)
        self.ent_display_order[db_c].insert(0, self.ad.md.get('Competency', 'Display Order', db_c))

        self.ent_competency_name[db_c].delete(0, 9999)
        self.ent_competency_name[db_c].insert(0, self.ad.md.get('Competency', 'Competency Name', db_c))

        self.cmb_scope[db_c].set(self.ad.md.get('Competency', 'Scope', db_c))

        self.ent_expiry[db_c].delete(0, 9999)
        self.ent_expiry[db_c].insert(0, self.ad.md.get('Competency', 'Expiry', db_c))

        if self.ad.md.get('Competency', 'Prerequisite', db_c):
            self.chc_prerequisite[db_c].select()
        else:
            self.chc_prerequisite[db_c].deselect()

        if self.ad.md.get('Competency', 'Nightshift', db_c):
            self.chc_nightshift[db_c].select()
        else:
            self.chc_nightshift[db_c].deselect()

        if self.ad.md.get('Competency', 'Bank', db_c):
            self.chc_bank[db_c].select()
        else:
            self.chc_bank[db_c].deselect()


class CompetencyDelete(object):
    """Window to allow user to delete Competency data records."""
    def __init__(self, ad: AppData, wnd_competency_del: ctk.CTkToplevel) -> None:
        logger.info(f"Creating Competency data delete window")

        self.wnd_competency_del = wnd_competency_del
        self.ad = ad

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
        # Identify selected competency
        competency_name = self.cmb_competency_name.get()
        if not competency_name:
            return
        db_c = self.ad.md.index('Competency', 'Competency Name', competency_name)

        # Warn that dependent rows will be deleted
        rc_cnt = self.ad.md.count('Role Competency', 'Competency Name', competency_name)
        sc_cnt = self.ad.md.count('Staff Competency', 'Competency Name', competency_name)
        if rc_cnt or sc_cnt:
            warn_text = (f"{competency_name} is used {rc_cnt} times in Role Competency"
                         f" and {sc_cnt} times in Staff Competency")
            msg = CTkMessagebox(title="Dependent Record Warning", message=warn_text,
                                icon='warning', option_1='Delete', option_2='Cancel')
            if msg.get() != 'Delete':
                return

        # Delete row and dependent rows, note deletes not audited
        self.ad.master_updated = True
        self.ad.md.delete_row('Competency', db_c)

        # Delete entries for Competency Name in Role Competency table
        self.ad.md.delete_value('Role Competency', 'Competency Name', competency_name)

        # Delete entries for Competency Name in Staff Competency table
        self.ad.md.delete_value('Staff Competency', 'Competency Name', competency_name)

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
        if not competency_name:
            input_warning(self.wnd_competency_add, "Competency Name field must be set!")
            return
        elif display_order and not str(display_order).isdigit():
            input_warning(self.wnd_competency_add, "Display Order field must be an integer!")
            return
        elif expiry and not str(expiry).isdigit():
            input_warning(self.wnd_competency_add, "Expiry field must be blank or an integer!")
            return

        # If display order not set then set it to be after last row
        if not display_order:
            display_order = self.ad.md.get('Competency', 'Display Order', self.ad.md.len('Competency') - 1) + 1
        else:
            display_order = int(display_order)

        if expiry:
            expiry = int(expiry)

        try:
            self.ad.md.index('Competency', 'Competency Name', competency_name)
        except IndexError:
            self.ad.master_updated = True
            self.ad.md.add_row('Competency', {'Competency Name': competency_name,
                                              'Scope': scope,
                                              'Display Order': display_order,
                                              'Expiry': expiry,
                                              'Prerequisite': prerequisite,
                                              'Nightshift': nightshift,
                                              'Bank': bank})
            CTkMessagebox(title="Information", message=f"Added {competency_name}", icon='info')
        else:
            input_warning(self.wnd_competency_add, f"Competency Name {competency_name} already defined!")
