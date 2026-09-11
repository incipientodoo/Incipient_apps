/** @odoo-module **/

/**
 * Global patch for Odoo 19:
 * Rename the Group-By date interval "Year" -> "Fiscal Year" and "Quarter" -> "Fiscal Quarter"
 * everywhere in the backend UI.
 */
import { INTERVAL_OPTIONS } from "@web/search/utils/dates";

if (INTERVAL_OPTIONS.year) {
    INTERVAL_OPTIONS.year.description = "Fiscal Year";
}

if (INTERVAL_OPTIONS.quarter) {
    INTERVAL_OPTIONS.quarter.description = "Fiscal Quarter";
}
