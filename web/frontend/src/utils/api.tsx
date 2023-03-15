const API_URL = "127.0.0.1:8000";

export async function getRouterMap(ids: number[]): Promise<string> {
  var query = `http://${API_URL}/api/map?`
  for (var i = 0; i < ids.length; i++) {
    query = query.concat(`poid=${ids[i]}&`)
  }

  query = query.substring(0, query.length - 1);

  const res = await fetch(query);
  const blob = await res.blob();
  const src = URL.createObjectURL(blob);

  return src;
}
