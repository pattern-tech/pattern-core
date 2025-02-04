export const fetchClient = async (
  endpoint: string,
  options: RequestInit = {}
) => {
  const baseURL = import.meta.env.VITE_API_BASE_URL;
  const token = localStorage.getItem("token");

  const headers = new Headers({
    Authorization: token ? `Bearer ${token}` : "",
    "Content-Type": "application/json",
  });

  try {
    const response = await fetch(`${baseURL}${endpoint}`, {
      ...options,
      headers,
    });

    if (response.status === 403) {
      localStorage.removeItem("token");
      window.location.href = "/login";
      return;
    }

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || "Something went wrong");
    }

    return await response.json();
  } catch (error) {
    console.error("Fetch error:", error);
    throw error;
  }
};
