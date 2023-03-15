import { useEffect, useRef } from "react";
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

  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://api.mazemap.com/js/v2.0.9/mazemap.min.js'
    script.addEventListener('load', initializeMap);

    document.body.appendChild(script);
    return () => {
      document.body.removeChild(script);
    }
  }, []);

  const initializeMap = () => {
    if (mapRef.current) return;

    mapRef.current = new window.Mazemap.Map({container: 'mazemap-container'}) as Map;
    mapRef.current.on('load', () => {
      if (!mapRef.current) return;

      mapRef.current.on('click', onMapClick);
      mapRef.current.jumpTo({
        center: { lat: 63.41732271104283, lng: 10.404263674366945 },
        zoom: 15.5,
      });
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
  }

  const removePoid = (poid: number) => {
    const poiToRemove = poisRef.current.find((poi) => poi.poi.properties.id === poid);
    if (poiToRemove) {
      poiToRemove.marker.remove();
      poisRef.current = poisRef.current.filter((poi) => poi !== poiToRemove);
    } else {
      console.warn(`Tried to remove poi with id ${poid} but could not find it.`);
    }
  }

  return (
    <div className="App">
      <div id='mazemap-container' style={{width: '500px', height: '500px'}} />
    </div>
  );
}

export default App;
