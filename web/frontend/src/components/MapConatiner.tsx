import "./MapContainer.css";

interface MapConatinerInterface {
  active: boolean;
}

function MapContainer(props: React.PropsWithChildren<MapConatinerInterface>) {
  const { active, children } = props;
  return <div className={`container map-container ${active ? "active" : ""}`}>
    {children}
  </div>;
}

export default MapContainer;
