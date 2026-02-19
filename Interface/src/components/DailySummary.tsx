import { Column } from "primereact/column";
import { DataTable } from "primereact/datatable";
import React, { useContext, useEffect, useState } from "react";
import { EventDataContext } from "../contexts/DataContext";
import { HourlySummary } from "../data/HourlyData";
import { formatDuration } from "../utils/Utils";

export default function DailySummary() {
    const [dailySummary, setDailySummary] = useState([] as HourlySummary[]);
    const { eventData } = useContext(EventDataContext)!;

    useEffect(() => {

        const summary: Record<string, HourlySummary> = {};

        const latestDate = new Date();
        latestDate.setMinutes(0, 0, 0);

        // 2) Pre-generate bins for the last 12 hours (including latest)
        for (let i = 11; i >= 0; i--) {
            const d = new Date(latestDate);
            d.setHours(d.getHours() - i);
            d.setMinutes(0, 0, 0);

            const bin = d.toLocaleString("en-US", {
                hour: "numeric",
                hour12: true,
            });


            summary[bin] = {
                time: bin,
                sortTime: d.getTime(),
                total_cars: 0,
                total_duration: 0,
                avg_duration: 0,
                displayedDuration: "",
            };
        }


        if (!eventData || eventData.length === 0) {
            setDailySummary(Object.values(summary));
            return;
        }
        // Go through each event
        eventData?.forEach((e) => {
            // get the event's hour
            const bin = e.startDate.toLocaleString("en-US", {
                hour: "numeric",
                hour12: true,
            });

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
                summary[bin].displayedDuration = formatDuration(summary[bin].avg_duration)
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
            scrollHeight="100%"
            size="normal"
            value={dailySummary}
            style={{
                paddingLeft: "1rem",
                paddingRight: "1rem",
                paddingBottom: "1rem",
                height: "23%"
            }}
            sortField="sortTime"
            sortOrder={-1}
        >
            <Column sortable field="time" header="Time" ></Column>
            <Column sortable field="total_cars" header="Cars"></Column>
            <Column
                sortable
                field="displayedDuration"
                header="Avg Time"></Column>
        </DataTable>
    );
}
