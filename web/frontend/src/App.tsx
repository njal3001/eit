import { useEffect, useRef, useState } from 'react';
import MapContainer from './components/MapConatiner'
import { getRoomMap, getRouterCoverage } from './utils/api';
import './App.css';

type LongLat = {
  lat: number,
  lng: number,
};

type MapMarker = {
  setLngLat: (lngLat: LongLat) => void,
  addTo: (map: Map) => void,
  remove: () => void,
};

type Poi = {
  properties: {
    id: number,
  }
};

type MarkedPoi = {
  poi: Poi,
  marker: MapMarker,
};

type MapView = {
  center: LongLat,
  zoom: number,
  speed?: number,
};

type Map = {
  jumpTo: (view: MapView) => void,
  on: (name: string, callback: (e: any) => void) => void,
  zLevel: number,
  highlighter: MapHighlighter,
}

type MapHighlighter = {
  clear: () => void,
  highlight: (poi: Poi) => void,
};

function App() {
  const mapRef = useRef<Map>();
  const poisRef = useRef<MarkedPoi[]>([]);

  const [mapSrc, setMapSrc] = useState<string>('');
  const [coverageSrc, setCoverageSrc] = useState<string>('');
  const [gridResolution, setGridResolution] = useState<number>(1.0);
  const [maxPathLoss, setMaxPathLoss] = useState<number>(90);

  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://api.mazemap.com/js/v2.0.94/mazemap.min.js'
    script.addEventListener('load', initializeMap);

    document.body.appendChild(script);
    return () => {
      document.body.removeChild(script);
    }
  }, []);

  useEffect(() => {
    updateMap();
  }, [gridResolution])

  const initializeMap = () => {
    if (mapRef.current) return;

    const mapOptions = {
      container: 'mazemap-container',
      center: { lat: 63.41732271104283, lng: 10.404263674366945 },
      zoom: 15.5,
    };

    mapRef.current = new window.Mazemap.Map(mapOptions) as Map;
    mapRef.current.on('load', () => {
      if (!mapRef.current) return;

      mapRef.current.on('click', onMapClick);
    })
  }

  const onMapClick = (e: any) => {
    if (!mapRef.current) return;

    const lngLat: LongLat = e.lngLat;
    const zLevel: number = mapRef.current.zLevel;
    if (!isNaN(zLevel)) {
      window.Mazemap.Data.getPoiAt(lngLat, zLevel).then((poi: Poi) => {
        const id = poi.properties.id;
        if (poisRef.current.some(({ poi }) => poi.properties.id === id)) {
          removePoid(id);
        } else {
          addPoi(poi);
        }
      })
    }
  }

  const addPoi = (poi: Poi) => {
    if (!mapRef.current) return;

    const lngLat = window.Mazemap.Util.getPoiLngLat(poi);
    const marker: MapMarker = new window.Mazemap.MazeMarker( {
        zLevel: mapRef.current.zLevel,
    });
    marker.setLngLat(lngLat);
    marker.addTo(mapRef.current);

    poisRef.current.push({ poi: poi, marker: marker });
    updateMap();
  }

  const removePoid = (poid: number) => {
    const poiToRemove = poisRef.current.find((poi) => poi.poi.properties.id === poid);
    if (poiToRemove) {
      poiToRemove.marker.remove();
      poisRef.current = poisRef.current.filter((poi) => poi !== poiToRemove);
      updateMap();
    } else {
      console.warn(`Tried to remove poi with id ${poid} but could not find it.`);
    }
  }

  const updateMap = async () => {
    if (gridResolution <= 0.0) return;
    if (poisRef.current.length === 0) {
        setMapSrc('');
        return;
    }

    const src = await getRoomMap(poisRef.current.map(({ poi }) => poi.properties.id), gridResolution);
    setMapSrc(src);
  }

  const onCalculate = async () => {
    if (gridResolution <= 0.0) return;
    if (poisRef.current.length === 0) return;

    const src = await getRouterCoverage(poisRef.current.map(({ poi }) => poi.properties.id), gridResolution, maxPathLoss);
    setCoverageSrc(src);
  }

  const onGridResolutionChanged = (e: React.ChangeEvent<HTMLInputElement>) => {
    setGridResolution(parseFloat(e.currentTarget.value));
  }

  const onMaxPathLossChanged = (e: React.ChangeEvent<HTMLInputElement>) => {
    setMaxPathLoss(parseInt(e.currentTarget.value));
  }

  return (
    <div className="App">
      <section className="mazemap-section">
        <h3 style={{ color: "#fff", maxWidth: "500px", minHeight: "3rem" }}>01. Velg rom du ønsker å beregne for</h3>
        <div id="mazemap-container" style={{width: '500px', height: '500px'}} />
        <div className="flex">
            <p className="text-white">Grid Oppløsning: </p>
            <input type="number" value={gridResolution} step="0.1" min="0.5" max="2.0" onChange={onGridResolutionChanged} />
        </div>
        <div className="flex">
            <p className="text-white">Maksimalt signaltap: </p>
            <input type="number" value={maxPathLoss} min="30" max="100" onChange={onMaxPathLossChanged} />
        </div>
      </section>
      <section>
        <h3 style={{ color: "#fff", maxWidth: "500px", minHeight: "3rem" }}>02. Beregning {(mapSrc === undefined || mapSrc === "") && "(velg rom for plassering og klikk 'Beregn plasseringer')"}</h3>
        <div className="container">
          <MapContainer active={mapSrc !== ''}>
            <img src={mapSrc} className="map-img" />
          </MapContainer>
          <MapContainer active={coverageSrc !== ''}>
            <img src={coverageSrc} className="map-img" />
          </MapContainer>
          <button className="api-button" onClick={onCalculate}>Beregn plasseringer</button>
        </div>
      </section>
    </div>
  );
}

export default App;
