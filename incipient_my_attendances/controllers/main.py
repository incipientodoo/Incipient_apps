# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request


class MyAttendanceController(http.Controller):

    @http.route('/my_attendances/status', type='json', auth='user')
    def get_attendance_status(self):
        employee = request.env.user.employee_id
        if not employee:
            return {'error': 'Employee not found for current user.'}
        
        return {
            'employee_name': employee.name,
            'attendance_state': employee.attendance_state,
            'hours_today': employee.hours_today,
            'last_check_in': employee.last_check_in,
            'last_check_out': employee.last_check_out,
        }

    @http.route('/my_attendances/toggle', type='json', auth='user')
    def toggle_attendance(self):
        employee = request.env.user.employee_id
        if not employee:
            return {'error': 'Employee not found for current user.'}
        
        # Toggle check in/out state
        employee._attendance_action_change()
        
        return self.get_attendance_status()
