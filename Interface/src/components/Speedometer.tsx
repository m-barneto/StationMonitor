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

    const MIN_PER_CAR_ARCS_PER_TICK = 1;
    const MIN_PER_CAR_TICKS = 6;
    const MIN_PER_CAR_MAX = 15;

    const CAR_PER_HOUR_ARCS_PER_TICK = 1;
    const CAR_PER_HOUR_TICKS = 5;
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

    function generateGaugeScale(
        min: number,
        max: number,
        numTicks: number,
        segmentsPerTickInterval: number,
        decimals = 0
    ) {
        // Tick labels
        const tickStep = (max - min) / (numTicks - 1);

        const ticks: Tick[] = Array.from({ length: numTicks }, (_, i) => ({
            value: Number((min + tickStep * i).toFixed(decimals)),
        }));

        // SubArcs (segments)
        const totalSegments = (numTicks - 1) * segmentsPerTickInterval;
        const arcStep = (max - min) / totalSegments;

        const subArcs = Array.from({ length: totalSegments }, (_, i) => ({
            limit: Number((min + arcStep * (i + 1)).toFixed(decimals)),
        }));

        return { ticks, subArcs };
    }

    const cphGuage = generateGaugeScale(0, CAR_PER_HOUR_MAX, 4, 2, 1);
    const mpcGuage = generateGaugeScale(0, MIN_PER_CAR_MAX, 6, 1, 1);

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
                            ticks: cphGuage.ticks,
                            defaultTickValueConfig: {
                                formatTextValue: (value: string) => value,
                            },
                        },
                    }}
                    arc={{
                        colorArray: ["#EA4228", "#5BE12C"],
                        subArcs: cphGuage.subArcs,
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
                            ticks: mpcGuage.ticks,
                            defaultTickValueConfig: {
                                formatTextValue: (value: string) => value,
                            },
                        },
                    }}
                    arc={{
                        colorArray: ["#5BE12C", "#EA4228"],
                        subArcs: mpcGuage.subArcs
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
