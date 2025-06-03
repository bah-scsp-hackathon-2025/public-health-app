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

export const fetchAlert = async (alert_id) => {
  try {
    const response = await fetch(`http://localhost:8000/alerts/${alert_id}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error:", error);
    return {};
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

export const fetchStrategiesByAlert = async (alert_id) => {
  try {
    const response = await fetch(
      `http://localhost:8000/policies/strategies/alert/${alert_id}`
    );
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error:", error);
    return [];
  }
};

export const generateStrategiesByAlert = async (alert_id) => {
  try {
    const response = await fetch(
      `http://localhost:8000/policies/generate/${alert_id}`
    );
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error:", error);
    return [];
  }
};

export const generatePolicyFromStrategy = async (strategy_id) => {
  try {
    const response = await fetch(
      `http://localhost:8000/policies/draft/${strategy_id}`
    );
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error:", error);
    return {};
  }
};

export const fetchApprovedPolicies = async () => {
  try {
    const response = await fetch(`http://localhost:8000/policies/approved/`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error:", error);
    return [];
  }
};

export const fetchDraftPolicies = async () => {
  try {
    const response = await fetch(`http://localhost:8000/policies/draft/`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error:", error);
    return [];
  }
};

export const fetchSummary = async () => {
  try {
    const response = await fetch(`http://localhost:8000/summary/`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error:", error);
    return [];
  }
};
