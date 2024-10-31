import tkinter as tk
from tkinter import simpledialog

# Settings flags for magnet controller
SWITCH_ENABLED = 'enabled'
SWITCH_WARMING = 'warming'
SWITCH_COOLING = 'cooling'
SWITCH_DISABLED = 'disabled'
SWITCH_UNKNOWN = 'unknown'
FIELD_HOLD = 'hold'
FIELD_GOTO = 'goto'
FIELD_ZERO = 'zero'
FIELD_INACTIVE = 'inactive'
SETPOINT_ACTIVE = 'active'
SETPOINT_INACTIVE = 'inactive'


class GUI(tk.Frame):
    def __init__(self, master=tk.Tk()):
        super().__init__(master)
        master.title('Transue Group Oxford Control Panel')
        master.resizable(False, False)
        self.master = master
        self.pack()

        # Make function identifiers
        self.func_serial_itc_connect = None
        self.func_serial_ips_connect = None
        self.func_serial_itc_disconnect = None
        self.func_serial_ips_disconnect = None
        self.func_set_temperature = None
        self.func_get_temperature = None
        self.func_engage_switch_heater = None
        self.func_disengage_switch_heater = None
        self.func_goto_field = None
        self.func_zero_field = None
        self.func_interrupt = None
        self.func_set_field = None
        self.func_set_pressure = None

        # Make container frames
        self.frm_contents = tk.Frame(self)
        self.frm_contents.pack()
        self.lbl_itc_frame = tk.Label(self.frm_contents, text='iTC Connection')
        self.lbl_ips_frame = tk.Label(self.frm_contents, text='iPS Connection')
        self.frm_itc = tk.Frame(self.frm_contents, highlightbackground='gray', highlightthickness=1)
        self.frm_ips = tk.Frame(self.frm_contents, highlightbackground='gray', highlightthickness=1)
        self.lbl_itc_frame.grid(row=0, column=0, sticky=tk.N)
        self.lbl_ips_frame.grid(row=0, column=1, sticky=tk.N)
        self.frm_itc.grid(row=1, column=0, sticky=tk.N, padx=3, pady=1)
        self.frm_ips.grid(row=1, column=1, sticky=tk.N, padx=3, pady=1)
        input_font = 'Arial 36'

        # Make iTC frame
        self.lbl_itc_com = tk.Label(self.frm_itc, text='COM Port')
        self.ent_itc_com = tk.Entry(self.frm_itc, fg='red', bg='black', insertbackground='white',
                                    font=input_font, width=10, disabledforeground='black', disabledbackground='white',
                                    justify='center')
        self.btn_itc_com = tk.Button(self.frm_itc, text='Connect')
        self.lbl_itc_com.grid(row=0, column=0, padx=3, pady=1)
        self.ent_itc_com.grid(row=0, column=1, padx=3, pady=1)
        self.btn_itc_com.grid(row=0, column=2, padx=3, pady=1, sticky=tk.W)
        self.lbl_probe_temp = tk.Label(self.frm_itc, text='Probe Temp')
        self.ent_probe_temp = tk.Entry(self.frm_itc, fg='red', bg='black', insertbackground='white',
                                       font=input_font, width=10, disabledforeground='black',
                                       disabledbackground='white', justify='center', state='disabled')
        self.lbl_vti_temp = tk.Label(self.frm_itc, text='VTI Temp')
        self.ent_vti_temp = tk.Entry(self.frm_itc, fg='red', bg='black', insertbackground='white',
                                     font=input_font, width=10, disabledforeground='black', disabledbackground='white',
                                     justify='center', state='disabled')
        self.lbl_vti_press = tk.Label(self.frm_itc, text='VTI Press')
        self.ent_vti_press = tk.Entry(self.frm_itc, fg='red', bg='black', insertbackground='white',
                                      font=input_font, width=10, disabledforeground='black', disabledbackground='white',
                                      justify='center', state='disabled')
        self.lbl_probe_temp.grid(row=1, column=0, padx=3, pady=1)
        self.ent_probe_temp.grid(row=1, column=1, padx=3, pady=1)
        self.lbl_vti_temp.grid(row=2, column=0, padx=3, pady=1)
        self.ent_vti_temp.grid(row=2, column=1, padx=3, pady=1)
        self.lbl_vti_press.grid(row=3, column=0, padx=3, pady=1)
        self.ent_vti_press.grid(row=3, column=1, padx=3, pady=1)
        # self.lbl_probe_temp_set = tk.Label(self.frm_itc, text='Probe Temp Set')
        # self.ent_probe_temp_set = tk.Entry(self.frm_itc, fg='red', bg='black', insertbackground='white',
        #                                font=input_font, width=10, disabledforeground='black', disabledbackground='white',
        #                                justify='center', state='disabled')
        # self.btn_probe_temp_set = tk.Button(self.frm_itc, text='Set', state='disabled')
        self.lbl_vti_temp_set = tk.Label(self.frm_itc, text='VTI Temp Set')
        self.ent_vti_temp_set = tk.Entry(self.frm_itc, fg='red', bg='black', insertbackground='white',
                                     font=input_font, width=10, disabledforeground='black', disabledbackground='white',
                                     justify='center', state='disabled')
        self.btn_vti_temp_set = tk.Button(self.frm_itc, text='Set', state='disabled')
        self.lbl_vti_press_set = tk.Label(self.frm_itc, text='VTI Press Set')
        self.ent_vti_press_set = tk.Entry(self.frm_itc, fg='red', bg='black', insertbackground='white',
                                      font=input_font, width=10, disabledforeground='black', disabledbackground='white',
                                      justify='center', state='disabled')
        self.btn_vti_press_set = tk.Button(self.frm_itc, text='Set', state='disabled')
        # self.lbl_probe_temp_set.grid(row=4, column=0, padx=3, pady=1)
        # self.ent_probe_temp_set.grid(row=4, column=1, padx=3, pady=1)
        # self.btn_probe_temp_set.grid(row=4, column=2, padx=3, pady=1, sticky=tk.W)
        self.lbl_vti_temp_set.grid(row=5, column=0, padx=3, pady=1)
        self.ent_vti_temp_set.grid(row=5, column=1, padx=3, pady=1)
        self.btn_vti_temp_set.grid(row=5, column=2, padx=3, pady=1, sticky=tk.W)
        self.lbl_vti_press_set.grid(row=6, column=0, padx=3, pady=1)
        self.ent_vti_press_set.grid(row=6, column=1, padx=3, pady=1)
        self.btn_vti_press_set.grid(row=6, column=2, padx=3, pady=1, sticky=tk.W)

        # Make iPS frame
        self.lbl_ips_com = tk.Label(self.frm_ips, text='COM Port')
        self.ent_ips_com = tk.Entry(self.frm_ips, fg='red', bg='black', insertbackground='white',
                                    font=input_font, width=10, disabledforeground='black', disabledbackground='white',
                                    justify='center')
        self.btn_ips_com = tk.Button(self.frm_ips, text='Connect')
        self.lbl_ips_com.grid(row=0, column=0, padx=3, pady=1)
        self.ent_ips_com.grid(row=0, column=1, padx=3, pady=1)
        self.btn_ips_com.grid(row=0, column=2, padx=3, pady=1, sticky=tk.W)
        self.lbl_pt2_temp = tk.Label(self.frm_ips, text='PT2 Temp')
        self.ent_pt2_temp = tk.Entry(self.frm_ips, fg='red', bg='black', insertbackground='white',
                                       font=input_font, width=10, disabledforeground='black', disabledbackground='white',
                                       justify='center', state='disabled')
        self.lbl_mag_temp = tk.Label(self.frm_ips, text='Magnet Temp')
        self.ent_mag_temp = tk.Entry(self.frm_ips, fg='red', bg='black', insertbackground='white',
                                     font=input_font, width=10, disabledforeground='black', disabledbackground='white',
                                     justify='center', state='disabled')
        self.lbl_curr_fld = tk.Label(self.frm_ips, text='Current Field')
        self.ent_curr_fld = tk.Entry(self.frm_ips, fg='red', bg='black', insertbackground='white',
                                      font=input_font, width=10, disabledforeground='black', disabledbackground='white',
                                      justify='center', state='disabled')
        self.lbl_pt2_temp.grid(row=1, column=0, padx=3, pady=1)
        self.ent_pt2_temp.grid(row=1, column=1, padx=3, pady=1)
        self.lbl_mag_temp.grid(row=2, column=0, padx=3, pady=1)
        self.ent_mag_temp.grid(row=2, column=1, padx=3, pady=1)
        self.lbl_curr_fld.grid(row=3, column=0, padx=3, pady=1)
        self.ent_curr_fld.grid(row=3, column=1, padx=3, pady=1)
        self.lbl_field_set = tk.Label(self.frm_ips, text='Field Set')
        self.ent_field_set = tk.Entry(self.frm_ips, fg='red', bg='black', insertbackground='white',
                                      font=input_font, width=10, disabledforeground='black', disabledbackground='white',
                                      justify='center', state='disabled')
        self.btn_field_set = tk.Button(self.frm_ips, text='Set', state='disabled')
        self.lbl_field_set.grid(row=4, column=0, padx=3, pady=1)
        self.ent_field_set.grid(row=4, column=1, padx=3, pady=1)
        self.btn_field_set.grid(row=4, column=2, padx=3, pady=1, sticky=tk.W)
        self.lbl_mag_action = tk.Label(self.frm_ips, text='Magnet Action')
        self.ent_mag_action = tk.Entry(self.frm_ips, fg='red', bg='black', insertbackground='white',
                                       font=input_font, width=10, disabledforeground='black',
                                       disabledbackground='white', justify='center', state='disabled')
        self.lbl_mag_action.grid(row=5, column=0, padx=3, pady=1)
        self.ent_mag_action.grid(row=5, column=1, padx=3, pady=1)
        self.frm_magnet_action = tk.Frame(self.frm_ips)
        self.frm_magnet_action.grid(row=6, column=1, pady=1)
        self.btn_switch_heater = tk.Button(self.frm_magnet_action, text='Switch On/Off', state='disabled')
        self.btn_goto_set = tk.Button(self.frm_magnet_action, text='To Set', state='disabled')
        self.btn_goto_zero = tk.Button(self.frm_magnet_action, text='To Zero', state='disabled')
        self.btn_hold = tk.Button(self.frm_magnet_action, text='Hold', state='disabled')
        self.btn_switch_heater.grid(row=0, column=0, padx=3)
        self.btn_goto_set.grid(row=0, column=1, padx=3)
        self.btn_goto_zero.grid(row=0, column=2, padx=3)
        self.btn_hold.grid(row=0, column=3, padx=3)
        self.lbl_switch_heater = tk.Label(self.frm_ips, text='Current Switch Heater Status: Unknown')
        self.lbl_switch_heater.grid(row=7, column=1, pady=1)

    def set_functions(self, serial_itc_connect=None, serial_ips_connect=None,
                      serial_itc_disconnect=None, serial_ips_disconnect=None,
                      set_temperature=None, get_temperature=None,
                      engage_switch_heater=None, disengage_switch_heater=None,
                      goto_field=None, zero_field=None, interrupt=None,
                      set_field=None, set_pressure=None):
        self.func_serial_itc_connect = serial_itc_connect
        self.func_serial_ips_connect = serial_ips_connect
        self.func_serial_itc_disconnect = serial_itc_disconnect
        self.func_serial_ips_disconnect = serial_ips_disconnect
        self.func_set_temperature = set_temperature
        self.func_get_temperature = get_temperature
        self.func_engage_switch_heater = engage_switch_heater
        self.func_disengage_switch_heater = disengage_switch_heater
        self.func_goto_field = goto_field
        self.func_zero_field = zero_field
        self.func_interrupt = interrupt
        self.func_set_field = set_field
        self.func_set_pressure = set_pressure

    def set_close_method(self, command):
        self.master.protocol('WM_DELETE_WINDOW', command)

    def update_ent(self, entry_box:tk.Entry, new_text):
        state = entry_box['state']
        entry_box['state'] = 'normal'
        entry_box.delete(0, tk.END)
        entry_box.insert(tk.END, str(new_text))
        entry_box['state'] = state

    def set_itc_frame(self, connected):
        if connected:
            self.ent_itc_com['state'] = 'disabled'
            self.btn_itc_com['text'] = 'Disconnect'
            self.btn_itc_com['command'] = self.func_serial_itc_disconnect
            self.ent_probe_temp['state'] = 'readonly'
            self.ent_vti_temp['state'] = 'readonly'
            self.ent_vti_press['state'] = 'readonly'
            # self.ent_probe_temp_set['state'] = 'readonly'
            self.ent_vti_temp_set['state'] = 'readonly'
            self.ent_vti_press_set['state'] = 'readonly'
            self.btn_vti_temp_set['state'] = 'normal'
            self.btn_vti_press_set['state'] = 'normal'
            self.btn_vti_temp_set['command'] = self.func_set_temperature
            self.btn_vti_press_set['command'] = self.func_set_pressure
        else:
            self.ent_itc_com['state'] = 'normal'
            self.ent_itc_com.bind('<Return>', func=self.func_serial_itc_connect)
            self.btn_itc_com['text'] = 'Connect'
            self.btn_itc_com['command'] = self.func_serial_itc_connect
            self.ent_probe_temp['state'] = 'disabled'
            self.ent_vti_temp['state'] = 'disabled'
            self.ent_vti_press['state'] = 'disabled'
            # self.ent_probe_temp_set['state'] = 'disabled'
            self.ent_vti_temp_set['state'] = 'disabled'
            self.ent_vti_press_set['state'] = 'disabled'
            self.btn_vti_temp_set['state'] = 'disabled'
            self.btn_vti_press_set['state'] = 'disabled'

    def set_ips_frame(self, connected, switch_setting=None, action=None):
        if connected:
            self.ent_ips_com['state'] = 'disabled'
            self.btn_ips_com['text'] = 'Disconnect'
            self.btn_ips_com['command'] = self.func_serial_ips_disconnect
            self.ent_pt2_temp['state'] = 'readonly'
            self.ent_mag_temp['state'] = 'readonly'
            self.ent_curr_fld['state'] = 'readonly'
            self.ent_field_set['state'] = 'readonly'
            self.ent_mag_action['state'] = 'readonly'
            self.btn_switch_heater['state'] = 'normal'
            self.btn_field_set['state'] = 'normal'
            self.btn_field_set['command'] = self.func_set_field
            self.btn_goto_set['command'] = self.func_goto_field
            self.btn_goto_zero['command'] = self.func_zero_field
            if switch_setting == SWITCH_ENABLED:
                self.lbl_switch_heater['text'] = 'Current Switch Heater Status: Enabled'
                self.btn_switch_heater['command'] = self.func_disengage_switch_heater
                self.btn_goto_set['state'] = 'normal'
                self.btn_goto_zero['state'] = 'normal'
                self.btn_hold['state'] = 'normal'
            elif switch_setting == SWITCH_WARMING:
                self.lbl_switch_heater['text'] = 'Current Switch Heater Status: Engaging...'
                self.btn_switch_heater['command'] = self.func_disengage_switch_heater
                self.btn_goto_set['state'] = 'disabled'
                self.btn_goto_zero['state'] = 'disabled'
                self.btn_hold['state'] = 'disabled'
            elif switch_setting == SWITCH_COOLING:
                self.lbl_switch_heater['text'] = 'Current Switch Heater Status: Disengaging...'
                self.btn_switch_heater['command'] = self.func_disengage_switch_heater
                self.btn_goto_set['state'] = 'disabled'
                self.btn_goto_zero['state'] = 'disabled'
                self.btn_hold['state'] = 'disabled'
            elif switch_setting == SWITCH_UNKNOWN:
                self.lbl_switch_heater['text'] = 'Current Switch Heater Status: Unknown'
                self.btn_switch_heater['state'] = 'disabled'
                self.btn_switch_heater['command'] = self.func_disengage_switch_heater
                self.btn_goto_set['state'] = 'disabled'
                self.btn_goto_zero['state'] = 'disabled'
                self.btn_hold['state'] = 'disabled'
            else:
                self.lbl_switch_heater['text'] = 'Current Switch Heater Status: Disabled'
                self.btn_switch_heater['command'] = self.func_engage_switch_heater
                self.btn_goto_set['state'] = 'disabled'
                self.btn_goto_zero['state'] = 'disabled'
                self.btn_hold['state'] = 'disabled'
        else:
            self.ent_ips_com['state'] = 'normal'
            self.ent_ips_com.bind('<Return>', func=self.func_serial_ips_connect)
            self.btn_ips_com['text'] = 'Connect'
            self.btn_ips_com['command'] = self.func_serial_ips_connect
            self.ent_pt2_temp['state'] = 'disabled'
            self.ent_mag_temp['state'] = 'disabled'
            self.ent_curr_fld['state'] = 'disabled'
            self.ent_field_set['state'] = 'disabled'
            self.ent_mag_action['state'] = 'disabled'
            self.lbl_switch_heater['text'] = 'Current Switch Heater Status: Unknown'
            self.btn_switch_heater['state'] = 'disabled'
            self.btn_goto_set['state'] = 'disabled'
            self.btn_goto_zero['state'] = 'disabled'
            self.btn_hold['state'] = 'disabled'


def input_popup(title, prompt):
    return simpledialog.askstring(title, prompt)


if __name__ == '__main__':
    gui = GUI()
    gui.mainloop()

