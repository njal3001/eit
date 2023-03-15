const API_URL = "127.0.0.1:8000";

export async function getRouterMap(urls: string[]): Promise<JSX.Element> {
  const res = await fetch(`http://${API_URL}/api/map?poid=5&poid=4`);
  const blob = await res.blob();
  const src = URL.createObjectURL(blob);

  return <div>
    <img src={src} alt="map" />
  </div>
}
