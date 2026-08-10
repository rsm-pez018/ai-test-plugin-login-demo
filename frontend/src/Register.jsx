import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function Register() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate();

    const handleRegister = async () => {
        try {
            const response = await axios.post(
                "http://127.0.0.1:5000/api/register",
                {
                    username,
                    password,
                }
            );

            alert(response.data.message);
            navigate("/login");
        } catch (error) {
            alert(error.response?.data?.message || "Registration failed");
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-card">
                <h1>Register</h1>

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

                <button onClick={handleRegister}>Register</button>

                <p>
                    Already have an account? <a href="/login">Login</a>
                </p>
            </div>
        </div>
    );
}

export default Register;
