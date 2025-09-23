import { Button } from "primereact/button";
import { Card } from "primereact/card";
import { Dropdown } from "primereact/dropdown";
import { InputNumber } from "primereact/inputnumber";
import { InputText } from "primereact/inputtext";
import { Divider } from "primereact/divider";
import { ProgressSpinner } from "primereact/progressspinner";
import { Calendar } from "primereact/calendar";
import { useEffect, useState } from "react";

export interface StationMonitorConfig {
    longDistanceSensors: LongDistanceSensor[];
    sleep: Sleep;
    alarmDuration: number;
    minOccupiedDuration: number;
    sensorPollRate: number;
    proxyEventRoute: string;
    proxyAlarmRoute: string;
    proxyStatusUpdateRoute: string;
    eventSendRate: number;
    eventSendFailureCooldown: number;
    updateConfigInterval: number;
    updateHealthStatusInterval: number;
}

export interface LongDistanceSensor {
    zone: string;
    serialNumber: string;
    occupiedDistance: number;
    emptyReflectionStrength: number;
}

export interface Sleep {
    timezone: string;
    openTime: string;
    closeTime: string;
    sleepInterval: number;
}

const timezones = [
    { label: "US/Eastern", value: "US/Eastern" },
    { label: "US/Central", value: "US/Central" },
    { label: "US/Mountain", value: "US/Mountain" },
    { label: "US/Pacific", value: "US/Pacific" },
];

// Settings Form Component
export default function SettingsForm() {
    const [settings, setSettings] = useState<StationMonitorConfig>(
        {} as StationMonitorConfig
    );

    const [loading, setLoading] = useState(true);

    const fetchSettings = async () => {
        fetch("http://192.168.17.136/config")
            .then((response) => response.json())
            .then((data) => {
                setSettings(data as StationMonitorConfig);
            });
    };

    useEffect(() => {
        fetchSettings();
    }, []);

    const updateField = (field: keyof StationMonitorConfig, value: any) => {
        setSettings((prev) => ({ ...prev, [field]: value }));
    };

    const updateSleepField = (field: keyof Sleep, value: any) => {
        setSettings((prev) => ({
            ...prev,
            sleep: { ...prev.sleep, [field]: value },
        }));
    };

    const updateSensorField = (
        index: number,
        field: keyof LongDistanceSensor,
        value: any
    ) => {
        const updated = [...settings.longDistanceSensors];
        updated[index] = { ...updated[index], [field]: value };
        updateField("longDistanceSensors", updated);
    };

    const handleSubmit = () => {
        console.log("Submitted Settings:", settings);
        alert("Settings saved! Check console for output.");
        // Make a post request containing the updated settings in json format
        fetch("http://192.168.17.136/config", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(settings),
        });
        console.log("sent request");
    };

    if (settings.longDistanceSensors === undefined) {
        return (
            <div
                className="flex justify-content-center align-items-center"
                style={{ height: "300px" }}>
                <ProgressSpinner style={{ width: "60px", height: "60px" }} />
            </div>
        );
    }

    return (
        <Card title="System Configuration" className="p-4">
            <h3>Distance Sensors</h3>

            {settings.longDistanceSensors.map((sensor, i) => (
                <Card key={i} className="mb-3 p-3">
                    <div className="p-fluid grid formgrid">
                        <div className="col-12 md:col-8">
                            <label htmlFor={`zone-${i}`}>Zone Label</label>
                            <InputText
                                value={sensor.zone}
                                onChange={(e) =>
                                    updateSensorField(i, "zone", e.target.value)
                                }
                                placeholder="Zone"
                            />
                        </div>
                        <div className="col-12 md:col-4">
                            <label htmlFor={`occupiedDistance-${i}`}>
                                Occupied Distance
                            </label>
                            <InputNumber
                                value={sensor.occupiedDistance}
                                onValueChange={(e) =>
                                    updateSensorField(
                                        i,
                                        "occupiedDistance",
                                        e.value || 1000
                                    )
                                }
                                placeholder="Occupied Distance"
                                suffix=" mm"
                                useGrouping={false}
                            />
                        </div>
                    </div>
                </Card>
            ))}

            <Divider />

            <h3>Sleep Settings</h3>
            <div className="p-fluid grid">
                <div className="col-12 md:col-4">
                    <label htmlFor="timezone">Timezone</label>
                    <Dropdown
                        value={settings.sleep.timezone}
                        options={timezones}
                        onChange={(e) => updateSleepField("timezone", e.value)}
                        placeholder="Timezone"
                    />
                </div>
                <div className="col-12 md:col-3">
                    <label htmlFor="openTime">Open Time</label>
                    <Calendar
                        id="openTime"
                        value={
                            new Date(`1970-01-01T${settings.sleep.openTime}:00`)
                        }
                        onChange={(e) => {
                            const timeStr = e.value
                                ? e.value.toLocaleTimeString([], {
                                      hour: "2-digit",
                                      minute: "2-digit",
                                      hour12: false,
                                  })
                                : "";
                            updateSleepField("openTime", timeStr);
                        }}
                        timeOnly
                        hourFormat="24"
                        className="w-full mb-3"
                    />
                </div>
                <div className="col-12 md:col-3">
                    <label htmlFor="closeTime">Close Time</label>

                    <Calendar
                        id="closeTime"
                        value={
                            new Date(
                                `1970-01-01T${settings.sleep.closeTime}:00`
                            )
                        }
                        onChange={(e) => {
                            const timeStr = e.value
                                ? e.value.toLocaleTimeString([], {
                                      hour: "2-digit",
                                      minute: "2-digit",
                                      hour12: false,
                                  })
                                : "";
                            updateSleepField("closeTime", timeStr);
                        }}
                        timeOnly
                        hourFormat="24"
                        className="w-full mb-3"
                    />
                </div>
            </div>

            <Divider />

            <h3>General Settings</h3>
            <div className="p-fluid grid">
                <div className="col-12 md:col-5">
                    <label htmlFor="alarmDuration" className="mb-2">
                        Alarm Duration
                    </label>
                    <InputNumber
                        id="alarmDuration"
                        value={settings.alarmDuration / 60} // convert seconds → minutes for display
                        onValueChange={(e) =>
                            updateField("alarmDuration", (e.value || 0) * 60)
                        }
                        showButtons
                        step={1}
                        min={1}
                        suffix=" min"
                        className="w-full mb-3"
                    />
                </div>
                <div className="col-12 md:col-5">
                    <label>Minimum Occupied Duration</label>
                    <InputNumber
                        value={settings.minOccupiedDuration}
                        onValueChange={(e) =>
                            updateField("minOccupiedDuration", e.value || 0)
                        }
                        placeholder="Min Occupied Duration (s)"
                        suffix=" s"
                        showButtons
                        step={1}
                        min={1}
                        className="w-full mb-3"
                    />
                </div>
            </div>

            <Divider />
            <Button
                label="Save Configuration"
                icon="pi pi-save"
                className="p-button-success mt-3"
                onClick={handleSubmit}
            />
        </Card>
    );
}
