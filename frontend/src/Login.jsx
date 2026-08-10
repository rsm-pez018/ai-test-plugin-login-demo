import { useState } from "react";
import axios from "axios";


function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const handleLogin = async () => {
        try {
            const response = await axios.post(
                "http://127.0.0.1:5000/api/login",
                {
                    username,
                    password,
                }
            );

            if (response.data.message === "Login successful") {
                window.location.href = "/success";
            }
        } catch (error) {
            alert(error.response?.data?.message || "Login failed");
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-card">
                <h1>Login</h1>

                <input
                    placeholder="Username"
                    value={username}
                    onChange={(event) => setUsername(event.target.value)}
                />

                <input
                    placeholder="Password"
                    type="password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                />

                <button onClick={handleLogin}>Login</button>

                <p>
                    No account yet? <a href="/register">Register</a>
                </p>
            </div>
        </div>
    );
}


export default Login;
