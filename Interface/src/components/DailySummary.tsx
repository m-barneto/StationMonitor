import { Column } from "primereact/column";
import { DataTable } from "primereact/datatable";
import React, { useContext, useEffect, useState } from "react";
import { EventDataContext } from "../contexts/DataContext";
import { HourlySummary } from "../data/HourlyData";

export default function DailySummary() {
    const [dailySummary, setDailySummary] = useState([] as HourlySummary[]);
    const { eventData } = useContext(EventDataContext)!;

    useEffect(() => {
        const summary: Record<string, HourlySummary> = {};
        // Go through each event
        eventData?.forEach((e) => {
            // get the event's hour
            const bin = e.startDate.toLocaleString("en-US", {
                hour: "numeric",
                hour12: true,
            });
            if (summary[bin] == undefined) {
                summary[bin] = {
                    time: bin,
                    total_cars: 0,
                    total_duration: 0,
                    avg_duration: 0,
                };
            }

            summary[bin].total_cars += 1;
            summary[bin].total_duration += e.duration;
        });

        for (const bin in summary) {
            if (summary[bin].total_cars > 0) {
                summary[bin].avg_duration = Number(
                    (
                        summary[bin].total_duration / summary[bin].total_cars
                    ).toFixed(2)
                );
            } else {
                summary[bin].avg_duration = 0;
            }
        }

        setDailySummary(Object.values(summary));
    }, [eventData]);

    return (
        <DataTable
            showGridlines
            stripedRows
            scrollable
            removableSort
            scrollHeight="flex"
            size="normal"
            value={dailySummary}
            style={{
                width: "100%",
                paddingLeft: "1rem",
                paddingRight: "1rem",

                height: "200px",
            }}>
            <Column sortable field="time" header="Time"></Column>
            <Column sortable field="total_cars" header="Cars"></Column>
            <Column
                sortable
                field="avg_duration"
                header="Avg Time (m)"></Column>
        </DataTable>
    );
}
