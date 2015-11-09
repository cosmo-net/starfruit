#!/usr/bin/env python
#
#       ddps.py

import re
#from datetime import datetime

from nupyst.ivr import IVR
import egobrain_tools.sqltools as _sql
import egobrain_tools.code_algorithm8 as _check8

# Static
createuser = 'IVR'
ivr_tabla = 'cervefest'


class Do_Stuff(IVR):

    def insert_stuff(self,
                     table_name,
                     dni,
                     phone,
                     email,
                     comodin,
                     createuser,
                     len_code = 8,
                     max_retries = 3):

        db = _sql.MyDbStuff('192.168.1.27', 'root', 'S13r22eqw', 'inbound_ivrs')
        
        code_count = max_retries

        while max_retries != 0:
            # input code:
            code = self.get_data('ddps/I', 20000, len_code)
            
            if len(code) <> len_code or re.search('\D', code):
                self.stream_file('ddps/Q', '""')
                max_retries -= 1
                continue
            elif _check8.checkdigit(code[0:7]) != int(code[7:8]):
                self.stream_file('ddps/Q', '""')
                max_retries -= 1
                continue                
            else:
                pass

            sp_value = (table_name, dni, code)
            reg = db.sp_return_stuff('sp_ivrs_verf_code', sp_value)

            if reg[0] == 1:
                self.stream_file('ddps/M', '""')
                max_retries -= 1
                continue
            else:
                pass
            
            sp_value = (table_name, dni, code, phone, email, comodin, createuser)
            db.sp_insert_stuff('sp_ivrs_inserta_reg', sp_value)
            
            self.stream_file('ddps/L', '""')
            
            code_count -= 1
            
            if code_count == 0:
                break
            
            result = self.ivr_fetchone('ddps/J', 'ddps/silence', '1,2')
            # ARg! more stuff!
            if '1' in result:
                pass
            else:
                break
        
        if max_retries == 0:
            self.dial_exten()
        else:
            #Do Nothing!
            pass
            

if __name__=='__main__':
    ooo = Do_Stuff()

    ooo.stream_file('ddps/A', '""')

        
    mie_identificacion = ooo.ivr_get_numeral('ddps/B', 'ddps/C', 'ddps/D',
                                  'ddps/O', 'ddps/silence', '1,2', 7)
    
    mie_phone = ooo.ivr_get_values('ddps/E', 'ddps/F', 'ddps/D',
                                   'ddps/N', 'ddps/silence', 8)

    provincia = ooo.ivr_fetchone('ddps/H', 'ddps/silence', '1,2,3,4,5,6,7')
    
    ooo.insert_stuff(ivr_tabla, mie_identificacion, mie_phone, 'ND', provincia, createuser)
    
    ooo.stream_file('ddps/K', '""')
    ooo.hangup()
