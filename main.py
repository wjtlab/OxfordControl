from time import sleep, time
from threading import Thread
from instrument import SerialPort, default_comports
from gui import *

# Settings for appearance, updates, etc
delay_sensor = 3  # time between updates for sensors

# iTC and iPS controller settings
min_temp, max_temp = 0, 300  # minimum and maximum settings for temperature in Kelvin
min_press, max_press = 2, 20 # minimum and maximum settings for pressure in mB
max_abs_field = 7  # maximum field in Tesla

# iTC Device UIDs
uid_probe_temperature = 'DEV:DB8.T1:TEMP'
uid_vti_temperature = 'DEV:MB1.T1:TEMP'
uid_vti_pressure = 'DEV:DB5.P1:PRES'
uid_vti_pressure_set = 'DEV:DB5.P1:TEMP'

# iPS Device UIDs
uid_pt2_temperature = 'DEV:DB7.T1:TEMP'
uid_magnet_temperature = 'DEV:MB1.T1:TEMP'
uid_magnet = 'DEV:GRPZ:PSU'


def format_temperature(temperature):
    """
    The temperature controller uses four decimal places so this function takes in a number and converts it into a string

    :param temperature: (float) converts an integer/float to a string with four decimal points
    :return: string of temperature with correct decimal places
    """
    if 0 <= temperature:
        return '{:.4f}'.format(temperature)
    else:
        return str(temperature)


def format_field(field, zero=0):
    if field > 0:
        return '+{:.4f}'.format(field)
    elif field < 0:
        return '{:.4f}'.format(field)
    elif field == 0:
        if zero == 1:
            return '+0.0000'
        elif zero == -1:
            return '-0.0000'
        else:
            return '0.0000'
    else:
        return str(field)


class Application:
    def __init__(self):
        self.itc, self.ips = SerialPort(), SerialPort()  # both serial connections
        self._itc_connect, self._ips_connect = False, False  # True/False flags for each connection
        self._itc_thread, self._ips_thread = None, None  # update thread for each connection
        self._itc_delay, self._ips_delay = delay_sensor, delay_sensor  # delays between updates for each connection
        self._switch_status = SWITCH_UNKNOWN  # flag indicating current switch heater status
        self._switch_action = None  # controls countdown for switch heater on/off
        self.gui = GUI()
        self.gui.ent_itc_com.insert(tk.END, str(default_comports[0]))
        self.gui.ent_ips_com.insert(tk.END, str(default_comports[1]))
        self.gui.set_close_method(self.disconnect_all)
        self.gui.set_functions(serial_itc_connect=self.itc_connect, serial_ips_connect=self.ips_connect,
                               serial_itc_disconnect=self.itc_disconnect, serial_ips_disconnect=self.ips_disconnect,
                               set_field=self.set_magnetic_field, goto_field=self.ramp_goto_set,
                               zero_field=self.ramp_goto_zero, set_temperature=self.set_vti_temperature,
                               set_pressure=self.set_vti_pressure)
        self.gui.set_itc_frame(False)
        self.gui.set_ips_frame(False)

    def run(self):
        self.gui.mainloop()

    def itc_connect(self):
        """
        Attempts to connect to the Oxford Mercury iTC through the user-supplied COM port
        """
        self.itc.port = self.gui.ent_itc_com.get()  # read the user-supplied COM port name
        if self.itc.is_open:  # if the port is somehow open already, close it
            self.itc.close()
        if not self.itc.open():  # if open() is false then something has gone wrong
            self.gui.update_ent(self.gui.ent_itc_com, 'fail')
            self.gui.set_itc_frame(False)
            return

        self.gui.set_itc_frame(True)
        inst_name = self.itc.transmit('*IDN?', 'Error receiving iTC identification')
        if inst_name[:34] != 'IDN:OXFORD INSTRUMENTS:MERCURY ITC':
            print('Mercury iTC was not located at user-supplied COM port')
            self.gui.update_ent(self.gui.ent_itc_com, 'non-iTC fail')
            self.gui.set_itc_frame(False)
            self.itc.close()
            return
        self.gui.set_itc_frame(True)
        self._itc_thread = Thread(target=self._monitor_itc, daemon=True)
        self._itc_thread.start()

    def itc_disconnect(self):
        if self.itc.is_open:
            self.itc.close()
        self.gui.set_itc_frame(False)

    def ips_connect(self):
        """
        Attempts to connect to the Oxford Mercury iPS through the user-supplied COM port
        """
        self.ips.port = self.gui.ent_ips_com.get()  # read the user-supplied COM port name
        if self.ips.is_open:  # if the port is somehow open already, close it
            self.ips.close()
        if not self.ips.open():  # if open() is false then something has gone wrong
            self.gui.update_ent(self.gui.ent_ips_com, 'fail')
            self.gui.set_ips_frame(False)
            return

        self.gui.set_ips_frame(True)
        inst_name = self.ips.transmit('*IDN?', 'Error receiving iPS identification')
        if inst_name[:34] != 'IDN:OXFORD INSTRUMENTS:MERCURY IPS':
            print('Mercury iPS was not located at user-supplied COM port')
            self.gui.update_ent(self.gui.ent_ips_com, 'non-iPS fail')
            self.gui.set_ips_frame(False)
            self.ips.close()
            return
        switch_status = self.ips.transmit(f'READ:{uid_magnet}:SIG:SWHT').split(':')
        self._switch_status = SWITCH_UNKNOWN
        if len(switch_status) > 0:
            if switch_status[-1] == 'ON':
                self._switch_status = SWITCH_ENABLED
            elif switch_status[-1] == 'OFF':
                self._switch_status = SWITCH_DISABLED
        self.gui.set_ips_frame(True, switch_setting=self._switch_status)
        self._ips_thread = Thread(target=self._monitor_ips, daemon=True)
        self._ips_thread.start()

    def ips_disconnect(self):
        if self.ips.is_open:
            # RETURN TO FINISH HERE. SET TO HOLD THEN INTERRUPT ANY ACTION
            self.ips.close()
        self.gui.set_ips_frame(False)

    def _monitor_itc(self):
        """
        Daemon thread function to update the various iTC boxes every `_itc_delay' seconds. Does not print each message/
        response to std_out so as to prevent clutter from background monitoring operations.
        """
        while self.itc.is_open:
            # read current values
            probe_temperature = self.itc.transmit(f'READ:{uid_probe_temperature}:SIG:TEMP',
                                                  'Error reading probe temperature', False)
            vti_temperature = self.itc.transmit(f'READ:{uid_vti_temperature}:SIG:TEMP',
                                                'Error reading VTI temperature', False)
            vti_pressure = self.itc.transmit(f'READ:{uid_vti_pressure}:SIG:PRES',
                                             'Error reading VTI pressure', False)
            probe_temperature = probe_temperature.split(':')
            if len(probe_temperature) > 0:
                self.gui.update_ent(self.gui.ent_probe_temp, probe_temperature[-1])
            vti_temperature = vti_temperature.split(':')
            if len(vti_temperature) > 0:
                self.gui.update_ent(self.gui.ent_vti_temp, vti_temperature[-1])
            vti_pressure = vti_pressure.split(':')
            if len(vti_pressure) > 0:
                self.gui.update_ent(self.gui.ent_vti_press, vti_pressure[-1])

            # read set points
            probe_temperature = self.itc.transmit(f'READ:{uid_probe_temperature}:SIG:TEMP:LOOP:TSET',
                                                  'Error reading probe temperature set point',
                                                  False)
            vti_temperature = self.itc.transmit(f'READ:{uid_vti_temperature}:SIG:TEMP:LOOP:TSET',
                                                'Error reading VTI temperature set point',
                                                False)
            vti_pressure = self.itc.transmit(f'READ:{uid_vti_pressure_set}:LOOP:TSET',
                                             'Error reading VTI pressure set point',
                                             False)
            probe_temperature = probe_temperature.split(':')
            if len(probe_temperature) > 0:
                self.gui.update_ent(self.gui.ent_probe_temp_set, probe_temperature[-1])
            vti_temperature = vti_temperature.split(':')
            if len(vti_temperature) > 0:
                self.gui.update_ent(self.gui.ent_vti_temp_set, vti_temperature[-1])
            vti_pressure = vti_pressure.split(':')
            if len(vti_pressure) > 0:
                self.gui.update_ent(self.gui.ent_vti_press_set, vti_pressure[-1])
            sleep(self._itc_delay)
        # after `while' loop breaks
        return

    def _monitor_ips(self):
        """
        Daemon thread function to update the various iPS boxes every `_ips_delay' seconds. Does not print each message/
        response to std_out so as to prevent clutter from background monitoring operations.
        """
        while self.ips.is_open:
            # read current values
            pt2_temperature = self.ips.transmit(f'READ:{uid_pt2_temperature}:SIG:TEMP',
                                                'Error reading PT2 temperature', False)
            mag_temperature = self.ips.transmit(f'READ:{uid_magnet_temperature}:SIG:TEMP',
                                                'Error reading magnet temperature', False)
            mag_field = self.ips.transmit(f'READ:{uid_magnet}:SIG:FLD',
                                          'Error reading magnetic field', False)
            pt2_temperature = pt2_temperature.split(':')
            if len(pt2_temperature) > 0:
                self.gui.update_ent(self.gui.ent_pt2_temp, pt2_temperature[-1])
            mag_temperature = mag_temperature.split(':')
            if len(mag_temperature) > 0:
                self.gui.update_ent(self.gui.ent_mag_temp, mag_temperature[-1])
            mag_field = mag_field.split(':')
            if len(mag_field) > 0:
                self.gui.update_ent(self.gui.ent_curr_fld, mag_field[-1])

            # read set points
            mag_field = self.ips.transmit(f'READ:{uid_magnet}:SIG:FSET',
                                          'Error reading magnetic field set point',
                                          False)
            mag_field = mag_field.split(':')
            if len(mag_field) > 0:
                self.gui.update_ent(self.gui.ent_field_set, mag_field[-1])

            # get action info
            if self._switch_action is not None:
                if isinstance(self._switch_action, float):
                    delta_time = time() - self._switch_action
                    if delta_time <= 600:  # if it hasn't yet been ten minutes, show countdown
                        if self._switch_status == SWITCH_WARMING:
                            self.gui.update_ent(self.gui.ent_mag_action, f'Engaging {int(600 - delta_time)}')
                        elif self._switch_status == SWITCH_COOLING:
                            self.gui.update_ent(self.gui.ent_mag_action, f'Disengaging {int(600 - delta_time)}')
                    else:
                        self._switch_action = None
                else:
                    self._switch_action = time()
            else:
                action = self.ips.transmit(f'READ:{uid_magnet}:ACTN',
                                           'Error reading magnet action',
                                           False).split(':')
                if len(action) > 0:
                    self.gui.update_ent(self.gui.ent_mag_action, action[-1])
                else:
                    self.gui.update_ent(self.gui.ent_mag_action, '~')
            sleep(self._ips_delay)
        # after `while' loop breaks
        return

    def disconnect_all(self):
        self.itc.close()
        self.ips.close()
        self.gui.master.destroy()

    def set_vti_temperature(self):
        if not self.itc.is_open:
            return
        new_value = input_popup('VTI Temperature Set Point', 'Set VTI temperature: (Kelvin)').strip('K')
        try:
            new_value = float(new_value)
        except ValueError:
            new_value = -1
        self.gui.update_ent(self.gui.ent_vti_temp_set, '')
        if min_temp <= new_value <= max_temp:
            self.itc.transmit(f'SET:{uid_vti_temperature}:LOOP:TSET:{new_value}')

    def set_vti_pressure(self):
        if not self.itc.is_open:
            return
        new_value = input_popup('VTI Pressure Set Point', 'Set VTI pressure: (mB)').strip('mB')
        try:
            new_value = float(new_value)
        except ValueError:
            new_value = -1
        self.gui.update_ent(self.gui.ent_vti_press_set, '')
        if min_press <= new_value <= max_press:
            self.itc.transmit(f'SET:{uid_vti_pressure_set}:LOOP:TSET:{new_value}')

    def set_magnetic_field(self):
        if not self.ips.is_open:
            return
        new_value = input_popup('Field Set Point', 'Set field set point: (Tesla)').strip('T')
        try:
            new_value = float(new_value)
        except ValueError:
            new_value = 100  # 100 is a random invalid value designed to cause the next `if' to be false
        self.gui.update_ent(self.gui.ent_field_set, '')
        if -7.0 <= new_value <= 7.0:  # if the value is valid
            self.ips.transmit(f'SET:{uid_magnet}:SIG:FSET:{new_value}')

    def ramp_goto_set(self):
        if not self.ips.is_open or not self._switch_status == SWITCH_ENABLED:
            return
        self.ips.transmit(f'SET:{uid_magnet}:ACTN:RTOS')

    def ramp_goto_zero(self):
        if not self.ips.is_open or not self._switch_status == SWITCH_ENABLED:
            return
        self.ips.transmit(f'SET:{uid_magnet}:ACTN:RTOZ')

    def ramp_hold(self):
        if not self.ips.is_open or not self._switch_status == SWITCH_ENABLED:
            return
        self.ips.transmit(f'SET:{uid_magnet}:ACTN:HOLD')

    def toggle_switch_heater(self):
        pass


if __name__ == '__main__':
    app = Application()
    app.run()
