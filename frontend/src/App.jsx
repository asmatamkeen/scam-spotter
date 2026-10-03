import { useState } from "react";

const COLORS = { SAFE: "#16a34a", SUSPICIOUS: "#d97706", SCAM: "#dc2626" };

export default function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function handleFile(e) {
    const f = e.target.files[0];
    if (!f) return;
    setFile(f);
    setResult(null);
    setError("");
    setPreview(f.type.startsWith("image/") ? URL.createObjectURL(f) : null);
  }

  async function check() {
    setLoading(true);
    setResult(null);
    setError("");
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch("http://localhost:8000/check", { method: "POST", body: form });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setResult(data);
    } catch (err) {
      setError("Couldn't check this one. Try again or use another file.");
    }
    setLoading(false);
  }

  return (
    <div style={{ maxWidth: 560, margin: "40px auto", fontFamily: "sans-serif", padding: 16 }}>
      <h1>🛡️ Scam Spotter</h1>
      <p>Got a suspicious offer? Upload a screenshot or offer letter PDF.</p>
      <input type="file" accept="image/*,application/pdf" onChange={handleFile} />
      {file && !preview && <p>📄 {file.name}</p>}
      {preview && <img src={preview} alt="upload" style={{ width: "100%", marginTop: 16, borderRadius: 8 }} />}
      <button onClick={check} disabled={!file || loading} style={{ marginTop: 16, padding: "10px 20px", fontSize: 16 }}>
        {loading ? "Checking..." : "Check it"}
      </button>

      {error && <p style={{ color: "#dc2626" }}>{error}</p>}

      {result && (
        <div style={{ marginTop: 20, border: `3px solid ${COLORS[result.verdict]}`, borderRadius: 12, padding: 16 }}>
          <h2 style={{ color: COLORS[result.verdict], margin: 0 }}>{result.verdict}</h2>
          <p>{result.summary}</p>
          {result.red_flags.length > 0 && <strong>Red flags:</strong>}
          {result.red_flags.map((f, i) => (
            <div key={i} style={{ background: "#fee2e2", padding: 10, borderRadius: 8, margin: "8px 0" }}>
              <strong>{f.flag}</strong>
              <div style={{ fontStyle: "italic" }}>"{f.quote}"</div>
            </div>
          ))}
          <strong>What to do:</strong>
          <p>{result.what_to_do}</p>
        </div>
      )}
    </div>
  );
}