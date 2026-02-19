import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { EventData } from "../data/EventData";

import dummyDataJson from "../data/dummy_data.json";
import { SensorStatusContext } from "./StatusContext";

const dummyData: EventData[] = dummyDataJson.events as unknown as EventData[];

interface EventDataContextType {
    eventData: EventData[] | undefined;
    setEventData: React.Dispatch<React.SetStateAction<EventData[] | undefined>>;
}

export const EventDataContext = createContext<EventDataContextType | undefined>(
    undefined
);

export const EventDataProvider: React.FC<{ children: React.ReactNode }> = ({
    children,
}) => {
    const [eventData, setEventData] = useState<EventData[] | undefined>(
        undefined
    );

    const contextValue = useMemo(() => {
        return {
            eventData,
            setEventData,
        };
    }, [eventData]);

    useEffect(() => {
        const id = setInterval(() => {
            const events: EventData[] = [];
            fetch("/events")
                .then((response) => response.json())
                .then((data) => {
                    for (const i of data) {
                        events.push(
                            new EventData(
                                "",
                                i["body"]["startTime"],
                                i["body"]["duration"]
                            )
                        );
                    }
                    setEventData(events);
                });
        }, 2500);

        return () => clearInterval(id);
    }, []);

    return (
        <EventDataContext.Provider value={contextValue}>
            {children}
        </EventDataContext.Provider>
    );
};
