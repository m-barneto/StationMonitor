import { useContext } from "react";
import { SensorStatusContext } from "../contexts/StatusContext";
import ZoneTimerCard from "./ZoneTimerCard";

export default function ZoneTimerPanel() {

    const { sensors } = useContext(SensorStatusContext)!;

    return (
        <div
            style={{
                display: "flex",
                flexDirection: "row",
                gap: 2,
                width: "100%",
                height: "100%",
                alignItems: "stretch",
            }}
        >
            {sensors?.map((s) => (
                <ZoneTimerCard key={s.zone} sensor={s} />
            ))}
        </div>
    )
}