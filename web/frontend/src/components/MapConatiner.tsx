import "./MapContainer.css";

interface MapContainer {
  active: boolean;
}

function MapContainer(props: React.PropsWithChildren<MapContainer>) {
  const { children, active } = props;
  return <div className={`container map-container ${active ? "active" : ""}`}>
    {children}
  </div>;
}

export default MapContainer;
