function login() {

    const username =
        document.getElementById("username").value;

    const password =
        document.getElementById("password").value;

    if (
        username === "admin" &&
        password === "xxxxxxxxxx"
    ) {

        localStorage.setItem(
            "authenticated",
            "true"
        );

        window.location.href = "index.html";

    } else {

        document.getElementById("error").innerHTML =
            "Invalid Username or Password";
    }
}
