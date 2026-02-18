import React, { useMemo } from "react";
import type LongDistanceSensor from "../data/StatusData";

type Props = {
    sensor: LongDistanceSensor;
};

const STAGE_1_END = 0.25 * 60; // 30s
const STAGE_2_END = 1 * 60;   // 1m
const STAGE_3_END = 1.5 * 60; // 1m 30s

const STAGE_1 = "0-15s";
const STAGE_2 = "15-60s";
const STAGE_3 = "60-90s";

export default function ZoneTimerCard({
    sensor
}: Props) {
    const duration = sensor.duration ?? 0;

    const stage = useMemo(() => {
        if (duration < STAGE_1_END) return 1;
        if (duration < STAGE_2_END) return 2;
        if (duration < STAGE_3_END) return 3;
        return 4;
    }, [duration]);

    // Progress resets when stage changes
    const { progress, stageLabel } = useMemo(() => {
        if (stage === 1) {
            return {
                progress: clamp(duration / STAGE_1_END),
                stageLabel: STAGE_1,
            };
        }

        if (stage === 2) {
            const stageDuration = duration - STAGE_1_END;
            const stageTotal = STAGE_2_END - STAGE_1_END;
            return {
                progress: clamp(stageDuration / stageTotal),
                stageLabel: STAGE_2,
            };
        }

        if (stage === 3) {
            const stageDuration = duration - STAGE_2_END;
            const stageTotal = STAGE_3_END - STAGE_2_END;
            return {
                progress: clamp(stageDuration / stageTotal),
                stageLabel: STAGE_3,
            };
        }

        return {
            progress: 1,
            stageLabel: "90+ sec",
        };
    }, [duration, stage]);

    const fillStyle: React.CSSProperties = useMemo(() => {
        // You can swap these colors easily
        if (stage === 1) return { background: "#22c55e" }; // green
        if (stage === 2) return { background: "#f59e0b" }; // amber
        return { background: "#ef4444" }; // red
    }, [stage]);

    const glowStyle: React.CSSProperties = useMemo(() => {
        if (stage !== 3) return {};
        return {
            boxShadow: "0 0 0 2px rgba(239,68,68,0.9), 0 0 18px rgba(239,68,68,0.75)",
        };
    }, [stage]);

    return (
        <div
            style={{
                height: "100%",
                borderRadius: 12,
                padding: 12,
                border: "1px solid rgba(255,255,255,0.12)",
                background: "rgba(0,0,0,0.25)",
                display: "flex",
                flexDirection: "column",
                gap: 10,
                alignItems: "stretch",
            }}
        >
            {/* Zone header */}
            <div style={{ textAlign: "center" }}>
                <div style={{ fontWeight: 700, fontSize: 16 }}>
                    {sensor.zone}
                </div>
                <div style={{ opacity: 0.7, fontSize: 12 }}>
                    {stageLabel}
                </div>
            </div>

            {/* Vertical bar container */}
            <div
                style={{
                    borderRadius: 12,
                    overflow: "hidden",
                    border: stage === 3 ? "2px solid rgba(239,68,68,0.9)" : "1px solid rgba(255,255,255,0.12)",
                    background: "rgba(255,255,255,0.06)",
                    position: "relative",
                    ...glowStyle,
                }}
            >
                {/* Fill */}
                <div
                    style={{
                        position: "absolute",
                        bottom: 0,
                        left: 0,
                        right: 0,
                        height: `${progress * 100}%`,
                        transition: "height 250ms linear, background 250ms linear",
                        ...fillStyle,
                    }}
                />
            </div>

            {/* Duration text */}
            <div style={{ textAlign: "center", fontSize: 13, opacity: 0.85 }}>
                {formatDuration(duration)}
            </div>
        </div>
    );
}

function clamp(n: number) {
    return Math.max(0, Math.min(1, n));
}

function formatDuration(seconds: number) {
    const s = Math.max(0, Math.floor(seconds));
    const mm = Math.floor(s / 60);
    const ss = s % 60;
    return `${mm}:${ss.toString().padStart(2, "0")}`;
}
