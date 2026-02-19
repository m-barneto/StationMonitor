import React, { useContext, useEffect, useState } from "react";
import ReactSpeedometer from "react-d3-speedometer";
import { EventDataContext } from "../contexts/DataContext";
import { getPastHour } from "../utils/Period";
import GaugeComponent, { Tick } from "react-gauge-component";
import { formatDuration } from "../utils/Utils";
import { SensorStatusContext } from "../contexts/StatusContext";

export default function Speedometer() {
    const { eventData } = useContext(EventDataContext)!;
    const { sensors } = useContext(SensorStatusContext)!;


    const [carsPerHour, setCarsPerHour] = useState(0);
    const [avgEventDuration, setAvgEventDuration] = useState(0);

    const CAR_PER_HOUR_ARCS_PER_TICK = 3;
    const CAR_PER_HOUR_TICKS = 5;
    const CAR_PER_HOUR_MAX = 60;

    const MIN_PER_CAR_ARCS_PER_TICK = 5;
    const MIN_PER_CAR_TICKS = 4;
    const MIN_PER_CAR_MAX = 15;

    useEffect(() => {
        if (!eventData || !sensors) return;
        // Go through every event (in past hour?) and calculate avg time and cars per hour
        //const lastHour = getPastHour(simTime, eventData!);
        const lastHour = getPastHour(eventData!);
        // generate events for the current status


        // Calculate avg event duration in the past hour
        let sum = 0;
        let count = lastHour.length;
        for (const sensorId in sensors) {
            const sensor = sensors[sensorId];
            if (sensor.duration > 0) {
                sum += sensor.duration / 60;
                count++;
            }
        }

        lastHour.forEach((e) => {
            sum += e.duration / 60;
        });

        if (lastHour.length > 0) {
            setAvgEventDuration(sum / count);
        } else {
            setAvgEventDuration(0);
        }

        // Calculate how many cars we had in the past hour
        setCarsPerHour(count);
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

    function padCenter(text: string, targetLen: number) {
        if (text.length >= targetLen) return text;

        const totalPad = targetLen - text.length;
        const leftPad = Math.floor(totalPad / 2);
        const rightPad = totalPad - leftPad;

        const nbsp = "\u00A0";
        return nbsp.repeat(leftPad) + text + nbsp.repeat(rightPad);
    }

    const cphGuage = generateGaugeScale(0, CAR_PER_HOUR_MAX, CAR_PER_HOUR_TICKS, CAR_PER_HOUR_ARCS_PER_TICK, 1);
    const mpcGuage = generateGaugeScale(0, MIN_PER_CAR_MAX, MIN_PER_CAR_TICKS, MIN_PER_CAR_ARCS_PER_TICK, 1);

    return (
        <div
            style={{
                display: "flex",
                justifyContent: "center",
                gap: "5rem",
                height: "65%"
            }}>
            <div style={{ width: "100%" }}>
                <h2
                    style={{
                        textAlign: "center",
                        margin: 0,
                        marginTop: "0.5rem"
                    }}>
                    Cars Per Hour
                </h2>
                <GaugeComponent
                    type="radial"
                    labels={{
                        valueLabel: {
                            formatTextValue: (value) => padCenter(value + " cars/hour", 14)
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
                        cornerRadius: 5
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
                        margin: 0,
                        marginTop: "0.5rem"
                    }}>
                    Avg Service Time
                </h2>
                <GaugeComponent
                    type="radial"
                    labels={{
                        valueLabel: {
                            formatTextValue: (value) => padCenter(formatDuration(avgEventDuration * 60) + "/car", 14)
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
