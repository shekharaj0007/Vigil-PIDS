import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function RiskTrendChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(19,33,43,0.08)" />
        <XAxis dataKey="id" tick={{ fontSize: 11 }} />
        <YAxis domain={[0, 1]} tick={{ fontSize: 11 }} />
        <Tooltip />
        <Line
          type="monotone"
          dataKey="risk_score"
          stroke="#0f766e"
          strokeWidth={2.5}
          dot={{ r: 3 }}
          name="Risk"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
