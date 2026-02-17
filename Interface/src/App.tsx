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

function App() {
    return (
        <main>
            <EventDataProvider>
                <TabView>
                    <TabPanel header="Summary">
                        <Splitter>
                            <SplitterPanel className="flex flex-row" size={5}>
                                <EventHistory />
                            </SplitterPanel>
                            <SplitterPanel className="flex flex-row">
                                <div style={{ width: "100%" }}>
                                    <Speedometer />
                                    <DailySummary />
                                </div>
                            </SplitterPanel>
                            <SplitterPanel>
                                <div>
                                    Timer
                                </div>
                            </SplitterPanel>
                        </Splitter>
                    </TabPanel>
                    <TabPanel header="Settings">
                        <StationDashboard />
                    </TabPanel>
                </TabView>
            </EventDataProvider>
        </main>
    );
}

export default App;
