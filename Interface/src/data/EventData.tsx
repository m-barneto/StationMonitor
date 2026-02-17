import { ReactElement } from "react";
import { formatDuration } from "../utils/Utils";

export class EventData {
    event_id: string;
    startTime: string;
    duration: number;

    startDate: Date;
    displayedStartTime: string;
    displayedDuration: string;
    event_icon: ReactElement;

    constructor(event_id: string, startTime: string, duration: number) {
        this.event_id = event_id;
        this.event_icon = (
            <i className="pi pi-car" style={{ fontSize: "2rem" }} />
        );
        this.startTime = startTime;
        this.duration = duration;
        this.displayedDuration = formatDuration(this.duration);

        this.startDate = new Date(startTime);

        const hours = String(this.startDate.getHours() % 12);
        const minutes = String(this.startDate.getMinutes()).padStart(2, "0");
        const seconds = String(this.startDate.getSeconds()).padStart(2, "0");
        const mmmm = this.startDate.getHours() - 12 > 0 ? "PM" : "AM";

        this.displayedStartTime = hours + ":" + minutes + " " + mmmm;
    }
}
