import { Button } from "primereact/button";
import { Toolbar } from "primereact/toolbar";
import React from "react";

export default function Header() {
    const startContent = (
        <React.Fragment>
            <Button
                icon="pi pi-print"
                tooltip="Export Current Quest JSON"
                raised
                style={{ margin: 2 }}
            />
        </React.Fragment>
    );

    const endContent = (
        <React.Fragment>
            <Button
                icon="pi pi-plus-circle"
                severity="success"
                tooltip="New Quest"
                raised
                style={{ margin: 2 }}></Button>
            <Button
                icon="pi pi-copy"
                severity="help"
                tooltip="Duplicate Quest"
                raised
                style={{ margin: 2 }}></Button>
            <Button
                icon="pi pi-trash"
                severity="danger"
                tooltip="Remove Quest"
                raised
                style={{ margin: 2 }}></Button>
        </React.Fragment>
    );

    return (
        <Toolbar
            start={startContent}
            end={endContent}
            style={{ marginBottom: "8px" }}
        />
    );
}
