import { useState } from "react";
import './App.css';
import MapContainer from './components/MapConatiner';
import SearchField from './components/SearchField';
import UrlOverview from './components/UrlOverview';
import { getRouterMap } from "./utils/api";

function App() {
  const [URLs, setURLs] = useState<string[]>([]);
  const [map, setMap] = useState<JSX.Element>();

  function addURL(url: string) {
    setURLs((prevState: string[]) => {
      return [...prevState, url];
    });
  }

  async function getMap() {
    const map = await getRouterMap(URLs);
    setMap(map);
  }

  return (
    <div className="App">
      <div className="container">
        <SearchField addURL={addURL} />
        <MapContainer>
          {map}
        </MapContainer>
        <button className="api-button" onClick={getMap}>Beregn plasseringer</button>
      </div>
      <UrlOverview URLs={URLs} />
    </div>
  );
}

export default App;
