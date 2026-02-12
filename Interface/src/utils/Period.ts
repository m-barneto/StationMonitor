import { EventData } from "../data/EventData";

export const getPastHourSim = (simTime: Date, events: EventData[]) => {
    const periodicEvents: EventData[] = [];
    events.forEach((e) => {
        // / 60  without this extra 60 its per minute
        const timeDiff = (simTime.getTime() - e.startDate!.getTime()) / 1000 / 60;
        if (timeDiff <= 1 && timeDiff > 0) {
            periodicEvents.push(e);
        }
    });

    return periodicEvents;
}

export const getPastHour = (events: EventData[]) => {
    const periodicEvents: EventData[] = [];
    events.forEach((e) => {
        // / 60
        const timeDiff = (new Date().getTime() - e.startDate!.getTime()) / 1000 / 60;
        if (timeDiff <= 1 && timeDiff > 0) {
            periodicEvents.push(e);
        }
    });

    return periodicEvents;
}