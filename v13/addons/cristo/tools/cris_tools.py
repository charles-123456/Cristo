from odoo import tools, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

def mobile_validation(mobile):
    """
    To Validate the single mobile no.
    Also Validate the multiple mobile no with comma separator.
    """
    mobile_list = mobile.split(',')
    for mobile in mobile_list:
        if mobile != '':
            if mobile.isnumeric():
                if len(mobile) != 10:
                    raise UserError(_("Please enter your 10 digit valid mobile number(s)"))
            else:
                raise UserError(_("Please enter only number(s)"))

def phone_validation(phone):
    """
        To Validate the single Phone no.
        Also Validate the multiple Phone no with comma separator.
        """
    phone_list = phone.split(',')
    for phone in phone_list:
        if phone != '':
            if '-' in phone:
                phone_no = phone.split('-')
                if len(phone_no) == 2:
                    if phone_no[0].isnumeric() and phone_no[-1].isnumeric():
                        if len(phone_no[0]) != 5 or len(phone_no[-1]) != 6:
                            raise UserError(_("Please enter valid Phone number(s)"))
                    else:
                        raise UserError(_("Please enter only number(s)"))
                else:
                    raise UserError(_("Please enter valid Phone number(s)"))
            else:
                if phone.isnumeric():
                    if len(phone) != 6:
                        raise UserError(_("Please enter valid Phone number(s)"))
                else:
                    raise UserError(_("Please enter only number(s)"))

def email_validation(email):
    """
    To Validate the single Email Address.
    Also Validate the multiple Email Address with comma separator. 
    """
    email_list = email.split(',')
    for email in email_list:
       if email != '':
           if email and not tools.single_email_re.match(email):
               raise UserError(_("Invalid Email Address "))

def date_validation(date_from, date_to):
    """
    Validation between dates ('date to' must be grater than 'date from')
    """
    if date_to < date_from:
        raise UserError(_("Date to should not be lesser than Date from."))
    
def future_date_validation(date,field_name='Date of Birth'):
    """
    Future Date validation
    """
    current_date = datetime.now().date()
    if date > current_date:
        raise ValidationError(_("%s cannot be futuristic.") % (field_name))

def remove_space(name):
    return name.strip()
    
    
    
    
    
      