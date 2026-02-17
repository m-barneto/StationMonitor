import React, { useContext, useEffect } from "react";
import { EventDataContext } from "../contexts/DataContext";
import { Column } from "primereact/column";
import { DataTable } from "primereact/datatable";
import { EventData } from "../data/EventData";

export default function EventHistory() {
    const { eventData, setEventData } = useContext(EventDataContext)!;

    return (
        <DataTable
            scrollable
            scrollHeight="100%"
            size="normal"
            value={eventData}
            tableStyle={{ width: "10rem" }}
            style={{ width: "100%" }}
            sortField="displayedStartTime"
            sortOrder={-1}>
            <Column field="event_icon" header="Type"></Column>
            <Column field="displayedStartTime" sortable header="Event Start"></Column>
            <Column field="duration" sortable header="Duration (m)"></Column>
        </DataTable>
    );
}
