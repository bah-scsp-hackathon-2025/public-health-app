export const fetchAlerts = async () => {
  try {
    const response = await fetch("http://localhost:8000/alerts/");
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error getting alerts:", error);
    return [];
  }
};

export const fetchAlert = async (alert_id) => {
  try {
    const response = await fetch(`http://localhost:8000/alerts/${alert_id}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error getting alert:", error);
    return {};
  }
};

export const fetchAlertByLocation = async (location) => {
  try {
    // Updating spaces to be underscores
    const response = await fetch(`http://localhost:8000/alerts/${location.replace(" ", "_")}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error getting alert:", error);
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
    console.error("Error creating alert:", error);
    return {};
  }
};

export const fetchStrategiesByAlert = async (alert_id) => {
  try {
    const response = await fetch(
      `http://localhost:8000/strategies/alert/${alert_id}`
    );
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error getting strategies:", error);
    return [];
  }
};

export const generateStrategiesByAlert = async (alert_id) => {
  try {
    const response = await fetch(
      `http://localhost:8000/strategies/generate/${alert_id}`
    );
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error generating strategies:", error);
    return [];
  }
};

export const generatePolicyFromStrategy = async (strategy_id) => {
  try {
    const response = await fetch(
      `http://localhost:8000/policies/generate/${strategy_id}`
    );
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error generating policy:", error);
    return {};
  }
};

export const fetchApprovedPolicies = async () => {
  try {
    const response = await fetch(`http://localhost:8000/policies/approved/`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error getting approved policies:", error);
    return [];
  }
};

export const fetchDraftPolicies = async () => {
  try {
    const response = await fetch(`http://localhost:8000/policies/draft/`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error getting draft policies:", error);
    return [];
  }
};

export const fetchApprovedPoliciesByAlert = async (alert_id) => {
  try {
    const response = await fetch(`http://localhost:8000/policies/approved/${alert_id}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error getting approved policies:", error);
    return [];
  }
};

export const fetchPoliciesByAlert = async (alert_id) => {
  try {
    const response = await fetch(`http://localhost:8000/policies/${alert_id}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error getting approved policies:", error);
    return [];
  }
};

export const updatePolicy = async (policy_id, policyData) => {
  try {
    const response = await fetch(`http://localhost:8000/policies/${policy_id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(policyData),
    });
    return response.json();
  } catch (error) {
    console.error("Error updating policy:", error);
    return {};
  }
};

export const fetchSummary = async () => {
  try {
    const response = await fetch(`http://localhost:8000/summary/`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error getting summary:", error);
    return [];
  }
};

export const fetchTrends= async () => {
  try {
    const response = await fetch(`http://localhost:8000/trends/`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error getting trends:", error);
    return [];
  }
};