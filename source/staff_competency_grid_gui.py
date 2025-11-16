"""This module provides the functions to update Staff Competency records via
   a grid or by directly accessing records."""
import datetime
import logging
import re

import customtkinter as ctk
import tkinter as tk

from source.appdata import AppData
from source.staff_gui import StaffAssessorUpdate
from source.staff_competency_gui import StaffCompetencyUpdate
from source.tool_tip import ToolTip, competency_tip_text, role_tip_text
from source.window import child_window, date_to_string
from source.competency_display import set_display_value, staff_competency_lists

logger = logging.getLogger(__name__)


class StaffCompetencyGrid(object):
    """Generate a clickable grid of competency status for staff. This follows
       the same structure as the staff competency Excel report. If a competency
       value is clicked a window is opened to allow the user to modify it. The
       value and colour is updated to reflect this change.
       I have used tkinter label widgets as they support wrapping."""
    def __init__(self, ad: AppData, wnd_sc_grid: ctk.CTkToplevel,
                 service_code: str, staff_type: str, font_size: int = 10) -> None:
        logger.info(f"Creating Staff Competency Grid window for {service_code} {staff_type}")

        self.wnd_sc_grid = wnd_sc_grid
        self.ad = ad
        self.service_code = service_code
        self.staff_type = staff_type

        # Create a lists of Staff and Competencies for the Service Code and Staff Type combination
        self.db_s_list, self.db_c_list = staff_competency_lists(ad, service_code, staff_type)

        # Set font to TCkCustom default and size specified by user
        font = ('Roboto', font_size)
        self.font = font

        # Set dimensions for labels Tkinter uses number of characters fot height and width but pixels for wrap
        ltr_wd_pixel = 7.0 * font_size / 10  # Pixel to font size ratio
        ht_lbl = 3  # Standard height for labels
        self.ht_lbl = ht_lbl
        wt_c = 14  # Width competency labels
        wrp_c = wt_c * ltr_wd_pixel  # Wrap for competency labels
        wt_s = 15  # Width staff name labels
        wrp_s = wt_s * ltr_wd_pixel  # Wrap for staff name labels
        wt_r = 5  # Width for role code label
        self.wt_r = wt_r

        # Set canvas sizes for grid, this will set starting size for scrollable portion of window
        ht_se = 700
        wd_se = 1400

        # Add title top window
        wnd_sc_grid.title("Staff Competency Grid")

        # Define frames to split window into
        #  nw - static top left
        #  ne - header scrollable left and right
        #  sw - row labels scrollable up and down
        #  se - grid scrollable in both directions
        self.frm_nw = ctk.CTkFrame(wnd_sc_grid)
        self.frm_ne = ctk.CTkFrame(wnd_sc_grid)
        self.frm_sw = ctk.CTkFrame(wnd_sc_grid)
        self.frm_se = ctk.CTkFrame(wnd_sc_grid)

        self.frm_nw.grid(row=0, column=0, sticky='nsew')
        self.frm_ne.grid(row=0, column=1, sticky='nsew')
        self.frm_sw.grid(row=1, column=0, sticky='nsew')
        self.frm_se.grid(row=1, column=1, sticky='nsew')

        # Define scroll bars
        self.vsb = ctk.CTkScrollbar(wnd_sc_grid, orientation='vertical', command=self.scroll_vertical)
        self.hsb = ctk.CTkScrollbar(wnd_sc_grid, orientation='horizontal', command=self.scroll_horizontal)

        self.vsb.grid(row=0, column=2, rowspan=2, sticky='ns')
        self.hsb.grid(row=2, column=0, columnspan=2, sticky='ew')

        # Make grid resizeable
        wnd_sc_grid.grid_rowconfigure(1, weight=1)
        wnd_sc_grid.grid_columnconfigure(1, weight=1)

        # Canvas with internal frame for three scrollable frames
        self.cnv_ne = tk.Canvas(self.frm_ne, width=wd_se, height=0)
        self.cnv_sw = tk.Canvas(self.frm_sw, width=0, height=ht_se)
        self.cnv_se = tk.Canvas(self.frm_se, width=wd_se, height=ht_se)

        self.frm_cnv_ne = ctk.CTkFrame(self.cnv_ne)
        self.frm_cnv_sw = ctk.CTkFrame(self.cnv_sw)
        self.frm_cnv_se = ctk.CTkFrame(self.cnv_se)

        self.cnv_ne.config(yscrollcommand=self.vsb.set, highlightthickness=0)
        self.cnv_sw.config(xscrollcommand=self.hsb.set, highlightthickness=0)
        self.cnv_se.config(xscrollcommand=self.hsb.set, yscrollcommand=self.vsb.set, highlightthickness=0)

        self.cnv_ne.pack(fill='both', side='left', expand=True)
        self.cnv_sw.pack(fill='both', side='left', expand=True)
        self.cnv_se.pack(fill='both', side='left', expand=True)

        self.cnv_ne.create_window(0, 0, window=self.frm_cnv_ne, anchor='nw')
        self.cnv_sw.create_window(0, 0, window=self.frm_cnv_sw, anchor='nw')
        self.cnv_se.create_window(0, 0, window=self.frm_cnv_se, anchor='nw')

        # Bind on window configure to set scroll regions
        self.wnd_sc_grid.bind('<Configure>', self.handle_configure)

        # Bind mouse wheel for scrolling
        self.cnv_se.bind_all('<MouseWheel>', lambda e: self.handle_mousewheel(e.delta))
        self.cnv_se.bind_all('<Shift-MouseWheel>', lambda e: self.handle_mousewheel_shift(e.delta))
        self.cnv_se.bind_all('<Button-4>', lambda e: self.handle_mousewheel(120))
        self.cnv_se.bind_all('<Button-5>', lambda e: self.handle_mousewheel(-120))
        self.cnv_se.bind_all('<Shift-Button-4>', lambda e: self.handle_mousewheel_shift(120))
        self.cnv_se.bind_all('<Shift-Button-5>', lambda e: self.handle_mousewheel_shift(-120))

        # Populate nw frame - row labels
        # This will set the height of the header row and width of the row label column
        # First row
        self.lbl_staff_name = tk.Label(self.frm_nw,
                                       text="Staff Name",
                                       font=font,
                                       height=ht_lbl,
                                       width=wt_s,
                                       borderwidth=1,
                                       relief='solid',
                                       bg='#FFFFFF')
        self.lbl_staff_name.grid(row=0, column=0)
        self.lbl_staff_name.bind('<Button-1>', self.handel_staff_click)

        self.lbl_role_code = tk.Label(self.frm_nw,
                                      text="Role",
                                      font=font,
                                      height=ht_lbl,
                                      width=wt_r,
                                      borderwidth=1,
                                      relief='solid',
                                      bg='#FFFFFF')
        self.lbl_role_code.grid(row=0, column=1)

        # Second row
        self.lbl_servicer = tk.Label(self.frm_nw,
                                     text=service_code + ' - ' + staff_type,
                                     font=font,
                                     height=ht_lbl - 1,
                                     width=wt_s,
                                     borderwidth=1,
                                     relief='solid',
                                     bg='#D3D3D3')
        self.lbl_servicer.grid(row=1, column=0)
        self.lbl_blank = tk.Label(self.frm_nw,
                                  text='',
                                  font=font,
                                  height=ht_lbl - 1,
                                  width=wt_r,
                                  borderwidth=1,
                                  relief='solid',
                                  bg='#FFFFFF')
        self.lbl_blank.grid(row=1, column=1)

        # Defile labels for assessor columns
        self.lbl_assessor = None
        self.lbl_supervisor = None
        self.lbl_blank2 = None
        self.lbl_blank3 = None

        # Create 2D list to header labels
        self.lbl_header = [[], []]

        # Write header
        db_s_list, db_c_list = staff_competency_lists(ad, service_code, staff_type)
        for c, db_c in enumerate(self.db_c_list):
            # Competency name in first row of header
            self.lbl_header[0].append(tk.Label(self.frm_cnv_ne,
                                               text=ad.md.get('Competency', 'Competency Name', db_c),
                                               font=font,
                                               height=ht_lbl,
                                               width=wt_c,
                                               wraplength=wrp_c,
                                               anchor='w',
                                               justify=tk.LEFT,
                                               borderwidth=1,
                                               relief='solid',
                                               bg='#D3D3D3'))
            self.lbl_header[0][c].grid(row=0, column=c)

            tip_text = competency_tip_text(ad, db_c, db_s_list, service_code, staff_type)
            ToolTip(self.lbl_header[0][c], tip_text, y_offset=45)

            # Expiry in second row, initially put out a blank label
            self.lbl_header[1].append(tk.Label(self.frm_cnv_ne,
                                               text='',
                                               font=font,
                                               height=ht_lbl - 1,
                                               width=wt_c,
                                               wraplength=wrp_c,
                                               borderwidth=1,
                                               relief='solid',
                                               bg='#FFFFFF'))
            self.lbl_header[1][c].grid(row=1, column=c)

            # Fill in expiry label text as n Yearly or Only Once
            if ad.md.get('Competency', 'Expiry', db_c):
                self.lbl_header[1][c].config(fg='#FF0000', text=f"{ad.md.get('Competency', 'Expiry', db_c)} Yearly")
            else:
                self.lbl_header[1][c].config(text="Once Only")

        # Create list to hold row and grid labels
        self.lbl_row = []
        self.lbl_grid = []

        # Write row for each staff name
        row = -1
        last_role_code = None
        last_staff_bank = 0
        for s, db_s in enumerate(self.db_s_list):
            row += 1
            staff_name = ad.md.get('Staff', 'Staff Name', db_s)
            db_sr = ad.md.find_two('Staff Role', service_code, 'Service Code', staff_name, 'Staff Name')
            if db_sr < 0:
                continue
            role_code = ad.md.get('Staff Role', 'Role Code', db_sr)
            db_r = ad.md.find_one('Role', role_code, 'Role Code')
            staff_nightshift = ad.md.get('Staff Role', 'Nightshift', db_sr)
            staff_bank = ad.md.get('Staff Role', 'Bank', db_sr)

            # Output Bank row at start of bank staff or blank row for staff role changes.
            # I use customs tinker Labels as I can not affect the label number returned
            # in the widget when a tinker Label for a competency cell is clicked as the
            # label number is used to derive the competency.
            columns = 2
            if staff_type == 'RN':
                columns = 4
            if staff_bank and not last_staff_bank:
                msg = ctk.CTkLabel(self.frm_cnv_sw, text="\nBank\n", anchor='w', font=font, fg_color='#D3D3D3')
                msg.grid(row=row, column=0, columnspan=columns, sticky='ew')
                msg = ctk.CTkLabel(self.frm_cnv_se, text="\n\n", font=font, fg_color='#FFFFFF')
                msg.grid(row=row, column=0, columnspan=len(self.db_c_list), sticky='ew')
                row += 1
            elif last_role_code and role_code != last_role_code:
                msg = ctk.CTkLabel(self.frm_cnv_sw, text="", font=font, fg_color='#FFFFFF')
                msg.grid(row=row, column=0, columnspan=columns, sticky='ew')
                msg = ctk.CTkLabel(self.frm_cnv_se, text="", font=font, fg_color='#FFFFFF')
                msg.grid(row=row, column=0, columnspan=len(self.db_c_list), sticky='ew')
                row += 1
            last_staff_bank = staff_bank
            last_role_code = role_code

            # Write Staff Name in first column, append (nights) is their Nightshift
            # flag is set
            if staff_nightshift:
                staff_name_nightshift = staff_name + ' (nights)'
            else:
                staff_name_nightshift = staff_name
            self.lbl_row.append([])
            self.lbl_row[s].append(tk.Label(self.frm_cnv_sw,
                                            text=staff_name_nightshift,
                                            font=font,
                                            height=ht_lbl,
                                            width=wt_s,
                                            wraplength=wrp_s,
                                            anchor='w',
                                            justify=tk.LEFT,
                                            borderwidth=1,
                                            relief='solid',
                                            bg='#FFFFFF'))
            self.lbl_row[s][0].grid(row=row, column=0)

            # Write staff role in second column
            self.lbl_row[s].append(tk.Label(self.frm_cnv_sw,
                                            text=role_code,
                                            font=font,
                                            height=ht_lbl,
                                            width=wt_r,
                                            borderwidth=1,
                                            relief='solid',
                                            bg='#FFFFFF'))
            self.lbl_row[s][1].grid(row=row, column=1)
            tip_text = role_tip_text(ad, db_r, service_code)
            ToolTip(self.lbl_row[s][1], tip_text, y_offset=45)

            # Define list elements for practice assessor and supervisor
            self.lbl_row[s].append(None)
            self.lbl_row[s].append(None)

            # Loop to output all Competencies
            self.lbl_grid.append([])
            for c, db_c in enumerate(self.db_c_list):
                # Call function to set display value and colour
                display_value, colour = set_display_value(ad, service_code, db_s, db_c)
                if isinstance(display_value, datetime.date):
                    display_value = date_to_string(display_value)

                # Put display value in label and
                self.lbl_grid[s].append(tk.Label(self.frm_cnv_se,
                                                 text=display_value,
                                                 font=font,
                                                 height=ht_lbl,
                                                 width=wt_c,
                                                 wraplength=wrp_c,
                                                 borderwidth=1,
                                                 relief='solid',
                                                 bg=colour))
                self.lbl_grid[s][c].grid(row=row, column=c)
                self.lbl_grid[s][c].bind('<Button-1>', self.handel_grid_click)

        # Display practice assessor and supervisor row label columns for RN grids
        self.assessor_displayed = False
        if staff_type == 'RN':
            self.assessor_displayed = True
            self.display_assessor()

    def display_assessor(self):

        self.lbl_assessor = tk.Label(self.frm_nw,
                                     text="Asses",
                                     font=self.font,
                                     height=self.ht_lbl,
                                     width=self.wt_r,
                                     borderwidth=1,
                                     relief='solid',
                                     bg='#FFFFFF')
        self.lbl_assessor.grid(row=0, column=2)

        self.lbl_supervisor = tk.Label(self.frm_nw,
                                       text="Super",
                                       font=self.font,
                                       height=self.ht_lbl,
                                       width=self.wt_r,
                                       borderwidth=1,
                                       relief='solid',
                                       bg='#FFFFFF')
        self.lbl_supervisor.grid(row=0, column=3)

        self.lbl_blank2 = tk.Label(self.frm_nw,
                                   text='',
                                   font=self.font,
                                   height=self.ht_lbl - 1,
                                   width=self.wt_r,
                                   borderwidth=1,
                                   relief='solid',
                                   bg='#FFFFFF')
        self.lbl_blank2.grid(row=1, column=2)

        self.lbl_blank3 = tk.Label(self.frm_nw,
                                   text='',
                                   font=self.font,
                                   height=self.ht_lbl - 1,
                                   width=self.wt_r,
                                   borderwidth=1,
                                   relief='solid',
                                   bg='#FFFFFF')
        self.lbl_blank3.grid(row=1, column=3)

        row = -1
        last_role_code = None
        last_staff_bank = 0
        for s, db_s in enumerate(self.db_s_list):
            row += 1

            staff_name = self.ad.md.get('Staff', 'Staff Name', db_s)
            db_sr = self.ad.md.find_two('Staff Role', self.service_code, 'Service Code', staff_name, 'Staff Name')
            if db_sr < 0:
                continue
            role_code = self.ad.md.get('Staff Role', 'Role Code', db_sr)
            staff_bank = self.ad.md.get('Staff Role', 'Bank', db_sr)

            if staff_bank and not last_staff_bank or last_role_code and role_code != last_role_code:
                row += 1
            last_staff_bank = staff_bank
            last_role_code = role_code

            # Add columns to row title for RNs for Assessor and Supervisor
            assessor = self.ad.md.get('Staff', 'Practice Assessor', db_s)
            supervisor = self.ad.md.get('Staff', 'Practice Supervisor', db_s)

            if assessor:
                assessor_txt = 'Y'
            else:
                assessor_txt = ''
            self.lbl_row[s][2] = tk.Label(self.frm_cnv_sw,
                                          text=assessor_txt,
                                          font=self.font,
                                          height=self.ht_lbl,
                                          width=self.wt_r,
                                          borderwidth=1,
                                          relief='solid',
                                          bg='#FFFFFF')
            self.lbl_row[s][2].grid(row=row, column=2)
            self.lbl_row[s][2].bind('<Button-1>', self.handel_assessor_click)

            if supervisor:
                supervisor_txt = 'Y'
            else:
                supervisor_txt = ''
            self.lbl_row[s][3] = tk.Label(self.frm_cnv_sw,
                                          text=supervisor_txt,
                                          font=self.font,
                                          height=self.ht_lbl,
                                          width=self.wt_r,
                                          borderwidth=1,
                                          relief='solid',
                                          bg='#FFFFFF')
            self.lbl_row[s][3].grid(row=row, column=3)
            self.lbl_row[s][3].bind('<Button-1>', self.handel_assessor_click)

    def scroll_horizontal(self, *args):
        """Scroll horizontally."""
        self.cnv_se.xview(*args)
        self.cnv_ne.xview(*args)

    def scroll_vertical(self, *args):
        """Scroll vertically."""
        self.cnv_se.yview(*args)
        self.cnv_sw.yview(*args)

    # noinspection PyUnusedLocal
    def handle_configure(self, event):
        """On window configure set frame scroll regions."""
        self.cnv_ne.config(scrollregion=self.frm_cnv_ne.bbox())
        self.cnv_sw.config(scrollregion=self.frm_cnv_sw.bbox())
        self.cnv_se.config(scrollregion=self.frm_cnv_se.bbox())

    def handle_mousewheel(self, event):
        """Scroll vertically for mouse wheel."""
        self.cnv_se.yview_scroll(int(-1 * (event / 120)), 'units')
        self.cnv_sw.yview_scroll(int(-1 * (event / 120)), 'units')

    def handle_mousewheel_shift(self, event):
        """Scroll horizontally for mouse wheel."""
        self.cnv_ne.xview_scroll(int(-1 * (event / 120)), 'units')
        self.cnv_se.xview_scroll(int(-1 * (event / 120)), 'units')

    def handel_assessor_click(self, event):
        """When a staff members assessor or supervisor cell is clicked open
           a window to allow user to set these values for the staff member."""
        # Extract label number from widget
        label_num_search = re.search(r'label(\d+)', str(event.widget))
        if not label_num_search:
            logger.error(f"Failed to extract label number from event widget [{event.widget}]")
            return
        label_num = int(label_num_search.group(1))

        # The labels for all staff name and role are created first then for each refresh of the practice columns for
        # each staff name a pair for practice assessor and supervisor labels are created. So the modulus twice the
        # number of customers of the label number plus one divided by 2 gives the row number.
        s = int((label_num % (2 * len(self.db_s_list)) + 1) / 2) - 1
        staff_name = self.ad.md.get('Staff', 'Staff Name', self.db_s_list[s])

        # Invoke child widow to allow user to update the Practice Assessor status
        child_window(StaffAssessorUpdate, self.ad, self.wnd_sc_grid, staff_name)

        # Update the values of Practice Assessor and Supervisor in the row label as they may have changed
        if self.ad.md.get('Staff', 'Practice Assessor', self.db_s_list[s]):
            self.lbl_row[s][2].configure(text='Y')
        else:
            self.lbl_row[s][2].configure(text='')

        if self.ad.md.get('Staff', 'Practice Supervisor', self.db_s_list[s]):
            self.lbl_row[s][3].configure(text='Y')
        else:
            self.lbl_row[s][3].configure(text='')

    def handel_staff_click(self, event: object):
        """When staff header is clicked display or hide assessor and supervisor columns."""
        logger.debug(f"handel_staff_click called for staff type {self.staff_type} with event: {event}")
        if self.staff_type != 'RN':
            return

        if not self.assessor_displayed:
            self.display_assessor()
            self.assessor_displayed = True
        else:
            self.lbl_assessor.destroy()
            self.lbl_supervisor.destroy()
            self.lbl_blank2.destroy()
            self.lbl_blank3.destroy()
            for s, db_s in enumerate(self.db_s_list):
                self.lbl_row[s][2].destroy()
                self.lbl_row[s][3].destroy()
            self.assessor_displayed = False

    def handel_grid_click(self, event):
        """ When a cell is clicked calls the window for the user to update a
            Staff Competency record. It extracts the number of the label from
            the event widget. This is then used to calculate the index into the
            staff name list and the competency name list. The numbers go up
            sequential from the top left hand corner of the grid."""
        # Extract label number from widget
        label_num_search = re.search(r'label(\d+)?', str(event.widget))
        if not label_num_search:
            logger.error(f"Failed to extract label number from event widget [{event.widget}]")
            return

        # First label has no number
        if not label_num_search.group(1):
            label_num = 1
        else:
            label_num = int(label_num_search.group(1))

        # The staff index is simply label number minus one divided by the
        # number of competencies rounded down
        s = int((label_num - 1) / len(self.db_c_list))

        # Use modules number of the number of competencies the label
        # number to set the competency index
        # 0 is a special case as this is the last column
        if label_num % len(self.db_c_list) == 0:
            c = len(self.db_c_list) - 1
        else:
            c = label_num % len(self.db_c_list) - 1

        logger.debug(f"Clicked widget {str(event.widget)}, label number{label_num}, staff index {c}"
                     f" of {len(self.db_s_list)} competency {s} of {len(self.db_c_list)}")

        # Create child to allow user to review and update Staff Competency
        staff_name = self.ad.md.get('Staff', 'Staff Name', self.db_s_list[s])
        competency_name = self.ad.md.get('Competency', 'Competency Name', self.db_c_list[c])
        child_window(StaffCompetencyUpdate, self.ad, self.wnd_sc_grid, staff_name, competency_name)

        # The Staff Competency may have been updated so update cell
        display_value, colour = set_display_value(self.ad, self.service_code, self.db_s_list[s], self.db_c_list[c])
        if isinstance(display_value, datetime.date):
            display_value = date_to_string(display_value)
        self.lbl_grid[s][c].config(text=display_value, bg=colour)
