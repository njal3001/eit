import { useState, useEffect } from "react";
import './App.css';
import MapContainer from './components/MapConatiner';
import SearchField from './components/SearchField';
import UrlOverview from './components/UrlOverview';
import { getRouterMap } from "./utils/api";

function App() {
  const [URLs, setURLs] = useState<string[]>([]);
  const [map, setMap] = useState<JSX.Element>();
  const [mazemap, setMazemap] = useState<any>(undefined);

  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://api.mazemap.com/js/v2.0.9/mazemap.min.js'
    script.addEventListener('load', () => {
        const win = window as any;
        setMazemap(new win.Mazemap.Map({container: 'mazemap-container'}));
    })

    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://api.mazemap.com/js/v2.0.9/mazemap.min.css';

    document.body.appendChild(script);
    document.body.appendChild(link);
    return () => {
      document.body.removeChild(script);
      document.body.removeChild(link);
    }
  }, []);

  function emptyURLs() {
    setURLs([]);
  }

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
      <UrlOverview URLs={URLs} emptyURLs={emptyURLs} />
      <div id='mazemap-container' style={{width: '500px', height: '500px'}} />
    </div>
  );
}

export default App;
