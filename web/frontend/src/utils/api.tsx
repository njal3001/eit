const API_URL = "127.0.0.1:8000";

export async function getRoomMap(ids: number[], grid_resolution: number): Promise<string> {
  var query = `http://${API_URL}/api/map?gres=${grid_resolution}&`
  for (var i = 0; i < ids.length; i++) {
    query = query.concat(`poid=${ids[i]}&`)
  }

  query = query.substring(0, query.length - 1);

  const res = await fetch(query);
  const blob = await res.blob();
  const src = URL.createObjectURL(blob);

  return src;
}

export async function getRouterCoverage(ids: number[], grid_resolution: number, maxPathLoss: number): Promise<string> {
  var query = `http://${API_URL}/api/solve?gres=${grid_resolution}&maxloss=${maxPathLoss}&`
  for (var i = 0; i < ids.length; i++) {
    query = query.concat(`poid=${ids[i]}&`)
  }

  query = query.substring(0, query.length - 1);

  const res = await fetch(query);
  const blob = await res.blob();
  const src = URL.createObjectURL(blob);

  return src;
}
