/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { SearchModel } from "@web/search/search_model";
import { Domain } from "@web/core/domain";
import { serializeDate, serializeDateTime } from "@web/core/l10n/dates";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

const { DateTime } = luxon;

const FYUtils = {
    getFYYearFromMonth(date, startMonth, startDay) {
        return date.year;
    },

    getFYBounds(fyYear, startMonth, startDay) {
        const start = DateTime.local(fyYear, startMonth, startDay);
        const end = start.plus({ years: 1 }).minus({ seconds: 1 });
        return { start, end };
    },

    getQuarterBounds(fyYear, startMonth, startDay, quarter) {
        const fiscalYearStart = DateTime.local(fyYear, startMonth, startDay);
        const quarterStart = fiscalYearStart.plus({ months: (quarter - 1) * 3 });
        const nextQuarterStart = fiscalYearStart.plus({ months: quarter * 3 });
        const quarterEnd = nextQuarterStart.minus({ seconds: 1 });
        return { start: quarterStart, end: quarterEnd };
    },

    formatFY(fyYear) {
        return `FY ${fyYear}`;
    },

    formatQuarter(fyYear, startMonth, startDay, quarter) {
        const { start, end } = FYUtils.getQuarterBounds(fyYear, startMonth, startDay, quarter);
        return `Q${quarter} (${start.toFormat("MMM")} – ${end.toFormat("MMM")}) ${fyYear.toString().slice(-2)}`;
    },

    formatMonth(fyYear, startMonth, startDay, monthIndex) {
        const today = new Date();
        const currentMonth = today.getMonth();
        const currentYear = today.getFullYear();
        const offsetDate = new Date(currentYear, currentMonth + monthIndex, 1);
        const options = { month: 'long', year: 'numeric' };
        const formatted = offsetDate.toLocaleDateString("en-US", options);
        const fiscalLabel = `FY ${fyYear.toString().slice(-2)}`;
        return `${formatted} (${fiscalLabel})`;
    },
};

patch(SearchModel.prototype, {
    setup(...args) {
        super.setup(...args);
        this.orm = useService("orm");
        this.loadFiscalStartMonth();
    },

    async loadFiscalStartMonth() {
        try {
            const companyId = session.user_companies?.current_company;
            if (!companyId) {
                return;
            }

            const [companyData] = await this.orm.searchRead(
                "res.company",
                [["id", "=", companyId]],
                ["fiscalyear_last_month", "fiscalyear_last_day"]
            );

            if (!companyData) {
                return;
            }

            let fiscalEndMonth = parseInt(companyData.fiscalyear_last_month);
            let fiscalEndDay = parseInt(companyData.fiscalyear_last_day);
            const currentYear = new Date().getFullYear();

            if (fiscalEndMonth === 2) {
                const isLeap = new Date(currentYear, 1, 29).getDate() === 29;
                if (fiscalEndDay === 28 && isLeap) {
                    fiscalEndDay = 29;
                } else if (fiscalEndDay === 29 && !isLeap) {
                    fiscalEndDay = 28;
                }
            }

            const fiscalEndDate = new Date(currentYear, fiscalEndMonth - 1, fiscalEndDay);
            const fiscalStartDate = new Date(fiscalEndDate);
            fiscalStartDate.setDate(fiscalStartDate.getDate() + 1);

            this._fiscalStartMonth = fiscalStartDate.getMonth() + 1;
            this._fiscalStartDay = fiscalStartDate.getDate();
        } catch (error) {
            console.error("Failed to fetch fiscal config:", error);
        }
    },

    _getDateFilterDomain(dateFilter, generatorIds, key = "domain") {
        const { fieldName, fieldType } = dateFilter;
        const currentDate = DateTime.local();
        const startMonth = this._fiscalStartMonth;
        const startDay = this._fiscalStartDay;
        const currentFY = FYUtils.getFYYearFromMonth(currentDate, startMonth, startDay);

        const yearGens = generatorIds.filter(id => ['year', 'year-1', 'year-2'].includes(id));
        const quarterGens = generatorIds.filter(id => ['first_quarter', 'second_quarter', 'third_quarter', 'fourth_quarter'].includes(id));
        const monthGens = generatorIds.filter(id => ['month', 'month-1', 'month-2'].includes(id));

        if (key === "description") {
            return this._getFYDescription(currentFY, yearGens, quarterGens, monthGens);
        }

        const domains = [];
        const yearOffsets = { 'year': 0, 'year-1': -1, 'year-2': -2 };
        const quarterMap = { first_quarter: 1, second_quarter: 2, third_quarter: 3, fourth_quarter: 4 };

        for (const yearGen of yearGens) {
            const fyYear = currentFY + yearOffsets[yearGen];

            if (quarterGens.length > 0) {
                for (const quarterGen of quarterGens) {
                    const quarter = quarterMap[quarterGen];
                    const { start, end } = FYUtils.getQuarterBounds(fyYear, startMonth, startDay, quarter);
                    domains.push(this._makeDomain(fieldName, fieldType, start, end));
                }
            }

            if (monthGens.length > 0) {
                return super._getDateFilterDomain(dateFilter, generatorIds, key);
            }

            if (!quarterGens.length && !monthGens.length) {
                const { start, end } = FYUtils.getFYBounds(fyYear, startMonth, startDay);
                domains.push(this._makeDomain(fieldName, fieldType, start, end));
            }
        }

        return domains.length === 1 ? domains[0] : Domain.or(domains);
    },

    _getFYDescription(fyYear, yearGens, quarterGens, monthGens) {
        const startMonth = this._fiscalStartMonth;
        const startDay = this._fiscalStartDay;
        const desc = [];

        const yearOffsets = { 'year': 0, 'year-1': -1, 'year-2': -2 };
        const quarterMap = { first_quarter: 1, second_quarter: 2, third_quarter: 3, fourth_quarter: 4 };
        const monthOffsets = { 'month': 0, 'month-1': -1, 'month-2': -2 };

        for (const yearGen of yearGens) {
            const targetYear = fyYear + yearOffsets[yearGen];

            if (quarterGens.length > 0) {
                for (const quarterGen of quarterGens) {
                    desc.push(FYUtils.formatQuarter(targetYear, startMonth, startDay, quarterMap[quarterGen]));
                }
            }

            if (monthGens.length > 0) {
                for (const monthGen of monthGens) {
                    desc.push(FYUtils.formatMonth(targetYear, startMonth, startDay, monthOffsets[monthGen]));
                }
            }

            if (!quarterGens.length && !monthGens.length) {
                desc.push(FYUtils.formatFY(targetYear));
            }
        }

        return desc.join(" / ");
    },

    _makeDomain(field, type, start, end) {
        const s = type === "date" ? serializeDate(start) : serializeDateTime(start);
        const e = type === "date" ? serializeDate(end) : serializeDateTime(end);
        return new Domain(["&", [field, ">=", s], [field, "<=", e]]);
    },

    _enrichItem(searchItem) {
        try {
            const enrichedItem = super._enrichItem(searchItem);

            if (enrichedItem?.type === 'dateFilter' && enrichedItem.options) {
                const currentDate = DateTime.local();
                const startMonth = this._fiscalStartMonth;
                const startDay = this._fiscalStartDay;
                const fyYear = FYUtils.getFYYearFromMonth(currentDate, startMonth, startDay);

                enrichedItem.options = enrichedItem.options.map(option => {
                    const modifiedOption = { ...option };

                    if (['year', 'year-1', 'year-2'].includes(option.id)) {
                        const yearOffsets = { 'year': 0, 'year-1': -1, 'year-2': -2 };
                        const targetFYYear = fyYear + yearOffsets[option.id];
                        modifiedOption.description = FYUtils.formatFY(targetFYYear);
                    }

                    return modifiedOption;
                });
            }

            return enrichedItem;
        } catch (error) {
            console.warn('Error in _enrichItem:', error);
            return super._enrichItem(searchItem);
        }
    },
});
