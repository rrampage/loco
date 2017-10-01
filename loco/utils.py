def is_int(s):
    if s is None:
        return False

    try:
        int(s)
        return True
    except ValueError:
        return False

def validate_otp(otp):
    if not otp:
        return False

    otp = str(otp)
    if len(otp) != 4 or not is_int(otp):
        return False

    return True

def validate_phone(phone):
    if not phone:
        return False

    phone = str(phone)
    if len(phone) != 10 or not is_int(phone):
        return False

    return True