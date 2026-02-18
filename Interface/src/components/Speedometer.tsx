import React, { useContext, useEffect, useState } from "react";
import ReactSpeedometer from "react-d3-speedometer";
import { EventDataContext } from "../contexts/DataContext";
import { getPastHour } from "../utils/Period";
import GaugeComponent, { Tick } from "react-gauge-component";
import { formatDuration } from "../utils/Utils";

export default function Speedometer() {
    const { eventData } = useContext(EventDataContext)!;

    const [carsPerHour, setCarsPerHour] = useState(0);
    const [avgEventDuration, setAvgEventDuration] = useState(0);

    const MIN_PER_CAR_TICKS = 6;
    const MIN_PER_CAR_MAX = 15;

    const CAR_PER_HOUR_TICKS = 4;
    const CAR_PER_HOUR_MAX = 60;

    useEffect(() => {
        if (!eventData) return;
        // Go through every event (in past hour?) and calculate avg time and cars per hour
        //const lastHour = getPastHour(simTime, eventData!);
        const lastHour = getPastHour(eventData!);

        // Calculate avg event duration in the past hour
        let sum = 0;
        lastHour.forEach((e) => {
            sum += e.duration / 60;
        });
        if (lastHour.length > 0) {
            setAvgEventDuration(Number((sum / lastHour.length).toFixed(1)));
        } else {
            setAvgEventDuration(0);
        }

        // Calculate how many cars we had in the past hour
        setCarsPerHour(lastHour.length);
    }, [eventData]);

    function generateSubArcs(min: number, max: number, segments: number) {
        const arcs: { limit: number }[] = [];

        const step = (max - min) / segments;

        for (let i = 1; i <= segments; i++) {
            arcs.push({
                limit: min + step * i,
            });
        }
        return arcs;
    }

    function generateTicks(min: number, max: number, numTicks: number) {
        const ticks: Tick[] = [];
        const step = (max - min) / (numTicks - 1);

        for (let i = 0; i < numTicks; i++) {
            ticks.push({
                value: Number((min + step * i).toFixed(1)),
            });
        }
        return ticks;
    }

    return (
        <div
            style={{
                display: "flex",
                justifyContent: "center",
                gap: "5rem",
                paddingBottom: "3.5rem",
                height: "75%"
            }}>
            <div style={{ width: "100%" }}>
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
                            ticks: generateTicks(0, CAR_PER_HOUR_MAX, CAR_PER_HOUR_TICKS),
                            defaultTickValueConfig: {
                                formatTextValue: (value: string) => value,
                            },
                        },
                    }}
                    arc={{
                        colorArray: ["#EA4228", "#5BE12C"],
                        subArcs: generateSubArcs(0, CAR_PER_HOUR_MAX, CAR_PER_HOUR_TICKS),
                    }}
                    minValue={0}
                    maxValue={60}
                    pointer={{
                        color: "#EA4228",
                        length: 0.8,
                        width: 15,
                    }}
                    value={carsPerHour}
                />
            </div>
            <div style={{ width: "100%" }}>
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
                            formatTextValue: (value) => formatDuration(avgEventDuration * 60) + "/car",
                        },
                        tickLabels: {
                            type: "inner",
                            ticks: generateTicks(0, MIN_PER_CAR_MAX, MIN_PER_CAR_TICKS),
                            defaultTickValueConfig: {
                                formatTextValue: (value: string) => value,
                            },
                        },
                    }}
                    arc={{
                        colorArray: ["#5BE12C", "#EA4228"],
                        subArcs: generateSubArcs(0, MIN_PER_CAR_MAX, MIN_PER_CAR_TICKS)
                    }}
                    minValue={0}
                    maxValue={MIN_PER_CAR_MAX}
                    pointer={{
                        color: "#EA4228",
                        length: 0.8,
                        width: 15,
                    }}
                    value={avgEventDuration}
                />
            </div>
        </div>
    );
}
