import "./style.css";

import React from "react";
import StationDashboard from "./components/StationDashboard";
import { Splitter, SplitterPanel } from "primereact/splitter";

import { useContext } from "react";
import { EventDataContext, EventDataProvider } from "./contexts/DataContext";
import EventHistory from "./components/EventHistory";
import Speedometer from "./components/Speedometer";
import DailySummary from "./components/DailySummary";
import Header from "./components/Header";
import { TabPanel, TabView } from "primereact/tabview";
import { SensorStatusContext, SensorStatusProvider } from "./contexts/StatusContext";
import ZoneTimerCard from "./components/ZoneTimerCard";
import ZoneTimerPanel from "./components/ZoneTimerPanel";

function App() {
    return (
        <main>
            <EventDataProvider>
                <SensorStatusProvider>
                    <TabView>
                        <TabPanel header="Summary">
                            <Splitter>
                                <SplitterPanel className="flex flex-row" size={5}>
                                    <EventHistory />
                                </SplitterPanel>
                                <SplitterPanel className="flex flex-row" size={80}>
                                    <div style={{ width: "100%" }}>
                                        <Speedometer />
                                        <DailySummary />
                                    </div>
                                </SplitterPanel>
                                <SplitterPanel size={15}>
                                    <div style={{ display: "flex", gap: 16, flexWrap: "wrap", width: "100%" }}>
                                        <ZoneTimerPanel />
                                    </div>
                                </SplitterPanel>
                            </Splitter>
                        </TabPanel>
                        <TabPanel header="Settings">
                            <StationDashboard />
                        </TabPanel>
                    </TabView>
                </SensorStatusProvider>
            </EventDataProvider>
        </main>
    );
}

export default App;
