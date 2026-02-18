import React, { useContext, useEffect } from "react";
import { EventDataContext } from "../contexts/DataContext";
import { Column } from "primereact/column";
import { DataTable } from "primereact/datatable";
import { EventData } from "../data/EventData";

export default function EventHistory() {
    const { eventData, setEventData } = useContext(EventDataContext)!;

    return (
        <div>
            <h2 style={{ marginBottom: "0.5rem" }}>Event History</h2>
            <DataTable
                scrollable
                scrollHeight="100%"
                size="normal"
                value={eventData}
                tableStyle={{}}
                style={{ width: "100%" }}
                sortField="startTimeNumeric"
                sortOrder={-1}>
                <Column field="displayedStartTime" sortable header="Start"></Column>
                <Column field="displayedDuration" sortable header="Time"></Column>
            </DataTable>
        </div>
    );
}
