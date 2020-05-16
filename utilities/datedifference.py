from datetime import datetime
import math

def date_difference(pastest, presentest=None, offset=None):
    if presentest:
        dt = presentest - pastest
        offset = dt.seconds + (dt.days * 60*60*24)

    if offset:
        delta_s = math.trunc(offset % 60)
        offset /= 60
        delta_mi = math.trunc(offset % 60)
        offset /= 60
        delta_h = math.trunc(offset % 24)
        offset /= 24
        delta_d = math.trunc(offset % 30)
        offset /= 30
        delta_mo = math.trunc(offset % 12)
        offset /= 12
        delta_y = math.trunc(offset)
    
    else:
        raise(ValueError("Must supply otherdate or offset (from now)"))
    
    if delta_y >= 1:
        return(f'{delta_y} year(s), {delta_mo} month(s), {delta_d} day(s)')   
    if delta_mo >= 1:
        return(f'{delta_mo} month(s), {delta_d} day(s), {delta_h} hour(s)')
    if delta_d >= 1:
        return(f'{delta_d} day(s), {delta_h} hour(s), {delta_mi} minute(s)')
    if delta_h >= 1:
        return(f'{delta_h} hour(s), {delta_mi} minute(s), {delta_s} second(s)')
    if delta_mi >= 1:
        return(f'{delta_mi} minute(s), {delta_s} second(s)')
    else:
        return(f'{delta_s} second(s)')
