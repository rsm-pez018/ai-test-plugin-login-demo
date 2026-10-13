import { Button, Card, Result } from "antd";
import { Link } from "react-router-dom";

function Success() {
    return (
        <div className="auth-page">
            <Card className="auth-card success-card">
                <Result
                    status="success"
                    title="Login Successful"
                    subTitle="Welcome to AI Testing Agent Demo"
                    extra={[
                        <Link to="/login" key="login">
                            <Button type="primary">Back to Login</Button>
                        </Link>,
                    ]}
                />
            </Card>
        </div>
    );
}


export default Success;
