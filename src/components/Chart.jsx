import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

function Chart({ data }) {
  
  return (
    <div style={{ width: "100%", height: 300 }}>
      <ResponsiveContainer>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
        dataKey="time" 
        tickFormatter={(time) => {
          const date = new Date(time);
          return date.toLocaleDateString(); // formats as MM/DD/YYYY or locale format
        }} 
      />
          <YAxis />
          <Tooltip 
        labelFormatter={(label) => {
          const date = new Date(label);
          return date.toLocaleDateString(undefined, {
            year: "numeric",
            month: "short",
            day: "numeric"
          });
        }}
        formatter={(value, name) => [`${value}`, name]} // optional: format the value label
      />
          <Legend />
          <Line type="monotone" dataKey="value" stroke="#8884d8" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default Chart;
