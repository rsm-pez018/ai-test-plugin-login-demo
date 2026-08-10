import { Link, useNavigate } from "react-router-dom";
import { Button, Card, Form, Input, Typography } from "antd";
import axios from "axios";

const { Text } = Typography;

function Register() {
    const navigate = useNavigate();

    const handleRegister = async (values) => {
        try {
            const response = await axios.post(
                "http://127.0.0.1:5000/api/register",
                values
            );

            alert(response.data.message);
            navigate("/login");
        } catch (error) {
            alert(error.response?.data?.message || "Registration failed");
        }
    };

    return (
        <div className="auth-page">
            <Card className="auth-card">
                <h1>Register</h1>

                <Form layout="vertical" onFinish={handleRegister}>
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
                        rules={[
                            { required: true, message: "Please enter password" },
                            { min: 6, message: "Password must be at least 6 characters" },
                        ]}
                    >
                        <Input.Password placeholder="Password" />
                    </Form.Item>

                    <Button type="primary" htmlType="submit" block>
                        Register
                    </Button>
                </Form>

                <p className="auth-footer">
                    <Text type="secondary">Already have an account? </Text>
                    <Link to="/login">Login</Link>
                </p>
            </Card>
        </div>
    );
}

export default Register;
