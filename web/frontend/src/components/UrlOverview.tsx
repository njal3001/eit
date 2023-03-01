import "./UrlOverview.css";

interface UrlOverviewProps {
  URLs: string[];
}

function UrlOverview(props: UrlOverviewProps) {
  const { URLs } = props;

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
  </div>;
}

export default UrlOverview;