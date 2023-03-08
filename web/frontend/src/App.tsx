import { useState, useEffect, useRef } from "react";
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
  const [pois, setPois] = useState<MarkedPoi[]>([]);
  const mapRef = useRef<Map>();
  const poisRef = useRef<MarkedPoi[]>([]);

  // Need to use a ref because mazemap object can't access
  // useState variables directly
  poisRef.current = pois;

  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://api.mazemap.com/js/v2.0.9/mazemap.min.js'
    script.addEventListener('load', initializeMap);

    document.body.appendChild(script);
    return () => {
      document.body.removeChild(script);
    }
  }, []);

  function initializeMap() {
    if (mapRef.current) return;

    mapRef.current = new window.Mazemap.Map({container: 'mazemap-container'}) as Map;
    mapRef.current.on('load', () => {
      if (!mapRef.current) return;

      mapRef.current.on('click', onMapClick);
      mapRef.current.highlighter = new window.Mazemap.Highlighter(mapRef.current, {
          showOutline: true,
          showFill: true,
          outlineColor: window.Mazemap.Util.Colors.MazeColors.MazeBlue,
          fillColor: window.Mazemap.Util.Colors.MazeColors.MazeBlue
      });

      mapRef.current.jumpTo({
        center: { lat: 63.41732271104283, lng: 10.404263674366945 },
        zoom: 15.5,
      });
    })
  }

  function onMapClick(e: any) {
    if (!mapRef.current) return;

    const lngLat: LongLat = e.lngLat;
    const zLevel: number = mapRef.current.zLevel;
    if (!isNaN(zLevel)) {
      window.Mazemap.Data.getPoiAt(lngLat, zLevel).then((poi: Poi) => {
        const id = poi.properties.id;
        if (poisRef.current.some((poi) => poi.poi.properties.id === id)) {
          removePoid(id);
        } else {
          addPoi(poi);
        }
      })
    }
  }

  function addPoi(poi: Poi) {
    if (!mapRef.current) return;

    const lngLat = window.Mazemap.Util.getPoiLngLat(poi);
    var marker: MapMarker = new window.Mazemap.MazeMarker( {
        zLevel: mapRef.current.zLevel,
    });
    marker.setLngLat(lngLat);
    marker.addTo(mapRef.current);

    setPois((prevState) => {
      return [...prevState, { poi: poi, marker: marker }];
    });
  }

  function removePoid(poid: number) {
    var poiToBeRemoved = poisRef.current.find((poi) => poi.poi.properties.id === poid);
    if (poiToBeRemoved) {
      poiToBeRemoved.marker.remove();
      setPois((prevState) => {
        return prevState.filter((poi) => poi.poi.properties.id !== poid);
      });
    }
  }

  return (
    <div className="App">
      <div id='mazemap-container' style={{width: '500px', height: '500px'}} />
    </div>
  );
}

export default App;
