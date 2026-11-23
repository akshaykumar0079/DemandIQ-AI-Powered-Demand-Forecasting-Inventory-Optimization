import { useMemo, useState } from "react";
import { Activity, Boxes, BrainCircuit, ChartNoAxesCombined, RefreshCw, TrendingUp } from "lucide-react";

const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

type ForecastResult = { method?: string; forecast?: number[]; actual?: number[]; predicted?: number[]; models?: Record<string, Record<string, number>>; recommended_model?: string };
type Recommendation = { average_daily_demand: number; safety_stock: number; reorder_point: number; suggested_order_quantity: number };

export default function App() {
  const [history, setHistory] = useState("12,14,13,9,16,18,15,13,15,14,10,17,19,16,14,16,15,11,18,20,17,15,17,16,12,19,21,18,16,18,17,13,20,22,19");
  const [horizon, setHorizon] = useState(7);
  const [onHand, setOnHand] = useState(30);
  const [leadTime, setLeadTime] = useState(5);
  const [forecast, setForecast] = useState<number[]>([]);
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [comparison, setComparison] = useState<ForecastResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const values = useMemo(() => history.split(",").map((value) => Number(value.trim())), [history]);
  const valid = values.length >= 8 && values.every((value) => Number.isFinite(value) && value >= 0);

  async function runPlanning() {
    if (!valid) {
      setError("Enter at least 8 comma-separated, non-negative daily sales values.");
      return;
    }
    setBusy(true);
    setError("");
    setRecommendation(null);
    try {
      const forecastResponse = await fetch(`${API}/forecast/ml`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ history: values, horizon }),
      });
      if (!forecastResponse.ok) throw new Error((await forecastResponse.json()).detail ?? "Forecast request failed");
      const forecastData = (await forecastResponse.json()) as ForecastResult;
      const predictions = forecastData.forecast ?? [];
      setForecast(predictions);

      const [stockResponse, comparisonResponse] = await Promise.all([
        fetch(`${API}/inventory/recommendation`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ forecast: predictions, on_hand: onHand, lead_time_days: leadTime }),
        }),
        fetch(`${API}/forecast/compare`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ history: values, horizon: Math.min(horizon, values.length - 22) }),
        }),
      ]);
      if (stockResponse.ok) setRecommendation((await stockResponse.json()) as Recommendation);
      if (comparisonResponse.ok) setComparison((await comparisonResponse.json()) as ForecastResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to reach DemandIQ API");
    } finally {
      setBusy(false);
    }
  }

  const maxForecast = Math.max(1, ...forecast);
  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand"><span className="brand-mark"><ChartNoAxesCombined size={21} /></span><div><strong>DemandIQ</strong><small>INTELLIGENT DEMAND PLANNING</small></div></div>
        <div className="status"><span /> Forecast workspace</div>
      </header>
      <section className="hero">
        <div><p className="eyebrow">PLANNING OVERVIEW / WORKSPACE 01</p><h1>Know what to stock.<br /><em>Before you need it.</em></h1><p className="intro">Turn historical sales into clear demand forecasts and practical replenishment decisions.</p></div>
        <div className="hero-icon"><BrainCircuit size={76} strokeWidth={1.1} /></div>
      </section>
      <section className="grid">
        <article className="panel input-panel">
          <div className="panel-heading"><div><p className="eyebrow">01 / INPUT DATA</p><h2>Sales history</h2></div><Boxes size={22} /></div>
          <label htmlFor="history">Daily units sold <span>comma-separated</span></label>
          <textarea id="history" value={history} onChange={(event) => setHistory(event.target.value)} rows={4} />
          <div className="field-row">
            <label>Forecast horizon <input type="number" min="1" max="30" value={horizon} onChange={(event) => setHorizon(Number(event.target.value))} /></label>
            <label>Current stock <input type="number" min="0" value={onHand} onChange={(event) => setOnHand(Number(event.target.value))} /></label>
            <label>Lead time (days) <input type="number" min="0" value={leadTime} onChange={(event) => setLeadTime(Number(event.target.value))} /></label>
          </div>
          <button className="primary" onClick={runPlanning} disabled={busy || !valid}><RefreshCw size={16} className={busy ? "spin" : ""} /> {busy ? "Analysing demand..." : "Generate planning insights"}</button>
          {error && <p className="error">{error}</p>}
          <p className="hint">Use at least 8 daily observations. For model comparison, 22+ training days plus the selected holdout are recommended.</p>
        </article>
        <article className="panel result-panel">
          <div className="panel-heading"><div><p className="eyebrow">02 / FORECAST OUTPUT</p><h2>Demand outlook</h2></div><TrendingUp size={22} /></div>
          {forecast.length ? <><div className="forecast-total">{forecast.reduce((sum, value) => sum + value, 0).toFixed(1)}<small>expected units over {forecast.length} days</small></div><div className="bars">{forecast.map((value, index) => <div className="bar-item" key={index}><div className="bar-track"><div className="bar-fill" style={{ height: `${Math.max(5, (value / maxForecast) * 100)}%` }} /></div><strong>{value.toFixed(1)}</strong><small>D{index + 1}</small></div>)}</div></> : <div className="empty"><Activity size={34} /><p>Your forecast will appear here.</p><small>Submit sales history to run the ML model.</small></div>}
        </article>
        <article className="panel">
          <div className="panel-heading"><div><p className="eyebrow">03 / INVENTORY POLICY</p><h2>Replenishment advice</h2></div><Boxes size={22} /></div>
          {recommendation ? <div className="metrics"><div><small>Suggested order</small><strong>{recommendation.suggested_order_quantity} <small>units</small></strong></div><div><small>Reorder point</small><strong>{recommendation.reorder_point}</strong></div><div><small>Safety stock</small><strong>{recommendation.safety_stock}</strong></div><div><small>Avg. daily demand</small><strong>{recommendation.average_daily_demand.toFixed(1)}</strong></div></div> : <div className="empty compact"><p>Inventory recommendation pending.</p><small>Generate a forecast to calculate your reorder point.</small></div>}
        </article>
        <article className="panel">
          <div className="panel-heading"><div><p className="eyebrow">04 / MODEL SELECTION</p><h2>Model comparison</h2></div><BrainCircuit size={22} /></div>
          {comparison?.models ? <><p className="winner">Recommended: <strong>{comparison.recommended_model?.replace("_", " ")}</strong></p><div className="model-table"><div className="model-row header"><span>Model</span><span>MAE</span><span>RMSE</span><span>sMAPE</span></div>{Object.entries(comparison.models).map(([name, metrics]) => <div className="model-row" key={name}><span>{name.replace("_", " ")}</span><span>{metrics.mae.toFixed(2)}</span><span>{metrics.rmse.toFixed(2)}</span><span>{metrics.smape.toFixed(1)}%</span></div>)}</div></> : <div className="empty compact"><p>Model metrics not available yet.</p><small>Comparison requires enough historical observations.</small></div>}
        </article>
      </section>
      <footer><span>DemandIQ · Forecasting is an estimate, not a guarantee.</span><span><Activity size={13} /> Built for data-informed decisions</span></footer>
    </main>
  );
}
