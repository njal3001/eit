import "./SearchField.css";
import { useState } from "react";
import sleep from "../utils/sleep";

interface SearchFieldProps {
  addURL: (url: string) => void;
}

function SearchField(props: SearchFieldProps) {
  const { addURL } = props;
  const [text, setText] = useState<string>();

  return <div className="searchfield-form">
    <form onSubmit={async (e) => {
      e.preventDefault();
      console.log("submitted");
      if (text !== undefined) {
        addURL(text);
        for (let i = text.length; i >= 0; i--) {
          setText(() => text.substring(0, i));
          await sleep(15);
        }
      } 
    }}>
      <div className="container searchfield-container">
        <MagnifyingGlass />
        <input id="searchfield" type="text" value={text} onChange={(e) => {
          setText(e.target.value);
        }} placeholder="Mazemap-URL" />
      </div>
    </form>
  </div>;
}

function MagnifyingGlass() {
  return <svg width="24" height="24" fill="none" id="magnifying-glass" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
    <path d="M11.5 21.75c-5.65 0-10.25-4.6-10.25-10.25S5.85 1.25 11.5 1.25s10.25 4.6 10.25 10.25-4.6 10.25-10.25 10.25Zm0-19c-4.83 0-8.75 3.93-8.75 8.75s3.92 8.75 8.75 8.75 8.75-3.93 8.75-8.75-3.92-8.75-8.75-8.75ZM22 22.75c-.19 0-.38-.07-.53-.22l-2-2a.754.754 0 0 1 0-1.06c.29-.29.77-.29 1.06 0l2 2c.29.29.29.77 0 1.06-.15.15-.34.22-.53.22Z" fill="currentColor" />
  </svg>
}

export default SearchField;