import "primereact/resources/themes/bootstrap4-dark-blue/theme.css";
import "primeicons/primeicons.css";
import "primeflex/primeflex.css";

import { useEffect, useState } from "react";
import { Card } from "primereact/card";
import { Dropdown } from "primereact/dropdown";
import { Tag } from "primereact/tag";
import SettingsForm from "./SettingsForm";
import { Button } from "primereact/button";
import { ScrollPanel } from "primereact/scrollpanel";

// Types
interface LongDistanceSensor {
    zone: string;
    currentDistance: number;
    stableDistance: number;
    readingCount: number;
    reflectionStrength: number;
    temperature: number;
    occupiedDistance: number;
    isOccupied: string;
    duration: number;
}

const severityColors = {
    0: { backgroundColor: "#444444", color: "#bbbbbb" },
    1: { backgroundColor: "#264d26", color: "#d4f8d4" },
    2: { backgroundColor: "#665c1a", color: "#f3eba0" },
    3: { backgroundColor: "#662626", color: "#f4b6b6" },
};

function formatDuration(seconds: number): string {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    const parts = [];
    if (hrs > 0) parts.push(`${hrs}h`);
    if (mins > 0) parts.push(`${mins}m`);
    if (secs > 0 || parts.length === 0)
        parts.push(`${secs}s`);

    return parts.join(" ");
}

function SensorCard({ sensor }: { sensor: LongDistanceSensor }) {
    const isOccupied = sensor.isOccupied === "OCCUPIED";
    const isEmpty = sensor.isOccupied === "EMPTY";

    // Set card color based on status
    const backgroundColor = isOccupied
        ? "#662626"
        : isEmpty
            ? "#264d26"
            : "#665c1a"; // warning/neutral

    const color = isOccupied || isEmpty ? "#fff" : "#f3eba0";

    return (
        <Card
            title={`Zone ${sensor.zone}`}
            className="mb-3"
            style={{
                backgroundColor,
                color,
            }}>
            <div className="grid">
                {/* Distance Metrics */}
                <div className="col-12 md:6">
                    <p className="m-0">
                        <strong>Immediate:</strong> {sensor.currentDistance} mm
                    </p>
                    <p className="m-0">
                        <strong>Smoothed:</strong> {sensor.stableDistance} mm
                    </p>
                    <p className="m-0">
                        <strong>Occupied Threshold:</strong>{" "}
                        {sensor.occupiedDistance} mm
                    </p>
                </div>

                {/* Status Metrics */}
                <div className="col-12 md:6">
                    <p className="m-0">
                        <strong>Status:</strong>{" "}
                        <Tag
                            value={sensor.isOccupied ?? "—"}
                            severity={
                                isOccupied
                                    ? "danger"
                                    : isEmpty
                                        ? "success"
                                        : "warning"
                            }
                        />
                    </p>
                    <p className="m-0">
                        <strong>Duration:</strong> {formatDuration(sensor.duration)}
                    </p>
                    <p className="m-0">
                        <strong>Reflection:</strong> {sensor.reflectionStrength}
                    </p>
                    <p className="m-0">
                        <strong>Temp:</strong> {sensor.temperature}°C
                    </p>
                    <p className="m-0">
                        <strong>Readings:</strong> {sensor.readingCount}
                    </p>
                </div>
            </div>
        </Card>
    );
}

const refreshIntervalOptions = [
    { label: "100 ms", value: 100 },
    { label: "250 ms", value: 250 },
    { label: "500 ms", value: 500 },
    { label: "1 second", value: 1000 },
];

// Main Dashboard
export default function StationDashboard() {
    const [sensors, setSensors] = useState<LongDistanceSensor[]>([]);
    const [rpiTime, setRpiTime] = useState<string>("");
    const [eventsQueued, setEventsQueued] = useState<number>(0);
    const [refreshInterval, setRefreshInterval] = useState<number>(250);
    const [showHelp, setShowHelp] = useState(false);

    const fetchSensorData = async () => {
        const sensorData: LongDistanceSensor[] = [];
        fetch("/status")
            .then((response) => response.json())
            .then((data) => {
                Object.entries(data.longDistanceSensors).forEach(
                    ([id, sensor]) => {
                        const s = sensor as LongDistanceSensor;
                        s.zone = id;
                        sensorData.push(s);
                    }
                );
                setSensors(sensorData);
                const [hourStr, minute] = data.rpiTime.split(":");
                let hour = parseInt(hourStr, 10);
                const ampm = hour >= 12 ? "PM" : "AM";
                hour = hour % 12 || 12;
                setRpiTime(`${hour}:${minute} ${ampm}`);
                setEventsQueued(data.eventsQueued);
            });
    };

    useEffect(() => {
        fetchSensorData();
        const id = setInterval(fetchSensorData, refreshInterval);

        return () => clearInterval(id);
    }, [refreshInterval]);

    return (
        <ScrollPanel style={{ height: "90vh" }}>

            <div
                className="p-4"
                style={{
                    display: "flex",
                    gap: "25px",
                    alignItems: "flex-start",
                }}>
                {/* Left column: Sensors */}
                <Card title={
                    <div className="flex justify-content-between align-items-center w-full">
                        <span>Sensors</span>
                        <Button
                            className="p-button-rounded p-button-text"
                            onClick={() => setShowHelp(true)}
                            tooltip="View setting descriptions"
                            tooltipOptions={{ position: "left" }}>
                            <i
                                className="pi pi-question-circle"
                                style={{ fontSize: "2rem" }}
                            />
                        </Button>
                    </div>
                } className="p-4">
                    <div
                        style={{
                            flex: 1,
                            overflowY: "auto",
                            paddingRight: "8px",
                            minWidth: "450px",
                        }}>
                        <p className="m-0">
                            <strong>Local System Time:</strong> {rpiTime || "—"}
                        </p>
                        <p className="m-0">
                            <strong>Events Queued:</strong>{" "}
                            <Tag
                                value={eventsQueued.toString()}
                                severity={eventsQueued > 0 ? "danger" : "success"}
                                style={{
                                    padding: "0.3rem 0.5rem",
                                }}
                            />
                        </p>
                        <h3 className="mb-3">Sensors</h3>
                        <div className="p-fluid surface-100 border-round shadow-1">
                            <label>Refresh Rate</label>
                            <Dropdown
                                placeholder="Refresh Rate"
                                value={refreshInterval}
                                className="mb-2"
                                options={refreshIntervalOptions}
                                onChange={(e) =>
                                    setRefreshInterval(e.value ?? 1000)
                                }
                            />
                        </div>
                        {sensors.map((s) => (
                            <SensorCard key={s.zone} sensor={s} />
                        ))}
                    </div>
                </Card>

                {/* Right column: Settings */}
                <div
                    style={{
                        width: "50%",
                        flexShrink: 0,
                    }}>
                    <SettingsForm />
                </div>
            </div>
        </ScrollPanel>
    );
}
