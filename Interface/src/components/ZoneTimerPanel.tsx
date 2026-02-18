import { useContext } from "react";
import { SensorStatusContext } from "../contexts/StatusContext";
import ZoneTimerCard from "./ZoneTimerCard";

export default function ZoneTimerPanel() {

    const { sensors } = useContext(SensorStatusContext)!;

    return <>
        {sensors?.map((s) => (
            <ZoneTimerCard key={s.zone} sensor={s} />
        ))}
    </>
}