const API_BASE_URL = "http://localhost:8000";

function getAuthHeaders() {
  const token = localStorage.getItem("access_token");

  return token
    ? {
        Authorization: `Bearer ${token}`,
      }
    : {};
}

export async function searchForms(query) {
  const response = await fetch(
    `${API_BASE_URL}/api/forms/search?q=${encodeURIComponent(query)}`
  );

  if (!response.ok) {
    throw new Error("Failed to search forms");
  }

  return response.json();
}

export async function createSession(formId) {
  const response = await fetch(
    `${API_BASE_URL}/api/sessions/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(),
      },
      body: JSON.stringify({
        form_id: formId,
      }),
    }
  );

  if (response.status === 401) {
    throw new Error("LOGIN_REQUIRED");
  }

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));

    throw new Error(
      data.detail || "Failed to create session"
    );
  }

  return response.json();
}

export async function getSession(sessionId) {
  const response = await fetch(
    `${API_BASE_URL}/api/sessions/${sessionId}`,
    {
      headers: {
        ...getAuthHeaders(),
      },
    }
  );

  if (response.status === 401) {
    throw new Error("LOGIN_REQUIRED");
  }

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));

    throw new Error(
      data.detail || "Failed to get session"
    );
  }

  return response.json();
}

export async function submitAnswer(sessionId, fieldId, value) {
  const response = await fetch(
    `${API_BASE_URL}/api/sessions/${sessionId}/answers`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(),
      },
      body: JSON.stringify({
        field_id: fieldId,
        value: value,
      }),
    }
  );

  if (response.status === 401) {
    throw new Error("LOGIN_REQUIRED");
  }

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));

    throw new Error(
      data.detail || "Failed to submit answer"
    );
  }

  return response.json();
}