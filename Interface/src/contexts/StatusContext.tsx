import React, { createContext, useEffect, useMemo, useState } from "react";
import LongDistanceSensor from "../data/StatusData";
import isDev from "../utils/Utils";

interface SensorStatusContextType {
    sensors: LongDistanceSensor[] | undefined;
    setSensorData: React.Dispatch<React.SetStateAction<LongDistanceSensor[] | undefined>>;
}

export const SensorStatusContext = createContext<SensorStatusContextType | undefined>(
    undefined
);

export const SensorStatusProvider: React.FC<{ children: React.ReactNode }> = ({
    children,
}) => {
    const [sensors, setSensorData] = useState<LongDistanceSensor[] | undefined>(
        undefined
    );

    const contextValue = useMemo(() => {
        return {
            sensors,
            setSensorData,
        };
    }, [sensors]);

    const fetchSensorData = async () => {
        const sensorData: LongDistanceSensor[] = [];
        fetch("/status")
            .then((response) => response.json())
            .then((data) => {
                Object.entries(data.longDistanceSensors).forEach(
                    ([id, sensor]) => {
                        const s = sensor as LongDistanceSensor;
                        s.zone = id;
                        sensorData.push(s);
                    }
                );
                setSensorData(sensorData);
            });
    };

    useEffect(() => {
        if (isDev()) {
            return;
        }

        fetchSensorData();
        const id = setInterval(fetchSensorData, 500);

        return () => clearInterval(id);
    }, []);

    return (
        <SensorStatusContext.Provider value={contextValue}>
            {children}
        </SensorStatusContext.Provider>
    );
};
