import { Link, useNavigate } from "react-router-dom";
import { Button, Card, Form, Input, Typography } from "antd";
import axios from "axios";

const { Text } = Typography;

function Login() {
    const navigate = useNavigate();

    const handleLogin = async (values) => {
        try {
            const response = await axios.post(
                "http://127.0.0.1:5000/api/login",
                values
            );

            if (response.data.message === "Login successful") {
                navigate("/success");
            }
        } catch (error) {
            alert(error.response?.data?.message || "Login failed");
        }
    };

    return (
        <div className="auth-page">
            <Card className="auth-card">
                <h1>Login</h1>

                <Form layout="vertical" onFinish={handleLogin}>
                    <Form.Item
                        label="Username"
                        name="username"
                        rules={[{ required: true, message: "Please enter username" }]}
                    >
                        <Input placeholder="Username" />
                    </Form.Item>

                    <Form.Item
                        label="Password"
                        name="password"
                        rules={[{ required: true, message: "Please enter password" }]}
                    >
                        <Input.Password placeholder="Password" />
                    </Form.Item>

                    <Button type="primary" htmlType="submit" block>
                        Login
                    </Button>
                </Form>

                <p className="auth-footer">
                    <Text type="secondary">No account yet? </Text>
                    <Link to="/register">Register</Link>
                </p>
            </Card>
        </div>
    );
}


export default Login;
