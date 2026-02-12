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
            scrollHeight="flex"
            size="normal"
            value={eventData}
            tableStyle={{ minWidth: "10rem", width: "auto" }}
            style={{ width: "100%" }}>
            <Column field="event_icon" header="Type"></Column>
            <Column field="displayedStartTime" header="Event Start"></Column>
            <Column field="duration" header="Duration (m)"></Column>
        </DataTable>
    );
}
