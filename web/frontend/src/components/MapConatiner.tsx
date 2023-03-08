import "./MapContainer.css";

function MapContainer(props: React.PropsWithChildren) {
  const { children } = props;
  return <div className="container map-container">
    {children}
  </div>;
}

export default MapContainer;
