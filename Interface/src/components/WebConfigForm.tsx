import { Button } from "primereact/button";
import { Card } from "primereact/card";
import { Dropdown } from "primereact/dropdown";
import { InputNumber } from "primereact/inputnumber";
import { InputText } from "primereact/inputtext";
import { InputMask } from "primereact/inputmask"
import { Divider } from "primereact/divider";
import { ProgressSpinner } from "primereact/progressspinner";
import { Calendar } from "primereact/calendar";
import { Dialog } from "primereact/dialog";
import { useEffect, useState } from "react";
import isDev from "../utils/Utils";


export interface Stage {
    duration: number;
    color: string;
    label: string;
}

export interface Guages {
    min: number;
    max: number;
    ticks: number;
    segments: number;
    window: number;
}

export interface WebConfig {
    stages: Stage[];
    guages: Guages;
}

const dummySettings: WebConfig = {
    "stages": [
        {
            "duration": 0,
            "color": "",
            "label": ""
        },
                {
            "duration": 60,
            "color": "",
            "label": ""
        },
        {
            "duration": 90,
            "color": "",
            "label": ""
        }
    ],
    "guages": {
        "min": 0,
        "max": 15,
        "ticks": 5,
        "segments": 3,
        "window": 60
    }
};

// Settings Form Component
export default function SettingsForm() {
    const [settings, setSettings] = useState<WebConfig>(
        {} as WebConfig
    );

    const [ip, setIp] = useState<string | undefined>();

    const [loading, setLoading] = useState(true);
    const [showHelp, setShowHelp] = useState(false);

    const fetchSettings = async () => {
        fetch("/webconfig")
            .then((response) => response.json())
            .then((data) => {
                setSettings(data as WebConfig);
            });
    };

    useEffect(() => {
        if (isDev()) {
            setSettings(dummySettings);
            return;
        }
        fetchSettings();
    }, []);

    const updateField = (field: keyof WebConfig, value: any) => {
        setSettings((prev) => ({ ...prev, [field]: value }));
    };

    const updateGuagesField = (field: keyof Guages, value: any) => {
        setSettings((prev) => ({
            ...prev,
            guages: { ...prev.guages, [field]: value },
        }));
    };

    const updateStagesField = (
        index: number,
        field: keyof Stage,
        value: any
    ) => {
        const updated = [...settings.stages];
        updated[index] = { ...updated[index], [field]: value };
        updateField("stages", updated);
    };

    const handleSubmit = () => {
        const pin = window.prompt("Enter PIN:");
        if (pin !== "1234") {
            alert("Incorrect PIN");
            return;
        }

        // Make a post request containing the updated settings in json format
        fetch("/webconfig", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(settings),
        }).then((response) => {
            if (response.ok) {
                alert("Settings saved successfully, reloading...");
            } else {
                alert("Failed to save settings");
            }
        });
        // Reload page after a short delay to allow server to process
        setTimeout(() => {
            window.location.reload();
        }, 3000);
    };

    const addStage = () => {
        const newStage: Stage = {
            duration: 0,
            color: "#ffffff",
            label: ""
        };

        setSettings(prev => ({
            ...prev,
            stages: [...prev.stages, newStage]
        }));
    };

    const removeStage = (index: number) => {
        const updated = settings.stages.filter((_, i) => i !== index);
        updateField("stages", updated);
    };

    if (settings.guages === undefined) {
        return (
            <div
                className="flex justify-content-center align-items-center"
                style={{ height: "300px" }}>
                <ProgressSpinner style={{ width: "60px", height: "60px" }} />
            </div>
        );
    }

    return (
        <div className="flex justify-content-center">
        <div style={{ width: "60%", minWidth: "320px" }}>
        <Card
            title={
                <div className="flex justify-content-between align-items-center w-full">
                    <span>System Configuration</span>
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
            }
            className="p-4">
            <h3>Timeline Stages</h3>

            {settings.stages.map((stage, i) => (
                <Card key={i} className="mb-3">
                    <div className="p-fluid grid formgrid">

                        {/* Label */}
                        <div className="col-6 md:col-2">
                            <label>Label</label>
                            <InputText
                                value={stage.label}
                                onChange={(e) =>
                                    updateStagesField(i, "label", e.target.value)
                                }
                                placeholder="Stage Label"
                            />
                        </div>

                        {/* Duration (Minutes) */}
                        <div className="col-6 md:col-2">
                            <label>Duration (minutes)</label>
                            <InputNumber
                                value={stage.duration}
                                onValueChange={(e) =>
                                    updateStagesField(
                                        i,
                                        "duration",
                                        e.value ?? 0
                                    )
                                }
                                suffix=" min"
                                useGrouping={false}
                            />
                        </div>

                        {/* Color */}
                        <div className="col-6 md:col-2">
                            <label>Color</label>
                            <InputText
                                type="color"
                                value={stage.color}
                                onChange={(e) =>
                                    updateStagesField(i, "color", e.target.value)
                                }
                            />
                        </div>

                        {/* Remove Button */}
                        <div className="col-6 md:col-1 flex align-items-end">
                            <Button
                                icon="pi pi-trash"
                                className="p-button-danger p-button-text"
                                onClick={() => removeStage(i)}
                            />
                        </div>

                    </div>
                </Card>
            ))}

            <Button
                label="Add Stage"
                icon="pi pi-plus"
                className="p-button-success mt-2"
                onClick={addStage}
            />

            <Divider />
            <Button
                label="Save Configuration"
                icon="pi pi-save"
                className="p-button-success mt-3"
                onClick={handleSubmit}
            />
            <Dialog
                header="Settings Description"
                visible={showHelp}
                style={{ width: "35rem" }}
                modal
                onHide={() => setShowHelp(false)}>
                <div className="p-3">
                    <ul className="m-0 p-0 list-none">
                        <li className="mb-3">
                            <strong>Zone Label:</strong>
                            <small className="block text-gray-500">
                                <code>SITE-0000-WAIT-1</code>
                            </small>
                            <small className="block text-gray-500">
                                <code>SITE-0000-BAY-1</code>
                            </small>
                        </li>
                        <li className="mb-6">
                            <strong>Occupied Distance:</strong> When the sensor
                            reading is below this value, the zone is considered
                            occupied.
                        </li>
                        <li className="mb-3">
                            <strong>Timezone:</strong> Timezone that the
                            open/close times are based on.
                        </li>
                        <li className="mb-6">
                            <strong>Open/Close Time:</strong> Events will only
                            be triggered within this time range.
                        </li>
                        <li className="mb-3">
                            <strong>Alarm Duration:</strong> Event's that go
                            over this duration (mins) will trigger an additional
                            alarm event.
                        </li>
                        <li className="mb-3">
                            <strong>Min. Occupied Duration:</strong> Event's
                            with a duration lower than this value (seconds) will
                            be ignored.
                        </li>
                        {/* Add more descriptions as needed */}
                    </ul>
                </div>
            </Dialog>
        </Card>
        </div>
        </div>
    );
}
