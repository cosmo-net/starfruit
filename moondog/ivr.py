'''
    (IVR) Interactive Voice Response.
'''
import re
import logging
from agi import AGI


class IVRException(Exception):
    '''
        IVRException
    '''
    pass


class IVRError(IVRException):
    '''
        IVRError
    '''
    pass

    
class IVRMaxTries(IVRError):
    '''
        IVRMaxTries
    '''
    pass


class IVR(AGI):

    def __init__(self):
        AGI.__init__(self)

    def max_retries(self, sounds.max_retries_hangup, max_retries.number):
        
        if max_retries == 0:
            self.stream_file(audio_max_retries_hangup, '""')
            error = 'Max tries exceeded'
            logging.error(error, max_retries)
            raise IVRMaxTries('Max tries exceeded: %s' % max_retries.number)

    def fetch_one(self, filename, sounds.max_retries_hangup,
                     escape_digits = '1,2,3', max_retries = 3):
        '''
            Send the given file, allowing playback to be interrupted by the given
            digits. Returns digit if one was pressed if any retry "max_retries" time's.
            Remember, the file extension must not be included in the filename.
        '''

        for i in range(0, max_retries):
            message = self.stream_file(filename, escape_digits)

            if str(message) in escape_digits.split(','):
                break
            else:
                max_retries -= 1

        self.ivr_max_retries(sounds.max_retries_hangup, max_retries)

        return message
    
    def get_values(self,
                       sounds.input_data, 
                       sounds.data_is,
                       sounds.data_confirmation,
                       sounds.invalid_data,
                       sounds.max_retries_hangup,
                       data_len = 9,
                       max_retries = 3):
        
        while max_retries != 0:
            message = self.get_data(sounds.input_data, 10000, data_len)
            
            if len(message) <> data_len or re.search('\D', message):
                self.stream_file(sounds.invalid_data, '""')
                max_retries -= 1
            else:
                self.stream_file(sounds.data_is, '""')
                self.say_alpha(message)
                confirm = self.ivr_fetchone(sounds.data_confirmation,
                            sounds.max_retries_hangup, '1,2', max_retries)
                
                if '1' in confirm:
                    break
                else:
                    max_retries -= 1
        
        self.max_retries(audio_max_retries_hangup, max_retries)

        return message
  
    def get_numeral(self, audio_input_data, audio_data_is,
                        audio_data_confirmation, audio_invalid_data,
                        audio_max_retries_hangup, confirmation_digits,
                        min_data_len = 9, max_data_len = 20, max_retries = 3):
        
        while max_retries != 0:
            message = self.get_data(audio_input_data, 10000, max_data_len)
            if len(message) <= min_data_len -1 or re.search('\D', message):
                self.stream_file(audio_invalid_data, '""')
                max_retries -= 1
            else:
                self.stream_file(audio_data_is, '""')
                self.say_alpha(message)
                confirm = self.ivr_fetchone(audio_data_confirmation,
                            audio_max_retries_hangup, '1,2', max_retries)
                if '1' in confirm:
                    break
                else:
                    max_retries -= 1
        
        self.max_retries(audio_max_retries_hangup, max_retries)

        return message

    def check_available_time(self, time_now, time_start, time_end):
        if int(time_now) in range(int(time_start), int(time_end)):
            return True
        else:
            return False


if __name__=='__main__':

    test_1 = IVR()
    phone = test_1.get_values('kfe/e', 'kfe/f', 'kfe/g', 'kfe/l', 8)
    test_1.say_alpha(phone)