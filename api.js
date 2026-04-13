const API_BASE = "https://shopping-website-production-2c24.up.railway.app/api";

async function apiRequest(endpoint, method = "GET", body = null, token = null) {
    const options = {
        method: method,
        headers: {
            "Content-Type": "application/json"
        }
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    if (token) {
        options.headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(API_BASE + endpoint, options);
    return res.json();
}
