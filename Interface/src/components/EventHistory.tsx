import React, { useContext, useEffect } from "react";
import { EventDataContext } from "../contexts/DataContext";
import { Column } from "primereact/column";
import { DataTable } from "primereact/datatable";
import { EventData } from "../data/EventData";

export default function EventHistory() {
    const { eventData, setEventData } = useContext(EventDataContext)!;

    return (
        <div style={{ width: "100%" }}>
            <div
                style={{
                    width: "100%",
                    display: "flex",
                    justifyContent: "center",
                    marginBottom: "0.5rem",
                }}
            >
                <img
                    src="/logo.png"
                    alt="Logo"
                    style={{
                        width: "100%",          // change size as you want
                        aspectRatio: "1 / 1",   // keeps it square
                        objectFit: "cover",
                        display: "block",
                    }}
                />
            </div>
            <h2 style={{ marginBottom: "0.5rem", marginTop: "0.5rem", textAlign: "center", width: "100%" }}>Event History</h2>
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
