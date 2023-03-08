import "./UrlOverview.css";

interface UrlOverviewProps {
  URLs: string[];
  emptyURLs: () => void;
}

function UrlOverview(props: UrlOverviewProps) {
  const { URLs, emptyURLs } = props;

  function renderURLs() {
    return URLs.map((url) => {
      return <p className="url">{url}</p>
    });
  }

  return <div className="urloverview-container">
    <p style={{
      color: "rgba(255, 255, 255, 0.9)",
      borderBottom: "1px solid rgba(255, 255, 255, 0.3)",
      padding: "0.25rem 0.5rem"
    }}>
      URLs
    </p>
    <div>
      {renderURLs() ?? <p>hallo</p>}
    </div>
    <button className="api-button" onClick={emptyURLs}>Tøm URLer</button>
  </div>;
}

export default UrlOverview;