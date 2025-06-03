export const fetchAlerts = async () => {
  try {
    const response = await fetch("http://localhost:8000/alerts/");
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error:", error);
    return [];
  }
};

export const createAlert = async (alertData) => {
  try {
    const response = await fetch("http://localhost:8000/alerts/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(alertData),
    });
    return response.json();
  } catch (error) {
    console.error("Error:", error);
    return {};
  }
};
