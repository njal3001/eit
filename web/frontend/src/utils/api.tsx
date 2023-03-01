import sleep from "./sleep";

export async function getRouterMap(urls: string[]): Promise<JSX.Element> {
  await sleep(2000);
  return <div>
    <p style={{ color: "white" }}>hallo</p>
  </div>
}
