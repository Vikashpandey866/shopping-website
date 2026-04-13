async function doLogin() {
    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPass").value;

    const data = await apiRequest("/auth/login", "POST", {
        email,
        password
    });

    console.log(data);

    if (data.token) {
        localStorage.setItem("token", data.token);
        alert("Login successful 🔥");
    } else {
        alert(data.error || "Login failed");
    }
}

async function doRegister() {
    const name = document.getElementById("regName").value;
    const email = document.getElementById("regEmail").value;
    const password = document.getElementById("regPass").value;

    const data = await apiRequest("/auth/register", "POST", {
        name,
        email,
        password
    });

    console.log(data);

    if (data.token) {
        alert("Account created 🔥");
    } else {
        alert(data.error || "Register failed");
    }
}
