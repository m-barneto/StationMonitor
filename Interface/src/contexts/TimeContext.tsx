import React, { createContext, useEffect, useMemo, useState } from "react";
import LongDistanceSensor from "../data/StatusData";

interface TimeContextType {
    time: Date | undefined;
    setTime: React.Dispatch<React.SetStateAction<Date | undefined>>;
}

export const TimeContext = createContext<TimeContextType | undefined>(
    undefined
);

export const TimeProvider: React.FC<{ children: React.ReactNode }> = ({
    children,
}) => {
    const [time, setTime] = useState<Date | undefined>(
        undefined
    );

    const contextValue = useMemo(() => {
        return {
            time,
            setTime,
        };
    }, [time]);

    const fetchSensorData = async () => {
        fetch("/status")
            .then((response) => response.json())
            .then((data) => {
                if (data["realTime"] !== undefined) {
                    setTime(new Date(data["realTime"]))
                }
            });
    };

    useEffect(() => {
        fetchSensorData();
        const id = setInterval(fetchSensorData, 5000);

        return () => clearInterval(id);
    }, []);

    return (
        <TimeContext.Provider value={contextValue}>
            {children}
        </TimeContext.Provider>
    );
};
