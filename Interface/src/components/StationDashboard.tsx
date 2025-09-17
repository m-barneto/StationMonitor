import "primereact/resources/themes/bootstrap4-dark-blue/theme.css";
import "primeicons/primeicons.css";
import "primeflex/primeflex.css";

import React, { useEffect, useState } from "react";
import { Card } from "primereact/card";
import { Button } from "primereact/button";
import { InputText } from "primereact/inputtext";
import { InputNumber } from "primereact/inputnumber";
import { Dropdown } from "primereact/dropdown";

// Types
interface LongDistanceSensor {
    currentDistance: number;
    stableDistance: number;
    readingCount: number;
    reflectionStrength: number;
    temperature: number;
    occupiedDistance: number;
    isOccupied: string;
    duration: number;
}

interface StationData {
    rpiTime: string;
    eventsQueued: string;
    isSleeping: boolean;
    reflectiveSensors: Record<string, any>;
    distanceSensors: Record<string, any>;
    longDistanceSensors: Record<string, LongDistanceSensor>;
}

export interface Sensor {
    id: string;
    name: string;
    value: number;
    unit?: string;
    status?: "ok" | "warning" | "error" | "offline";
}

// Sensor Card Component
function SensorCard({ sensor }: { sensor: Sensor }) {
    return (
        <Card className="mb-3 shadow-1" title={sensor.name}>
            <p className="m-0">
                Value: {sensor.value} {sensor.unit ?? ""}
            </p>
            <p className="m-0 text-sm text-500">
                Status: {sensor.status ?? "—"}
            </p>
        </Card>
    );
}

// Settings Form Component
function SettingsForm() {
    const [refreshRate, setRefreshRate] = useState<number>(5000);
    const [mode, setMode] = useState<string>("normal");
    const [endpoint, setEndpoint] = useState<string>("/api/sensors");
    const [submitting, setSubmitting] = useState<boolean>(false);

    const modes = [
        { label: "Normal", value: "normal" },
        { label: "Debug", value: "debug" },
        { label: "Maintenance", value: "maintenance" },
    ];

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setSubmitting(true);
        try {
            const config = { refreshRate, mode, endpoint };
            const res = await fetch("/api/settings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(config),
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            alert("Settings saved successfully");
        } catch (err: any) {
            alert(`Error saving settings: ${err.message}`);
        } finally {
            setSubmitting(false);
        }
    }

    return (
        <form
            onSubmit={handleSubmit}
            className="p-fluid p-3 surface-100 border-round shadow-1">
            <h3 className="mb-3">System Settings</h3>
            <div className="field">
                <label htmlFor="refresh">Refresh Rate (ms)</label>
                <InputNumber
                    id="refresh"
                    value={refreshRate}
                    onValueChange={(e) => setRefreshRate(e.value ?? 5000)}
                />
            </div>
            <div className="field">
                <label htmlFor="mode">Mode</label>
                <Dropdown
                    id="mode"
                    value={mode}
                    options={modes}
                    onChange={(e) => setMode(e.value)}
                    placeholder="Select Mode"
                />
            </div>
            <div className="field">
                <label htmlFor="endpoint">API Endpoint</label>
                <InputText
                    id="endpoint"
                    value={endpoint}
                    onChange={(e) => setEndpoint(e.target.value)}
                />
            </div>
            <Button
                type="submit"
                label={submitting ? "Saving..." : "Save Settings"}
                icon="pi pi-save"
                className="p-button-success mt-3"
                disabled={submitting}
            />
        </form>
    );
}

// Main Dashboard
export default function StationDashboard() {
    const [sensors, setSensors] = useState<Sensor[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const id = setInterval(() => {
            const sensorData: Sensor[] = [];
            return;
            fetch("http://192.168.17.136/status")
                .then((response) => response.json())
                .then((data) => {
                    console.log(data["data"]);
                });
            setSensors(sensorData);
            console.log(sensors);
        }, 2500);

        return () => clearInterval(id);
    });

    return (
        <div className="grid p-4 gap-4">
            <div className="col-12 md:col-8">
                <h2 className="mb-3">Sensors</h2>
                {sensors.map((s) => (
                    <SensorCard key={s.id} sensor={s} />
                ))}
            </div>
            <div className="col-12 md:col-4">
                <SettingsForm />
            </div>
        </div>
    );
}
