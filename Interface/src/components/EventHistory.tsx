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
            tableStyle={{}}
            style={{ width: "100%" }}
            sortField="displayedStartTime"
            sortOrder={-1}>
            <Column field="displayedStartTime" sortable header="Start"></Column>
            <Column field="displayedDuration" sortable header="Mins"></Column>
        </DataTable>
    );
}
