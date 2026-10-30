/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

export class MyAttendances extends Component {
    setup() {
        this.notification = useService("notification");
        
        this.state = useState({
            employeeName: "",
            attendanceState: "checked_out",
            hoursToday: 0,
            error: null,
            loading: true,
            processing: false,
        });

        onWillStart(async () => {
            await this.loadAttendanceStatus();
        });
    }

    async loadAttendanceStatus() {
        try {
            const result = await rpc("/my_attendances/status", {});
            if (result.error) {
                this.state.error = result.error;
            } else {
                this.state.employeeName = result.employee_name;
                this.state.attendanceState = result.attendance_state;
                this.state.hoursToday = result.hours_today || 0;
                this.state.error = null;
            }
        } catch (error) {
            this.state.error = "Could not fetch attendance status.";
        } finally {
            this.state.loading = false;
        }
    }

    async toggleAttendance() {
        if (this.state.processing) {
            return;
        }
        this.state.processing = true;
        try {
            const result = await rpc("/my_attendances/toggle", {});
            if (result.error) {
                this.notification.add(result.error, { type: "danger" });
            } else {
                this.state.employeeName = result.employee_name;
                this.state.attendanceState = result.attendance_state;
                this.state.hoursToday = result.hours_today || 0;
                const stateText = this.state.attendanceState === 'checked_in' ? 'Checked In' : 'Checked Out';
                this.notification.add(`Successfully ${stateText}`, { type: "success" });
            }
        } catch (error) {
            let errorMsg = "An unexpected error occurred while processing your attendance.";
            if (error && error.data && error.data.message) {
                errorMsg = error.data.message;
            } else if (error && error.message) {
                errorMsg = error.message;
            }
            this.notification.add(errorMsg, { type: "danger" });
        } finally {
            this.state.processing = false;
        }
    }
}

MyAttendances.template = "incipient_my_attendances.MyAttendancesTemplate";
registry.category("actions").add("incipient_my_attendances.MyAttendances", MyAttendances);
