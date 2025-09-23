import "primereact/resources/themes/bootstrap4-dark-blue/theme.css";
import "primeicons/primeicons.css";
import "primeflex/primeflex.css";

import { useEffect, useState } from "react";
import { Card } from "primereact/card";
import { Dropdown } from "primereact/dropdown";
import { Tag } from "primereact/tag";
import SettingsForm from "./SettingsForm";

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

// Sensor Card Component
function SensorCardOld({ sensor }: { sensor: LongDistanceSensor }) {
    const colorSeverity = sensor.isOccupied === "EMPTY" ? 1 : 2; // 2 or 3 if alarmed
    const styles = {
        backgroundColor: severityColors[colorSeverity]?.backgroundColor,
        color: severityColors[colorSeverity]?.color,
    };
    return (
        <Card
            className="mb-3 shadow-1"
            title={sensor.zone}
            style={{
                backgroundColor: styles.backgroundColor,
                color: styles.color,
            }}>
            <p className="m-0">
                Immediate Distance: {sensor.currentDistance} mm
            </p>
            <p className="m-0">Smoothed Distance: {sensor.stableDistance} mm</p>
            <p className="m-0">
                Occupied Distance Threshold: {sensor.occupiedDistance}
            </p>
            <p className="m-0">Status: {sensor.isOccupied ?? "—"}</p>
            <p className="m-0">
                Reflection Strength: {sensor.reflectionStrength}
            </p>
        </Card>
    );
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
                        <strong>Duration:</strong> {sensor.duration}s
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

    const fetchSensorData = async () => {
        const sensorData: LongDistanceSensor[] = [];
        fetch("http://192.168.17.136/status")
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
        <div
            className="p-4"
            style={{
                display: "flex",
                height: "100vh",
                gap: "25px",
                alignItems: "flex-start",
            }}>
            {/* Left column: Sensors */}
            <Card title="Status" className="p-4">
                <div
                    style={{
                        flex: 1,
                        overflowY: "auto",
                        paddingRight: "8px",
                        minWidth: "450px",
                    }}>
                    <h3 className="mb-3">System Information</h3>
                    <Card title="System" className="mb-3">
                        <p className="m-0">
                            <strong>Raspberry Pi Time:</strong> {rpiTime || "—"}
                        </p>
                        <p className="m-0">
                            <strong>Events Queued:</strong>{" "}
                            <Tag
                                value={eventsQueued.toString()}
                                severity={
                                    eventsQueued > 0 ? "danger" : "success"
                                }
                                style={{
                                    padding: "0.3rem 0.5rem",
                                }}
                            />
                        </p>
                    </Card>
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
    );
}
