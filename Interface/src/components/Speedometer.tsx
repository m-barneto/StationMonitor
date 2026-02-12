import React, { useContext, useEffect, useState } from "react";
import ReactSpeedometer from "react-d3-speedometer";
import { EventDataContext } from "../contexts/DataContext";
import { getPastHour } from "../utils/Period";
import GaugeComponent from "react-gauge-component";

export default function Speedometer() {
    const { eventData } = useContext(EventDataContext)!;

    const [carsPerHour, setCarsPerHour] = useState(0);
    const [avgEventDuration, setAvgEventDuration] = useState(0);

    useEffect(() => {
        if (!eventData) return;
        // Go through every event (in past hour?) and calculate avg time and cars per hour
        //const lastHour = getPastHour(simTime, eventData!);
        const lastHour = getPastHour(eventData!);

        // Calculate avg event duration in the past hour
        let sum = 0;
        lastHour.forEach((e) => {
            sum += e.duration;
        });
        if (lastHour.length > 0) {
            setAvgEventDuration(Number((sum / lastHour.length).toFixed(2)));
        } else {
            setAvgEventDuration(0);
        }

        // Calculate how many cars we had in the past hour
        setCarsPerHour(lastHour.length);
    }, [eventData]);

    return (
        <div
            style={{
                display: "flex",
                width: "100%",
                justifyContent: "center",
                gap: "5rem",
            }}>
            <div>
                <h2
                    style={{
                        textAlign: "center",
                    }}>
                    Cars Per Hour
                </h2>
                <GaugeComponent
                    type="radial"
                    labels={{
                        valueLabel: {
                            formatTextValue: (value) => value + " cars/hour",
                        },
                        tickLabels: {
                            type: "inner",
                            ticks: [
                                { value: 15 },
                                { value: 30 },
                                { value: 45 },
                                { value: 60 },
                            ],
                            defaultTickValueConfig: {
                                formatTextValue: (value: string) => value,
                            },
                        },
                    }}
                    arc={{
                        colorArray: ["#EA4228", "#5BE12C"],
                        subArcs: [
                            {
                                limit: 5,
                            },
                            {
                                limit: 10,
                            },
                            {
                                limit: 15,
                            },
                            {
                                limit: 20,
                            },
                            {
                                limit: 25,
                            },
                            {
                                limit: 30,
                            },
                            {
                                limit: 35,
                            },
                            {
                                limit: 40,
                            },
                            {
                                limit: 45,
                            },
                            {
                                limit: 50,
                            },
                            {
                                limit: 55,
                            },
                            {},
                        ],
                    }}
                    minValue={0}
                    maxValue={60}
                    pointer={{
                        color: "#EA4228",
                        length: 0.8,
                        width: 15,
                    }}
                    value={carsPerHour}
                    style={{
                        width: "30rem",
                        height: "20rem",
                    }}
                />
            </div>
            <div>
                <h2
                    style={{
                        textAlign: "center",
                    }}>
                    Avg Service Time
                </h2>
                <GaugeComponent
                    type="radial"
                    labels={{
                        valueLabel: {
                            formatTextValue: (value) => value + " mins/car",
                        },
                        tickLabels: {
                            type: "inner",
                            ticks: [{ value: 4 }, { value: 6 }, { value: 8 }],
                            defaultTickValueConfig: {
                                formatTextValue: (value: string) => value,
                            },
                        },
                    }}
                    arc={{
                        colorArray: ["#5BE12C", "#EA4228"],
                        subArcs: [
                            {},
                            {
                                limit: 1,
                            },
                            {
                                limit: 2,
                            },
                            {
                                limit: 3,
                            },
                            {
                                limit: 4,
                            },
                            {
                                limit: 5,
                            },
                            {
                                limit: 6,
                            },
                            {
                                limit: 7,
                            },
                            {
                                limit: 8,
                            },
                            {
                                limit: 9,
                            },
                            {
                                limit: 10,
                            },
                            {
                                limit: 11,
                            },
                            {},
                        ],
                    }}
                    minValue={0}
                    maxValue={12}
                    pointer={{
                        color: "#EA4228",
                        length: 0.8,
                        width: 15,
                    }}
                    value={avgEventDuration}
                    style={{
                        width: "30rem",
                        height: "20rem",
                    }}
                />
            </div>
        </div>
    );
}
