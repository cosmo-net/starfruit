#!/usr/bin/env python
#
"""(IVR) Interactive Voice Response.

This module contains functions and classes to development IVR Promotions with AGI scripts in python.

"""
import re
import agitb
from agi import AGI

class IVRException(Exception):
    pass

class IVRError(IVRException):
    pass
    
class IVRMaxTries(IVRError):
    pass

class IVR(AGI):

    def __init__(self):
        AGI.__init__(self)

    def ivr_max_retries(self, audio_max_retries_hangup, max_retries):
        if max_retries == 0:
            self.stream_file(audio_max_retries_hangup, '""')
            agitb.handler()
            raise IVRMaxTries('Max tries exceeded: %s' % max_retries)
        else:
            pass

    def ivr_fetchone(self, filename, audio_max_retries_hangup,
                     escape_digits = '1,2,3', max_retries = 3):

        """
        Send the given file, allowing playback to be interrupted by the given
        digits. Returns digit if one was pressed if any retry "max_retries" time's.
        Remember, the file extension must not be included in the filename.
        """

        for i in range(0, max_retries):
            result = self.stream_file(filename, escape_digits)

            if str(result) in escape_digits.split(','):
                break
            else:
                max_retries -= 1

        self.ivr_max_retries(audio_max_retries_hangup, max_retries)

        return result
    
    def ivr_get_values(self, audio_input_data, audio_data_is,
                       audio_data_confirmation, audio_invalid_data,
                       audio_max_retries_hangup, data_len = 9, max_retries = 3):
        while max_retries != 0:
            result = self.get_data(audio_input_data, 10000, data_len)
            if len(result) <> data_len or re.search('\D', result):
                self.stream_file(audio_invalid_data, '""')
                max_retries -= 1
            else:
                self.stream_file(audio_data_is, '""')
                self.say_alpha(result)
                confirm = self.ivr_fetchone(audio_data_confirmation,
                            audio_max_retries_hangup, '1,2', max_retries)
                if '1' in confirm:
                    break
                else:
                    max_retries -= 1
        self.ivr_max_retries(audio_max_retries_hangup, max_retries)

        return result
            
    def ivr_get_numeral(self, audio_input_data, audio_data_is,
                        audio_data_confirmation, audio_invalid_data,
                        audio_max_retries_hangup, confirmation_digits,
                        min_data_len = 9, max_data_len = 20, max_retries = 3):
        while max_retries != 0:
            result = self.get_data(audio_input_data, 10000, max_data_len)
            if len(result) <= min_data_len -1 or re.search('\D', result):
                self.stream_file(audio_invalid_data, '""')
                max_retries -= 1
            else:
                self.stream_file(audio_data_is, '""')
                self.say_alpha(result)
                confirm = self.ivr_fetchone(audio_data_confirmation,
                            audio_max_retries_hangup, '1,2', max_retries)
                if '1' in confirm:
                    break
                else:
                    max_retries -= 1
        self.ivr_max_retries(audio_max_retries_hangup, max_retries)

        return result

    def ivr_check_available_time(self, time_now, time_start, time_end):
        if int(time_now) in range(int(time_start), int(time_end)):
            return True
        else:
            return False


if __name__=='__main__':
    prueba = IVR()
    agitb.enable(prueba, False, '/root/')
    mie_telefono = prueba.ivr_get_values('kfe/e', 'kfe/f', 'kfe/g', 'kfe/l', 8)
    prueba.say_alpha(mie_telefono)

